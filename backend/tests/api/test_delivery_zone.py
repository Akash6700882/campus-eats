import json

import pytest

pytestmark = pytest.mark.asyncio

VALID_POLYGON = json.dumps(
    {
        "type": "Polygon",
        "coordinates": [[[91.69, 26.19], [91.70, 26.19], [91.70, 26.20], [91.69, 26.20], [91.69, 26.19]]],
    }
)


async def test_get_delivery_zone_returns_null_when_none_seeded(client):
    resp = await client.get("/api/v1/delivery-zone")
    assert resp.status_code == 200
    assert resp.json() is None


async def test_get_delivery_zone_returns_seeded_zone(client, seeded_zone):
    resp = await client.get("/api/v1/delivery-zone")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == str(seeded_zone.id)
    assert body["name"] == seeded_zone.name


async def test_non_admin_cannot_update_delivery_zone(client, customer_headers):
    resp = await client.put(
        "/api/v1/admin/delivery-zone",
        json={"name": "IIT Guwahati Campus", "polygon_geojson": VALID_POLYGON},
        headers=customer_headers,
    )
    assert resp.status_code == 403


async def test_admin_creates_zone_when_none_exists(client, admin_headers):
    resp = await client.put(
        "/api/v1/admin/delivery-zone",
        json={"name": "IIT Guwahati Campus", "polygon_geojson": VALID_POLYGON},
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["name"] == "IIT Guwahati Campus"
    assert body["is_active"] is True

    refetched = await client.get("/api/v1/delivery-zone")
    assert refetched.json()["id"] == body["id"]


async def test_admin_updates_existing_zone_in_place(client, admin_headers, seeded_zone):
    resp = await client.put(
        "/api/v1/admin/delivery-zone",
        json={"name": "Updated Campus Boundary", "polygon_geojson": VALID_POLYGON},
        headers=admin_headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["id"] == str(seeded_zone.id)
    assert body["name"] == "Updated Campus Boundary"
    assert body["polygon_geojson"] == VALID_POLYGON


async def test_update_rejects_invalid_polygon(client, admin_headers):
    resp = await client.put(
        "/api/v1/admin/delivery-zone",
        json={"name": "Bad Zone", "polygon_geojson": json.dumps({"type": "Point", "coordinates": [1, 2]})},
        headers=admin_headers,
    )
    assert resp.status_code == 422


async def test_update_rejects_malformed_json(client, admin_headers):
    resp = await client.put(
        "/api/v1/admin/delivery-zone",
        json={"name": "Bad Zone", "polygon_geojson": "not json"},
        headers=admin_headers,
    )
    assert resp.status_code == 422
