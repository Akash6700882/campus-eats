import pytest

pytestmark = pytest.mark.asyncio


async def _create_category(client, admin_headers, name="Beverages"):
    resp = await client.post(
        "/api/v1/admin/categories", json={"name": name}, headers=admin_headers
    )
    assert resp.status_code == 201
    return resp.json()


async def _create_food(client, admin_headers, category_id, **overrides):
    payload = {
        "category_id": category_id,
        "name": "Masala Dosa",
        "price": 70,
        "is_veg": True,
        **overrides,
    }
    resp = await client.post("/api/v1/admin/foods", json=payload, headers=admin_headers)
    return resp


async def test_create_category_requires_admin(client):
    resp = await client.post("/api/v1/admin/categories", json={"name": "Snacks"})
    assert resp.status_code == 401


async def test_customer_cannot_create_category(client):
    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "full_name": "Regular Student",
            "email": "regular@campus.edu",
            "phone": "9111111111",
            "password": "RegularPass1",
        },
    )
    token = signup.json()["access_token"]
    resp = await client.post(
        "/api/v1/admin/categories",
        json={"name": "Snacks"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


async def test_admin_creates_category(client, admin_headers):
    category = await _create_category(client, admin_headers, name="South Indian")
    assert category["slug"] == "south-indian"
    assert category["is_active"] is True


async def test_duplicate_category_name_rejected(client, admin_headers):
    await _create_category(client, admin_headers, name="Snacks")
    resp = await client.post("/api/v1/admin/categories", json={"name": "Snacks"}, headers=admin_headers)
    assert resp.status_code == 409


async def test_list_categories_public(client, admin_headers):
    await _create_category(client, admin_headers, name="Juices")
    resp = await client.get("/api/v1/categories")
    assert resp.status_code == 200
    names = [c["name"] for c in resp.json()]
    assert "Juices" in names


async def test_create_food_and_fetch_by_slug(client, admin_headers):
    category = await _create_category(client, admin_headers)
    resp = await _create_food(client, admin_headers, category["id"], discount_percent=10)
    assert resp.status_code == 201
    body = resp.json()
    assert body["slug"] == "masala-dosa"
    assert body["discounted_price"] == 63.0  # 70 * 0.9

    fetch = await client.get(f"/api/v1/foods/{body['slug']}")
    assert fetch.status_code == 200
    assert fetch.json()["name"] == "Masala Dosa"


async def test_create_food_unknown_category_rejected(client, admin_headers):
    resp = await _create_food(client, admin_headers, "00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_update_food_price(client, admin_headers):
    category = await _create_category(client, admin_headers)
    created = (await _create_food(client, admin_headers, category["id"])).json()

    resp = await client.patch(
        f"/api/v1/admin/foods/{created['id']}", json={"price": 85}, headers=admin_headers
    )
    assert resp.status_code == 200
    assert resp.json()["price"] == 85.0


async def test_delete_food(client, admin_headers):
    category = await _create_category(client, admin_headers)
    created = (await _create_food(client, admin_headers, category["id"])).json()

    resp = await client.delete(f"/api/v1/admin/foods/{created['id']}", headers=admin_headers)
    assert resp.status_code == 204

    fetch = await client.get(f"/api/v1/foods/{created['slug']}")
    assert fetch.status_code == 404


async def test_search_foods_by_veg_flag(client, admin_headers):
    category = await _create_category(client, admin_headers)
    await _create_food(client, admin_headers, category["id"], name="Chicken Roll", is_veg=False)
    await _create_food(client, admin_headers, category["id"], name="Veg Roll", is_veg=True)

    resp = await client.get("/api/v1/foods", params={"is_veg": "true"})
    assert resp.status_code == 200
    names = [f["name"] for f in resp.json()]
    assert "Veg Roll" in names
    assert "Chicken Roll" not in names


async def test_search_foods_by_query_and_price_range(client, admin_headers):
    category = await _create_category(client, admin_headers)
    await _create_food(client, admin_headers, category["id"], name="Cheap Idli", price=30)
    await _create_food(client, admin_headers, category["id"], name="Fancy Idli", price=150)

    resp = await client.get("/api/v1/foods", params={"q": "Idli", "max_price": 50})
    assert resp.status_code == 200
    names = [f["name"] for f in resp.json()]
    assert names == ["Cheap Idli"]


async def test_image_upload_without_cloudinary_configured_returns_503(client, admin_headers):
    category = await _create_category(client, admin_headers)
    created = (await _create_food(client, admin_headers, category["id"])).json()

    files = {"file": ("test.jpg", b"fake-image-bytes", "image/jpeg")}
    resp = await client.post(
        f"/api/v1/admin/foods/{created['id']}/image", files=files, headers=admin_headers
    )
    assert resp.status_code == 503
