import csv
import io

import openpyxl
import pytest

from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG
from tests.helpers import place_order

pytestmark = pytest.mark.asyncio


async def _advance_to_ready(client, kitchen_headers, order_id):
    await client.post(f"/api/v1/kitchen/orders/{order_id}/accept", headers=kitchen_headers)
    await client.post(f"/api/v1/kitchen/orders/{order_id}/start-preparing", headers=kitchen_headers)
    return await client.post(f"/api/v1/kitchen/orders/{order_id}/ready", headers=kitchen_headers)


async def _deliver_order(client, admin_headers, customer_headers, kitchen_headers, delivery_headers, order_id):
    await _advance_to_ready(client, kitchen_headers, order_id)
    await client.post(f"/api/v1/delivery/orders/{order_id}/pickup", headers=delivery_headers)
    await client.post(f"/api/v1/delivery/orders/{order_id}/on-the-way", headers=delivery_headers)
    otp = (await client.get(f"/api/v1/orders/{order_id}", headers=customer_headers)).json()["delivery_otp"]
    resp = await client.post(
        f"/api/v1/delivery/orders/{order_id}/deliver", json={"otp": otp}, headers=delivery_headers
    )
    assert resp.status_code == 200, resp.text


async def test_non_admin_cannot_access_reports(client, customer_headers):
    resp = await client.get("/api/v1/admin/reports", headers=customer_headers)
    assert resp.status_code == 403


@pytest.mark.parametrize("period", ["daily", "weekly", "monthly", "yearly"])
async def test_report_accepts_every_period(client, admin_headers, period):
    resp = await client.get("/api/v1/admin/reports", params={"period": period}, headers=admin_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["period"] == period
    assert "start_date" in body and "end_date" in body


async def test_report_reflects_a_delivered_order(
    client, admin_headers, customer_headers, kitchen_headers, delivery_headers, delivery_partner, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG, price=100)
    await _deliver_order(client, admin_headers, customer_headers, kitchen_headers, delivery_headers, order["id"])

    resp = await client.get("/api/v1/admin/reports", params={"period": "weekly"}, headers=admin_headers)
    body = resp.json()
    assert body["total_orders"] >= 1
    assert body["total_revenue"] >= order["grand_total"]
    assert any(row["status"] == "delivered" for row in body["orders_by_status"])
    assert any(row["name"] == "Masala Dosa" for row in body["best_selling_foods"])
    assert len(body["daily_breakdown"]) >= 1


async def test_csv_export_is_well_formed(client, admin_headers, customer_headers, seeded_zone):
    await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)

    resp = await client.get(
        "/api/v1/admin/reports", params={"period": "weekly", "format": "csv"}, headers=admin_headers
    )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("text/csv")
    assert "attachment" in resp.headers["content-disposition"]

    rows = list(csv.reader(io.StringIO(resp.text)))
    assert rows[0][0] == "Campus Eats Report"


async def test_excel_export_is_valid_workbook(client, admin_headers, customer_headers, seeded_zone):
    await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)

    resp = await client.get(
        "/api/v1/admin/reports", params={"period": "weekly", "format": "excel"}, headers=admin_headers
    )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    wb = openpyxl.load_workbook(io.BytesIO(resp.content))
    ws = wb.active
    assert "Campus Eats Report" in str(ws.cell(1, 1).value)


async def test_pdf_export_is_a_pdf(client, admin_headers, customer_headers, seeded_zone):
    await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)

    resp = await client.get(
        "/api/v1/admin/reports", params={"period": "weekly", "format": "pdf"}, headers=admin_headers
    )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"
