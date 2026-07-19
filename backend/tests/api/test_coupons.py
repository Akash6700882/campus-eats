from datetime import datetime, timedelta, timezone

import pytest

from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG
from tests.helpers import create_category, create_food

pytestmark = pytest.mark.asyncio

VALID_FROM = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
VALID_TO = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()


async def _create_coupon(client, admin_headers, **overrides):
    payload = {
        "code": "WELCOME10",
        "discount_type": "percent",
        "discount_value": 10,
        "min_order_amount": 50,
        "valid_from": VALID_FROM,
        "valid_to": VALID_TO,
        "per_user_limit": 1,
        **overrides,
    }
    resp = await client.post("/api/v1/admin/coupons", json=payload, headers=admin_headers)
    return resp


async def test_admin_creates_coupon(client, admin_headers):
    resp = await _create_coupon(client, admin_headers)
    assert resp.status_code == 201
    assert resp.json()["code"] == "WELCOME10"


async def test_duplicate_coupon_code_rejected(client, admin_headers):
    await _create_coupon(client, admin_headers)
    resp = await _create_coupon(client, admin_headers)
    assert resp.status_code == 409


async def test_non_admin_cannot_create_coupon(client, customer_headers):
    resp = await _create_coupon(client, customer_headers)
    assert resp.status_code == 403


async def test_coupon_applies_discount_at_checkout(client, admin_headers, customer_headers, seeded_zone):
    await _create_coupon(client, admin_headers, code="SAVE10")
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=100)
    await client.post(
        "/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers
    )
    address = (
        await client.post(
            "/api/v1/addresses",
            json={"label": "Hostel", "latitude": IN_CAMPUS_LAT, "longitude": IN_CAMPUS_LNG},
            headers=customer_headers,
        )
    ).json()

    resp = await client.post(
        "/api/v1/orders",
        json={"address_id": address["id"], "coupon_code": "save10"},
        headers=customer_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["discount_amount"] == 10.0  # 10% of 100


async def test_coupon_below_minimum_order_rejected_at_checkout(
    client, admin_headers, customer_headers, seeded_zone
):
    await _create_coupon(client, admin_headers, code="BIG50", min_order_amount=500)
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=100)
    await client.post(
        "/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers
    )
    address = (
        await client.post(
            "/api/v1/addresses",
            json={"label": "Hostel", "latitude": IN_CAMPUS_LAT, "longitude": IN_CAMPUS_LNG},
            headers=customer_headers,
        )
    ).json()

    resp = await client.post(
        "/api/v1/orders",
        json={"address_id": address["id"], "coupon_code": "BIG50"},
        headers=customer_headers,
    )
    assert resp.status_code == 422
    assert "minimum order amount" in resp.json()["detail"]


async def test_coupon_per_user_limit_enforced(client, admin_headers, customer_headers, seeded_zone):
    await _create_coupon(client, admin_headers, code="ONCE", per_user_limit=1)
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=100)
    address = (
        await client.post(
            "/api/v1/addresses",
            json={"label": "Hostel", "latitude": IN_CAMPUS_LAT, "longitude": IN_CAMPUS_LNG},
            headers=customer_headers,
        )
    ).json()

    for _ in range(2):
        await client.post(
            "/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers
        )
        resp = await client.post(
            "/api/v1/orders",
            json={"address_id": address["id"], "coupon_code": "ONCE"},
            headers=customer_headers,
        )

    assert resp.status_code == 422
    assert "already used" in resp.json()["detail"]
