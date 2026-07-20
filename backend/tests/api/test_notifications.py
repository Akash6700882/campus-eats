import pytest

from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG
from tests.helpers import place_order

pytestmark = pytest.mark.asyncio


async def test_kitchen_accept_creates_customer_notification(
    client, admin_headers, customer_headers, kitchen_headers, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)

    before = await client.get("/api/v1/notifications", headers=customer_headers)
    assert before.json()["unread_count"] == 0

    await client.post(f"/api/v1/kitchen/orders/{order['id']}/accept", headers=kitchen_headers)

    after = await client.get("/api/v1/notifications", headers=customer_headers)
    assert after.json()["unread_count"] == 1
    assert after.json()["items"][0]["title"] == "Order accepted"
    assert order["order_number"] in after.json()["items"][0]["message"]


async def test_mark_notification_read(client, admin_headers, customer_headers, kitchen_headers, seeded_zone):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    await client.post(f"/api/v1/kitchen/orders/{order['id']}/accept", headers=kitchen_headers)

    notifications = (await client.get("/api/v1/notifications", headers=customer_headers)).json()
    notification_id = notifications["items"][0]["id"]

    resp = await client.post(f"/api/v1/notifications/{notification_id}/read", headers=customer_headers)
    assert resp.status_code == 200
    assert resp.json()["is_read"] is True

    after = await client.get("/api/v1/notifications", headers=customer_headers)
    assert after.json()["unread_count"] == 0


async def test_mark_all_read(client, admin_headers, customer_headers, kitchen_headers, seeded_zone):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    await client.post(f"/api/v1/kitchen/orders/{order['id']}/accept", headers=kitchen_headers)
    await client.post(f"/api/v1/kitchen/orders/{order['id']}/start-preparing", headers=kitchen_headers)

    resp = await client.post("/api/v1/notifications/read-all", headers=customer_headers)
    assert resp.status_code == 204

    after = await client.get("/api/v1/notifications", headers=customer_headers)
    assert after.json()["unread_count"] == 0
    assert len(after.json()["items"]) == 2


async def test_cannot_mark_other_users_notification_read(
    client, admin_headers, customer_headers, kitchen_headers, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    await client.post(f"/api/v1/kitchen/orders/{order['id']}/accept", headers=kitchen_headers)
    notification_id = (await client.get("/api/v1/notifications", headers=customer_headers)).json()["items"][0]["id"]

    resp = await client.post(f"/api/v1/notifications/{notification_id}/read", headers=admin_headers)
    assert resp.status_code == 404
