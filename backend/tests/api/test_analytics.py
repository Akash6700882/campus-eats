import pytest

from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG
from tests.helpers import advance_order_to_delivered, place_order

pytestmark = pytest.mark.asyncio


async def test_non_admin_cannot_access_analytics(client, customer_headers):
    resp = await client.get("/api/v1/admin/analytics/summary", headers=customer_headers)
    assert resp.status_code == 403


async def test_analytics_summary_reflects_delivered_order(
    client, admin_headers, customer_headers, kitchen_headers, delivery_headers, delivery_partner, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG, price=100)
    delivered = await advance_order_to_delivered(
        client, kitchen_headers, delivery_headers, customer_headers, order["id"]
    )

    resp = await client.get("/api/v1/admin/analytics/summary", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()

    assert body["total_orders"] >= 1
    assert body["total_revenue"] >= delivered["grand_total"]
    assert body["total_customers"] >= 1
    assert body["total_delivery_partners"] >= 1
    assert any(s["status"] == "delivered" and s["count"] >= 1 for s in body["orders_by_status"])
    assert any(f["name"] == delivered["items"][0]["food_name"] for f in body["best_selling_foods"])
