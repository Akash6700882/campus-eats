import pytest

from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG
from tests.helpers import place_order

pytestmark = pytest.mark.asyncio


async def _me(client, headers) -> dict:
    return (await client.get("/api/v1/auth/me", headers=headers)).json()


async def test_non_admin_cannot_list_audit_logs(client, customer_headers):
    resp = await client.get("/api/v1/admin/audit-logs", headers=customer_headers)
    assert resp.status_code == 403


async def test_blocking_a_user_writes_an_audit_log_entry(client, admin_headers, customer_headers):
    me = await _me(client, customer_headers)
    await client.post(f"/api/v1/admin/users/{me['id']}/block", headers=admin_headers)

    resp = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    entries = resp.json()
    entry = next(e for e in entries if e["action"] == "user.block" and e["target_id"] == me["id"])
    assert entry["target_type"] == "user"
    assert entry["actor_name"]


async def test_force_cancel_writes_an_audit_log_entry_with_reason(
    client, admin_headers, customer_headers, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    await client.post(
        f"/api/v1/admin/orders/{order['id']}/cancel",
        json={"reason": "kitchen closed early"},
        headers=admin_headers,
    )

    resp = await client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    entries = resp.json()
    entry = next(e for e in entries if e["action"] == "order.force_cancel" and e["target_id"] == order["id"])
    assert "kitchen closed early" in entry["details"]


async def test_delivery_zone_update_writes_an_audit_log_entry(client, admin_headers):
    import json

    polygon = json.dumps(
        {"type": "Polygon", "coordinates": [[[91.69, 26.19], [91.70, 26.19], [91.70, 26.20], [91.69, 26.19]]]}
    )
    resp = await client.put(
        "/api/v1/admin/delivery-zone",
        json={"name": "Test Zone", "polygon_geojson": polygon},
        headers=admin_headers,
    )
    zone_id = resp.json()["id"]

    logs = (await client.get("/api/v1/admin/audit-logs", headers=admin_headers)).json()
    entry = next(e for e in logs if e["action"] == "delivery_zone.update" and e["target_id"] == zone_id)
    assert entry["target_type"] == "delivery_zone"


async def test_audit_logs_ordered_most_recent_first(client, admin_headers, customer_headers):
    me = await _me(client, customer_headers)
    await client.post(f"/api/v1/admin/users/{me['id']}/block", headers=admin_headers)
    await client.post(f"/api/v1/admin/users/{me['id']}/unblock", headers=admin_headers)

    logs = (await client.get("/api/v1/admin/audit-logs", headers=admin_headers)).json()
    actions = [e["action"] for e in logs if e["target_id"] == me["id"]]
    assert actions[:2] == ["user.unblock", "user.block"]
