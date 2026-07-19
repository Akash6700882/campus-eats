"""Idempotent seed script: default admin, campus roles, sample menu, placeholder geofence.

Run inside the backend container/venv:
    python -m scripts.seed
"""

import asyncio
import json
import uuid

from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import AsyncSessionLocal
from app.core.security import hash_password
from app.models import Category, DeliveryZone, Food, Role, User
from app.models.enums import RoleName

settings = get_settings()

ROLE_NAMES = [RoleName.CUSTOMER, RoleName.ADMIN, RoleName.KITCHEN, RoleName.DELIVERY]

CATEGORIES = [
    ("Breakfast", "breakfast"),
    ("South Indian", "south-indian"),
    ("Lunch", "lunch"),
    ("Dinner", "dinner"),
    ("Snacks", "snacks"),
    ("Juices & Beverages", "juices-beverages"),
    ("Desserts", "desserts"),
]

# (name, category_slug, price, is_veg, prep_time, description, popular, special_today)
FOODS = [
    ("Idli", "south-indian", 40, True, 10, "Steamed rice cakes served with sambar and chutney.", True, False),
    ("Plain Dosa", "south-indian", 50, True, 12, "Classic crispy rice-and-lentil crepe.", True, False),
    ("Masala Dosa", "south-indian", 70, True, 14, "Dosa filled with spiced potato masala.", True, True),
    ("Onion Dosa", "south-indian", 65, True, 14, "Dosa topped with crispy onions.", False, False),
    ("Poori", "breakfast", 50, True, 10, "Deep-fried puffed bread with curry.", False, False),
    ("Vada", "south-indian", 35, True, 8, "Crispy fried lentil doughnuts.", False, False),
    ("Pongal", "breakfast", 45, True, 12, "Savory rice and lentil porridge with pepper and ghee.", False, False),
    ("Uttapam", "south-indian", 60, True, 13, "Thick savory pancake topped with vegetables.", False, False),
    ("Meals (Veg)", "lunch", 90, True, 20, "Full South Indian thali with rice, sambar, rasam, curries.", True, False),
    ("Curd Rice", "lunch", 45, True, 8, "Comfort rice tempered curd rice.", False, False),
    ("Lemon Rice", "lunch", 50, True, 10, "Tangy tempered lemon rice.", False, False),
    ("Fried Rice", "dinner", 70, True, 15, "Wok-tossed vegetable fried rice.", False, False),
    ("Noodles", "dinner", 70, True, 15, "Stir-fried veg noodles.", False, False),
    ("Tea", "juices-beverages", 15, True, 5, "Classic Indian masala chai.", True, False),
    ("Coffee", "juices-beverages", 20, True, 5, "South Indian filter coffee.", True, False),
    ("Badam Milk", "juices-beverages", 40, True, 5, "Chilled almond-flavoured milk.", False, False),
    ("Fresh Lime", "juices-beverages", 30, True, 5, "Fresh lime soda, sweet or salted.", False, False),
    ("Fruit Juice (Mixed)", "juices-beverages", 45, True, 5, "Seasonal mixed fruit juice.", False, True),
    ("Mango Milkshake", "juices-beverages", 55, True, 5, "Thick mango milkshake.", True, False),
    ("Lassi", "juices-beverages", 40, True, 5, "Sweet churned yogurt drink.", False, False),
    ("Ice Cream", "desserts", 35, True, 3, "Two scoops, ask for today's flavours.", False, False),
]

# Placeholder campus geofence — approx a 3.2km half-width square (~10,000 acres)
# around a generic sample coordinate. Replace with the real campus GIS
# boundary in the admin delivery-zone editor (Phase 7) once available.
CAMPUS_CENTER = (12.9716, 77.5946)
_HALF_WIDTH_DEG = 0.029


def _placeholder_campus_polygon() -> str:
    lat, lng = CAMPUS_CENTER
    coords = [
        [lng - _HALF_WIDTH_DEG, lat - _HALF_WIDTH_DEG],
        [lng + _HALF_WIDTH_DEG, lat - _HALF_WIDTH_DEG],
        [lng + _HALF_WIDTH_DEG, lat + _HALF_WIDTH_DEG],
        [lng - _HALF_WIDTH_DEG, lat + _HALF_WIDTH_DEG],
        [lng - _HALF_WIDTH_DEG, lat - _HALF_WIDTH_DEG],
    ]
    return json.dumps({"type": "Polygon", "coordinates": [coords]})


def _slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("(", "").replace(")", "")


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        # Roles
        roles_by_name: dict[str, Role] = {}
        for role_name in ROLE_NAMES:
            result = await session.execute(select(Role).where(Role.name == role_name.value))
            role = result.scalar_one_or_none()
            if role is None:
                role = Role(id=uuid.uuid4(), name=role_name.value)
                session.add(role)
                await session.flush()
                print(f"Created role: {role_name.value}")
            roles_by_name[role_name.value] = role

        # Default admin
        result = await session.execute(select(User).where(User.email == settings.default_admin_email))
        admin = result.scalar_one_or_none()
        if admin is None:
            admin = User(
                id=uuid.uuid4(),
                full_name="Campus Eats Admin",
                email=settings.default_admin_email,
                phone=settings.default_admin_phone,
                hashed_password=hash_password(settings.default_admin_password),
                role_id=roles_by_name[RoleName.ADMIN.value].id,
                is_active=True,
                is_verified=True,
            )
            session.add(admin)
            await session.flush()
            print(f"Created default admin: {settings.default_admin_email}")
        else:
            print("Default admin already exists, skipping")

        # Categories
        categories_by_slug: dict[str, Category] = {}
        for sort_order, (name, slug) in enumerate(CATEGORIES):
            result = await session.execute(select(Category).where(Category.slug == slug))
            category = result.scalar_one_or_none()
            if category is None:
                category = Category(id=uuid.uuid4(), name=name, slug=slug, sort_order=sort_order)
                session.add(category)
                await session.flush()
                print(f"Created category: {name}")
            categories_by_slug[slug] = category

        # Foods
        created_foods = 0
        for name, cat_slug, price, is_veg, prep_time, desc, popular, special in FOODS:
            slug = _slugify(name)
            result = await session.execute(select(Food).where(Food.slug == slug))
            existing = result.scalar_one_or_none()
            if existing is not None:
                continue
            food = Food(
                id=uuid.uuid4(),
                category_id=categories_by_slug[cat_slug].id,
                name=name,
                slug=slug,
                description=desc,
                price=price,
                is_veg=is_veg,
                prep_time_minutes=prep_time,
                is_available=True,
                is_popular=popular,
                is_special_today=special,
            )
            session.add(food)
            created_foods += 1
        if created_foods:
            print(f"Created {created_foods} food items")

        # Placeholder campus delivery zone
        result = await session.execute(select(DeliveryZone).where(DeliveryZone.name == "Main Campus (placeholder)"))
        zone = result.scalar_one_or_none()
        if zone is None:
            zone = DeliveryZone(
                id=uuid.uuid4(),
                name="Main Campus (placeholder)",
                polygon_geojson=_placeholder_campus_polygon(),
                is_active=True,
            )
            session.add(zone)
            print("Created placeholder campus delivery zone")

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
