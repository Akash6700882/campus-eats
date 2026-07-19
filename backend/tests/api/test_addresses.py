import pytest

pytestmark = pytest.mark.asyncio

ADDRESS_PAYLOAD = {
    "label": "Hostel",
    "hostel": "Block A",
    "room_number": "204",
    "latitude": 12.975,
    "longitude": 77.595,
    "is_default": True,
}


async def test_create_and_list_address(client, customer_headers):
    resp = await client.post("/api/v1/addresses", json=ADDRESS_PAYLOAD, headers=customer_headers)
    assert resp.status_code == 201
    assert resp.json()["is_default"] is True

    resp = await client.get("/api/v1/addresses", headers=customer_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_setting_new_default_unsets_previous(client, customer_headers):
    await client.post("/api/v1/addresses", json=ADDRESS_PAYLOAD, headers=customer_headers)
    resp = await client.post(
        "/api/v1/addresses", json={**ADDRESS_PAYLOAD, "label": "Department"}, headers=customer_headers
    )
    second_id = resp.json()["id"]
    assert resp.json()["is_default"] is True

    addresses = (await client.get("/api/v1/addresses", headers=customer_headers)).json()
    defaults = [a for a in addresses if a["is_default"]]
    assert len(defaults) == 1
    assert defaults[0]["id"] == second_id


async def test_update_address(client, customer_headers):
    created = (
        await client.post("/api/v1/addresses", json=ADDRESS_PAYLOAD, headers=customer_headers)
    ).json()
    resp = await client.patch(
        f"/api/v1/addresses/{created['id']}", json={"room_number": "305"}, headers=customer_headers
    )
    assert resp.status_code == 200
    assert resp.json()["room_number"] == "305"


async def test_delete_address(client, customer_headers):
    created = (
        await client.post("/api/v1/addresses", json=ADDRESS_PAYLOAD, headers=customer_headers)
    ).json()
    resp = await client.delete(f"/api/v1/addresses/{created['id']}", headers=customer_headers)
    assert resp.status_code == 204

    addresses = (await client.get("/api/v1/addresses", headers=customer_headers)).json()
    assert addresses == []


async def test_cannot_access_another_users_address(client, customer_headers, admin_headers):
    created = (
        await client.post("/api/v1/addresses", json=ADDRESS_PAYLOAD, headers=customer_headers)
    ).json()
    resp = await client.patch(
        f"/api/v1/addresses/{created['id']}", json={"room_number": "999"}, headers=admin_headers
    )
    assert resp.status_code == 404


async def test_invalid_latitude_rejected(client, customer_headers):
    resp = await client.post(
        "/api/v1/addresses", json={**ADDRESS_PAYLOAD, "latitude": 500}, headers=customer_headers
    )
    assert resp.status_code == 422
