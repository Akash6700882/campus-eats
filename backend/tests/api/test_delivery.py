import uuid

import pytest

from app.core.security import hash_password
from app.models.delivery import DeliveryPartner
from app.models.role import Role
from app.models.user import User
from sqlalchemy import select

from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG
from tests.helpers import place_order

pytestmark = pytest.mark.asyncio


async def _advance_to_ready(client, admin_headers, customer_headers, kitchen_headers, order_id):
    await client.post(f"/api/v1/kitchen/orders/{order_id}/accept", headers=kitchen_headers)
    await client.post(f"/api/v1/kitchen/orders/{order_id}/start-preparing", headers=kitchen_headers)
    return await client.post(f"/api/v1/kitchen/orders/{order_id}/ready", headers=kitchen_headers)


async def _order_otp(client, customer_headers, order_id) -> str:
    resp = await client.get(f"/api/v1/orders/{order_id}", headers=customer_headers)
    return resp.json()["delivery_otp"]


async def test_kitchen_cannot_access_delivery_orders(client, kitchen_headers):
    resp = await client.get("/api/v1/delivery/orders", headers=kitchen_headers)
    assert resp.status_code == 403


async def test_delivery_profile_required_for_me(client, delivery_headers):
    resp = await client.get("/api/v1/delivery/me", headers=delivery_headers)
    assert resp.status_code == 404


async def test_delivery_full_flow(
    client, admin_headers, customer_headers, kitchen_headers, delivery_headers, delivery_partner, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    order_id = order["id"]
    resp = await _advance_to_ready(client, admin_headers, customer_headers, kitchen_headers, order_id)
    assert resp.json()["status"] == "assigned"

    listed = (await client.get("/api/v1/delivery/orders", headers=delivery_headers)).json()
    assert any(o["id"] == order_id for o in listed)

    resp = await client.post(f"/api/v1/delivery/orders/{order_id}/pickup", headers=delivery_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "picked_up"

    resp = await client.post(f"/api/v1/delivery/orders/{order_id}/on-the-way", headers=delivery_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "on_the_way"

    otp = await _order_otp(client, customer_headers, order_id)
    assert otp and len(otp) == 6

    resp = await client.post(
        f"/api/v1/delivery/orders/{order_id}/deliver", json={"otp": otp}, headers=delivery_headers
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "delivered"

    profile = (await client.get("/api/v1/delivery/me", headers=delivery_headers)).json()
    assert profile["total_deliveries"] == 1
    assert profile["today_earnings"] == order["delivery_charge"]
    assert profile["is_available"] is True


async def test_deliver_with_wrong_otp_rejected(
    client, admin_headers, customer_headers, kitchen_headers, delivery_headers, delivery_partner, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    order_id = order["id"]
    await _advance_to_ready(client, admin_headers, customer_headers, kitchen_headers, order_id)
    await client.post(f"/api/v1/delivery/orders/{order_id}/pickup", headers=delivery_headers)
    await client.post(f"/api/v1/delivery/orders/{order_id}/on-the-way", headers=delivery_headers)

    resp = await client.post(
        f"/api/v1/delivery/orders/{order_id}/deliver", json={"otp": "000000"}, headers=delivery_headers
    )
    assert resp.status_code == 409


async def test_unassigned_partner_cannot_pick_up_someone_elses_order(
    client, db_session, admin_headers, customer_headers, kitchen_headers, delivery_partner, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    order_id = order["id"]
    await _advance_to_ready(client, admin_headers, customer_headers, kitchen_headers, order_id)

    result = await db_session.execute(select(Role).where(Role.name == "delivery"))
    role = result.scalar_one()
    other_user = User(
        id=uuid.uuid4(),
        full_name="Other Delivery",
        email="other-delivery@campuseats.com",
        phone="9555555555",
        hashed_password=hash_password("OtherPass1"),
        role_id=role.id,
        is_active=True,
        is_verified=True,
    )
    db_session.add(other_user)
    await db_session.flush()
    other_partner = DeliveryPartner(
        id=uuid.uuid4(),
        user_id=other_user.id,
        is_available=True,
        current_latitude=IN_CAMPUS_LAT,
        current_longitude=IN_CAMPUS_LNG,
    )
    db_session.add(other_partner)
    await db_session.commit()

    login = await client.post(
        "/api/v1/auth/login", json={"email": other_user.email, "password": "OtherPass1"}
    )
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    resp = await client.post(f"/api/v1/delivery/orders/{order_id}/pickup", headers=other_headers)
    assert resp.status_code == 409


async def test_update_my_location_and_availability(client, delivery_headers, delivery_partner):
    resp = await client.patch(
        "/api/v1/delivery/me/location",
        json={"latitude": 12.9, "longitude": 77.6, "is_available": False},
        headers=delivery_headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["current_latitude"] == 12.9
    assert body["is_available"] is False
