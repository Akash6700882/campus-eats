import pytest

from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG, OUT_OF_CAMPUS_LAT, OUT_OF_CAMPUS_LNG
from tests.helpers import create_category, create_food

pytestmark = pytest.mark.asyncio


async def _add_to_cart(client, customer_headers, food_id, quantity=1):
    resp = await client.post(
        "/api/v1/cart/items", json={"food_id": food_id, "quantity": quantity}, headers=customer_headers
    )
    assert resp.status_code == 201, resp.text


async def _create_address(client, customer_headers, lat, lng):
    resp = await client.post(
        "/api/v1/addresses",
        json={"label": "Hostel", "hostel": "Block A", "room_number": "1", "latitude": lat, "longitude": lng},
        headers=customer_headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


async def test_checkout_requires_active_delivery_zone(client, admin_headers, customer_headers):
    # no seeded_zone fixture used here — zero active zones configured
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=100)
    await _add_to_cart(client, customer_headers, food["id"])
    address = await _create_address(client, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)

    resp = await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    assert resp.status_code == 422
    assert "delivery zone" in resp.json()["detail"]


async def test_checkout_success_in_campus(client, admin_headers, customer_headers, seeded_zone):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=100)
    await _add_to_cart(client, customer_headers, food["id"], quantity=2)
    address = await _create_address(client, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)

    resp = await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert body["item_total"] == 200.0
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 2
    assert body["grand_total"] > body["item_total"]

    # cart is cleared after checkout
    cart = (await client.get("/api/v1/cart", headers=customer_headers)).json()
    assert cart["items"] == []


async def test_checkout_rejected_outside_campus(client, admin_headers, customer_headers, seeded_zone):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"])
    await _add_to_cart(client, customer_headers, food["id"])
    address = await _create_address(client, customer_headers, OUT_OF_CAMPUS_LAT, OUT_OF_CAMPUS_LNG)

    resp = await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    assert resp.status_code == 422
    assert "outside" in resp.json()["detail"]


async def test_checkout_empty_cart_rejected(client, customer_headers, seeded_zone):
    address = await _create_address(client, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    resp = await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    assert resp.status_code == 422
    assert "empty" in resp.json()["detail"]


async def test_list_and_get_order(client, admin_headers, customer_headers, seeded_zone):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"])
    await _add_to_cart(client, customer_headers, food["id"])
    address = await _create_address(client, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    created = (
        await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    ).json()

    listed = (await client.get("/api/v1/orders", headers=customer_headers)).json()
    assert len(listed) == 1

    fetched = await client.get(f"/api/v1/orders/{created['id']}", headers=customer_headers)
    assert fetched.status_code == 200
    assert fetched.json()["order_number"] == created["order_number"]


async def test_other_users_order_not_visible(client, admin_headers, customer_headers, seeded_zone):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"])
    await _add_to_cart(client, customer_headers, food["id"])
    address = await _create_address(client, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    created = (
        await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    ).json()

    resp = await client.get(f"/api/v1/orders/{created['id']}", headers=admin_headers)
    assert resp.status_code == 404


async def test_cancel_pending_order(client, admin_headers, customer_headers, seeded_zone):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"])
    await _add_to_cart(client, customer_headers, food["id"])
    address = await _create_address(client, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    created = (
        await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    ).json()

    resp = await client.post(f"/api/v1/orders/{created['id']}/cancel", headers=customer_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_cancel_already_cancelled_order_rejected(client, admin_headers, customer_headers, seeded_zone):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"])
    await _add_to_cart(client, customer_headers, food["id"])
    address = await _create_address(client, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    created = (
        await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    ).json()
    await client.post(f"/api/v1/orders/{created['id']}/cancel", headers=customer_headers)

    resp = await client.post(f"/api/v1/orders/{created['id']}/cancel", headers=customer_headers)
    assert resp.status_code == 409
