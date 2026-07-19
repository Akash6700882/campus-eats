import pytest

from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG
from tests.helpers import place_order

pytestmark = pytest.mark.asyncio


async def test_customer_cannot_access_kitchen_orders(client, customer_headers):
    resp = await client.get("/api/v1/kitchen/orders", headers=customer_headers)
    assert resp.status_code == 403


async def test_kitchen_lists_active_orders(client, admin_headers, customer_headers, kitchen_headers, seeded_zone):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)

    resp = await client.get("/api/v1/kitchen/orders", headers=kitchen_headers)
    assert resp.status_code == 200
    ids = [o["id"] for o in resp.json()]
    assert order["id"] in ids


async def test_kitchen_accept_start_preparing_ready_without_partner(
    client, admin_headers, customer_headers, kitchen_headers, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    order_id = order["id"]

    resp = await client.post(f"/api/v1/kitchen/orders/{order_id}/accept", headers=kitchen_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "accepted"

    resp = await client.post(f"/api/v1/kitchen/orders/{order_id}/start-preparing", headers=kitchen_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "preparing"

    resp = await client.post(f"/api/v1/kitchen/orders/{order_id}/ready", headers=kitchen_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ready"
    assert body["delivery_partner"] is None
    # OTP is generated internally but never revealed on a staff-facing response
    assert body["delivery_otp"] is None


async def test_kitchen_ready_auto_assigns_available_partner(
    client, admin_headers, customer_headers, kitchen_headers, seeded_zone, delivery_partner
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    order_id = order["id"]

    await client.post(f"/api/v1/kitchen/orders/{order_id}/accept", headers=kitchen_headers)
    await client.post(f"/api/v1/kitchen/orders/{order_id}/start-preparing", headers=kitchen_headers)
    resp = await client.post(f"/api/v1/kitchen/orders/{order_id}/ready", headers=kitchen_headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "assigned"
    assert body["delivery_partner"]["id"] == str(delivery_partner.id)


async def test_kitchen_reject_cancels_order(client, admin_headers, customer_headers, kitchen_headers, seeded_zone):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)

    resp = await client.post(
        f"/api/v1/kitchen/orders/{order['id']}/reject",
        json={"reason": "out of stock"},
        headers=kitchen_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_cannot_skip_accept_before_preparing(
    client, admin_headers, customer_headers, kitchen_headers, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)

    resp = await client.post(
        f"/api/v1/kitchen/orders/{order['id']}/start-preparing", headers=kitchen_headers
    )
    assert resp.status_code == 409
