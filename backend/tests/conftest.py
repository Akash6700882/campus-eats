import json
import uuid

import asyncpg
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.models  # noqa: F401 — registers all models on Base.metadata
from app.core.config import get_settings
from app.core.db import Base, get_db
from app.core.redis_client import get_redis
from app.core.security import hash_password
from app.main import app
from app.models.delivery import DeliveryPartner, DeliveryZone
from app.models.role import Role
from app.models.user import User
from sqlalchemy import select

# Test campus geofence: a simple square, lng in [77.59, 77.60], lat in [12.97, 12.98]
IN_CAMPUS_LAT, IN_CAMPUS_LNG = 12.975, 77.595
OUT_OF_CAMPUS_LAT, OUT_OF_CAMPUS_LNG = 13.5, 78.5
TEST_ZONE_POLYGON = json.dumps(
    {
        "type": "Polygon",
        "coordinates": [[[77.59, 12.97], [77.60, 12.97], [77.60, 12.98], [77.59, 12.98], [77.59, 12.97]]],
    }
)

settings = get_settings()

_base_url, _, _db_name = settings.database_url.rpartition("/")
TEST_DB_NAME = f"{_db_name}_test"
TEST_DATABASE_URL = f"{_base_url}/{TEST_DB_NAME}"

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=test_engine, expire_on_commit=False)


async def _ensure_test_database_exists() -> None:
    admin_url = settings.database_url_sync.replace("+psycopg2", "").rsplit("/", 1)[0] + "/postgres"
    conn = await asyncpg.connect(admin_url)
    try:
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB_NAME)
        if not exists:
            await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
    finally:
        await conn.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    await _ensure_test_database_exists()
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _seed_roles():
    async with TestSessionLocal() as session:
        for name in ("customer", "admin", "kitchen", "delivery"):
            session.add(Role(id=uuid.uuid4(), name=name))
        await session.commit()
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture(autouse=True)
async def _reset_redis_client():
    """`get_redis()` is an `lru_cache` singleton — correct for the running app
    (one event loop for its whole lifetime), but pytest-asyncio gives each
    test its own event loop, so a connection opened in one test breaks the
    next. Flush (OTP codes + slowapi rate-limit counters share this Redis),
    close, and evict the cached client after every test."""
    yield
    redis = get_redis()
    await redis.flushdb()
    await redis.aclose()
    get_redis.cache_clear()


@pytest_asyncio.fixture
async def db_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_headers(client, db_session) -> dict[str, str]:
    result = await db_session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one()

    admin = User(
        id=uuid.uuid4(),
        full_name="Test Admin",
        email="test-admin@campuseats.com",
        phone="9000000000",
        hashed_password=hash_password("AdminPass1"),
        role_id=admin_role.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(admin)
    await db_session.commit()

    resp = await client.post(
        "/api/v1/auth/login", json={"email": admin.email, "password": "AdminPass1"}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def customer_headers(client) -> dict[str, str]:
    resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "Test Customer",
            "email": "test-customer@campuseats.com",
            "phone": "9222222222",
            "password": "CustomerPass1",
        },
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _create_staff_user(
    db_session, client, role_name: str, email: str, phone: str, full_name: str
) -> tuple[User, dict[str, str]]:
    password = "StaffPass1"
    result = await db_session.execute(select(Role).where(Role.name == role_name))
    role = result.scalar_one()

    user = User(
        id=uuid.uuid4(),
        full_name=full_name,
        email=email,
        phone=phone,
        hashed_password=hash_password(password),
        role_id=role.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    await db_session.commit()

    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    token = resp.json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def kitchen_user(client, db_session) -> tuple[User, dict[str, str]]:
    return await _create_staff_user(
        db_session, client, "kitchen", "test-kitchen@campuseats.com", "9333333333", "Test Kitchen"
    )


@pytest_asyncio.fixture
async def kitchen_headers(kitchen_user) -> dict[str, str]:
    return kitchen_user[1]


@pytest_asyncio.fixture
async def delivery_user(client, db_session) -> tuple[User, dict[str, str]]:
    return await _create_staff_user(
        db_session, client, "delivery", "test-delivery@campuseats.com", "9444444444", "Test Delivery"
    )


@pytest_asyncio.fixture
async def delivery_headers(delivery_user) -> dict[str, str]:
    return delivery_user[1]


@pytest_asyncio.fixture
async def delivery_partner(delivery_user, db_session) -> DeliveryPartner:
    """A delivery-role user with an already-created DeliveryPartner profile,
    available and positioned inside the test campus zone — ready to receive
    auto-assigned orders."""
    user, _ = delivery_user
    partner = DeliveryPartner(
        id=uuid.uuid4(),
        user_id=user.id,
        vehicle_number="KA-01-AB-1234",
        is_available=True,
        current_latitude=IN_CAMPUS_LAT,
        current_longitude=IN_CAMPUS_LNG,
    )
    db_session.add(partner)
    await db_session.commit()
    return partner


@pytest_asyncio.fixture
async def seeded_zone(db_session) -> DeliveryZone:
    zone = DeliveryZone(id=uuid.uuid4(), name="Test Campus", polygon_geojson=TEST_ZONE_POLYGON, is_active=True)
    db_session.add(zone)
    await db_session.commit()
    return zone
