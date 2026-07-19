import pytest

from tests.helpers import create_category, create_food

pytestmark = pytest.mark.asyncio


async def test_get_empty_cart(client, customer_headers):
    resp = await client.get("/api/v1/cart", headers=customer_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["grand_total"] == 0
    assert body["delivery_charge"] == 0  # no delivery charge on an empty cart


async def test_add_item_computes_totals(client, admin_headers, customer_headers):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=100)

    resp = await client.post(
        "/api/v1/cart/items", json={"food_id": food["id"], "quantity": 2}, headers=customer_headers
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["item_total"] == 200.0
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 2
    assert body["grand_total"] > body["item_total"]  # delivery/packing/GST added


async def test_add_same_item_twice_accumulates_quantity(client, admin_headers, customer_headers):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=50)

    await client.post("/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers)
    resp = await client.post(
        "/api/v1/cart/items", json={"food_id": food["id"], "quantity": 2}, headers=customer_headers
    )
    body = resp.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 3


async def test_add_unavailable_food_rejected(client, admin_headers, customer_headers):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], is_available=False)

    resp = await client.post(
        "/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers
    )
    assert resp.status_code == 400


async def test_update_quantity(client, admin_headers, customer_headers):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=40)
    await client.post("/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers)

    resp = await client.patch(
        f"/api/v1/cart/items/{food['id']}", json={"quantity": 5}, headers=customer_headers
    )
    assert resp.status_code == 200
    assert resp.json()["items"][0]["quantity"] == 5


async def test_remove_item(client, admin_headers, customer_headers):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"])
    await client.post("/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers)

    resp = await client.delete(f"/api/v1/cart/items/{food['id']}", headers=customer_headers)
    assert resp.status_code == 200
    assert resp.json()["items"] == []


async def test_cart_requires_auth(client):
    resp = await client.get("/api/v1/cart")
    assert resp.status_code == 401


async def test_cart_with_invalid_coupon_reports_error_not_failure(client, admin_headers, customer_headers):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=100)
    await client.post("/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers)

    resp = await client.get("/api/v1/cart", params={"coupon_code": "NOPE"}, headers=customer_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["coupon_error"] is not None
    assert body["discount_amount"] == 0
