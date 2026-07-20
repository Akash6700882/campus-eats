import pytest

from tests.helpers import create_category, create_food

pytestmark = pytest.mark.asyncio


async def test_wishlist_add_list_remove(client, admin_headers, customer_headers):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"])

    resp = await client.post(f"/api/v1/wishlist/{food['id']}", headers=customer_headers)
    assert resp.status_code == 201, resp.text
    assert resp.json()["food"]["id"] == food["id"]

    listed = await client.get("/api/v1/wishlist", headers=customer_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    # adding the same food again is idempotent, not a duplicate error
    resp2 = await client.post(f"/api/v1/wishlist/{food['id']}", headers=customer_headers)
    assert resp2.status_code == 201
    listed_again = await client.get("/api/v1/wishlist", headers=customer_headers)
    assert len(listed_again.json()) == 1

    removed = await client.delete(f"/api/v1/wishlist/{food['id']}", headers=customer_headers)
    assert removed.status_code == 204
    listed_final = await client.get("/api/v1/wishlist", headers=customer_headers)
    assert listed_final.json() == []


async def test_remove_missing_wishlist_item_404(client, customer_headers):
    resp = await client.delete("/api/v1/wishlist/00000000-0000-0000-0000-000000000000", headers=customer_headers)
    assert resp.status_code == 404


async def test_wishlist_requires_auth(client):
    resp = await client.get("/api/v1/wishlist")
    assert resp.status_code == 401
