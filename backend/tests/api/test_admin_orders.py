import pytest

from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG
from tests.helpers import place_order

pytestmark = pytest.mark.asyncio


async def _advance_to_ready(client, kitchen_headers, order_id):
    await client.post(f"/api/v1/kitchen/orders/{order_id}/accept", headers=kitchen_headers)
    await client.post(f"/api/v1/kitchen/orders/{order_id}/start-preparing", headers=kitchen_headers)
    return await client.post(f"/api/v1/kitchen/orders/{order_id}/ready", headers=kitchen_headers)


async def test_non_admin_cannot_access_admin_orders(client, customer_headers):
    resp = await client.get("/api/v1/admin/orders", headers=customer_headers)
    assert resp.status_code == 403


async def test_admin_lists_all_orders(client, admin_headers, customer_headers, seeded_zone):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    resp = await client.get("/api/v1/admin/orders", headers=admin_headers)
    assert resp.status_code == 200
    assert any(o["id"] == order["id"] for o in resp.json())

    resp = await client.get("/api/v1/admin/orders?status=pending", headers=admin_headers)
    assert resp.status_code == 200
    assert all(o["status"] == "pending" for o in resp.json())


async def test_admin_force_cancel_active_order(
    client, admin_headers, customer_headers, kitchen_headers, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    await client.post(f"/api/v1/kitchen/orders/{order['id']}/accept", headers=kitchen_headers)

    resp = await client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"reason": "kitchen closed early"},
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "cancelled"


async def test_admin_cannot_cancel_delivered_order(
    client, admin_headers, customer_headers, kitchen_headers, delivery_headers, delivery_partner, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    order_id = order["id"]
    await _advance_to_ready(client, kitchen_headers, order_id)
    await client.post(f"/api/v1/delivery/orders/{order_id}/pickup", headers=delivery_headers)
    await client.post(f"/api/v1/delivery/orders/{order_id}/on-the-way", headers=delivery_headers)
    otp = (await client.get(f"/api/v1/orders/{order_id}", headers=customer_headers)).json()["delivery_otp"]
    await client.post(f"/api/v1/delivery/orders/{order_id}/deliver", json={"otp": otp}, headers=delivery_headers)

    resp = await client.post(f"/api/v1/admin/orders/{order_id}/cancel", json={}, headers=admin_headers)
    assert resp.status_code == 409


async def test_admin_lists_users_by_role(client, admin_headers, delivery_user, kitchen_headers):
    delivery_user_obj, _ = delivery_user

    resp = await client.get("/api/v1/admin/users?role=delivery", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert any(u["id"] == str(delivery_user_obj.id) for u in body)
    assert all(u["role"] == "delivery" for u in body)


async def test_non_admin_cannot_list_users_by_role(client, kitchen_headers):
    resp = await client.get("/api/v1/admin/users?role=delivery", headers=kitchen_headers)
    assert resp.status_code == 403


async def test_create_delivery_partner_requires_delivery_role(client, admin_headers, customer_headers):
    me = (await client.get("/api/v1/auth/me", headers=customer_headers)).json()
    resp = await client.post(
        "/api/v1/admin/delivery-partners", json={"user_id": me["id"]}, headers=admin_headers
    )
    assert resp.status_code == 400


async def test_admin_manual_assign_when_no_partner_available(
    client, admin_headers, customer_headers, kitchen_headers, delivery_user, seeded_zone
):
    delivery_user_obj, _ = delivery_user
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    order_id = order["id"]

    resp = await _advance_to_ready(client, kitchen_headers, order_id)
    assert resp.json()["status"] == "ready"
    assert resp.json()["delivery_partner"] is None

    created = await client.post(
        "/api/v1/admin/delivery-partners",
        json={"user_id": str(delivery_user_obj.id), "vehicle_number": "KA-05-XY-9999"},
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    partner_id = created.json()["id"]

    resp = await client.post(
        f"/api/v1/admin/orders/{order_id}/assign",
        json={"delivery_partner_id": partner_id},
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "assigned"
    assert resp.json()["delivery_partner"]["id"] == partner_id

    partners = (await client.get("/api/v1/admin/delivery-partners", headers=admin_headers)).json()
    assert any(p["id"] == partner_id for p in partners)
