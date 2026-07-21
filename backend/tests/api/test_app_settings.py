import pytest

from tests.helpers import create_category, create_food

pytestmark = pytest.mark.asyncio


async def test_get_settings_is_public_and_returns_defaults(client):
    resp = await client.get("/api/v1/settings")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["restaurant_name"] == "Campus Eats"
    assert body["gst_percent"] == 5.0
    assert body["delivery_charge"] == 15.0
    assert body["packing_charge"] == 5.0
    assert body["business_hours_open"] == "09:00"
    assert body["business_hours_close"] == "22:00"


async def test_non_admin_cannot_update_settings(client, customer_headers):
    resp = await client.put(
        "/api/v1/admin/settings",
        json={
            "restaurant_name": "Hacked",
            "gst_percent": 5,
            "delivery_charge": 15,
            "packing_charge": 5,
            "business_hours_open": "09:00",
            "business_hours_close": "22:00",
        },
        headers=customer_headers,
    )
    assert resp.status_code == 403


async def test_admin_updates_settings_and_get_reflects_it(client, admin_headers):
    resp = await client.put(
        "/api/v1/admin/settings",
        json={
            "restaurant_name": "IIT Guwahati Canteen",
            "gst_percent": 8,
            "delivery_charge": 20,
            "packing_charge": 10,
            "business_hours_open": "08:00",
            "business_hours_close": "23:30",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text

    refetched = (await client.get("/api/v1/settings")).json()
    assert refetched["restaurant_name"] == "IIT Guwahati Canteen"
    assert refetched["gst_percent"] == 8.0
    assert refetched["delivery_charge"] == 20.0
    assert refetched["packing_charge"] == 10.0
    assert refetched["business_hours_open"] == "08:00"
    assert refetched["business_hours_close"] == "23:30"


async def test_update_rejects_malformed_business_hours(client, admin_headers):
    resp = await client.put(
        "/api/v1/admin/settings",
        json={
            "restaurant_name": "Campus Eats",
            "gst_percent": 5,
            "delivery_charge": 15,
            "packing_charge": 5,
            "business_hours_open": "9am",
            "business_hours_close": "22:00",
        },
        headers=admin_headers,
    )
    assert resp.status_code == 422


async def test_updated_gst_and_charges_flow_into_cart_and_checkout(
    client, admin_headers, customer_headers, seeded_zone
):
    from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG

    await client.put(
        "/api/v1/admin/settings",
        json={
            "restaurant_name": "Campus Eats",
            "gst_percent": 10,
            "delivery_charge": 25,
            "packing_charge": 15,
            "business_hours_open": "09:00",
            "business_hours_close": "22:00",
        },
        headers=admin_headers,
    )

    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=100)
    await client.post(
        "/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers
    )

    cart = (await client.get("/api/v1/cart", headers=customer_headers)).json()
    assert cart["delivery_charge"] == 25.0
    assert cart["packing_charge"] == 15.0
    assert cart["gst_amount"] == 10.0  # 10% of 100

    address = (
        await client.post(
            "/api/v1/addresses",
            json={"label": "Hostel", "latitude": IN_CAMPUS_LAT, "longitude": IN_CAMPUS_LNG},
            headers=customer_headers,
        )
    ).json()
    order = (
        await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    ).json()
    assert order["delivery_charge"] == 25.0
    assert order["packing_charge"] == 15.0
    assert order["gst_amount"] == 10.0
    assert order["grand_total"] == 150.0  # 100 + 25 + 15 + 10
