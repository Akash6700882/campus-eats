import pytest

from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG
from tests.helpers import advance_order_to_delivered, place_order

pytestmark = pytest.mark.asyncio


async def test_cannot_review_food_never_ordered(client, admin_headers, customer_headers):
    category = (
        await client.post("/api/v1/admin/categories", json={"name": "Snacks2"}, headers=admin_headers)
    ).json()
    food = (
        await client.post(
            "/api/v1/admin/foods",
            json={"category_id": category["id"], "name": "Vada", "price": 30, "is_veg": True},
            headers=admin_headers,
        )
    ).json()

    resp = await client.post(
        f"/api/v1/foods/{food['id']}/reviews", json={"rating": 5, "comment": "Great!"}, headers=customer_headers
    )
    assert resp.status_code == 400
    assert "delivered" in resp.json()["detail"]


async def test_review_delivered_order_updates_food_rating(
    client, admin_headers, customer_headers, kitchen_headers, delivery_headers, delivery_partner, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    food_id = order["items"][0]["food_id"]
    await advance_order_to_delivered(client, kitchen_headers, delivery_headers, customer_headers, order["id"])

    resp = await client.post(
        f"/api/v1/foods/{food_id}/reviews",
        json={"rating": 4, "comment": "Tasty", "order_id": order["id"]},
        headers=customer_headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["rating"] == 4
    assert body["likes_count"] == 0

    listed = await client.get(f"/api/v1/foods/{food_id}/reviews")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["user_name"]

    foods = (await client.get("/api/v1/foods?limit=200")).json()
    updated_food = next(f for f in foods if f["id"] == food_id)
    assert updated_food["rating_avg"] == 4.0
    assert updated_food["rating_count"] == 1


async def test_cannot_review_same_food_twice(
    client, admin_headers, customer_headers, kitchen_headers, delivery_headers, delivery_partner, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    food_id = order["items"][0]["food_id"]
    await advance_order_to_delivered(client, kitchen_headers, delivery_headers, customer_headers, order["id"])

    await client.post(f"/api/v1/foods/{food_id}/reviews", json={"rating": 5}, headers=customer_headers)
    resp = await client.post(f"/api/v1/foods/{food_id}/reviews", json={"rating": 3}, headers=customer_headers)
    assert resp.status_code == 400
    assert "already reviewed" in resp.json()["detail"]


async def test_like_and_unlike_review_toggles(
    client, admin_headers, customer_headers, kitchen_headers, delivery_headers, delivery_partner, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    food_id = order["items"][0]["food_id"]
    await advance_order_to_delivered(client, kitchen_headers, delivery_headers, customer_headers, order["id"])
    review = (
        await client.post(f"/api/v1/foods/{food_id}/reviews", json={"rating": 5}, headers=customer_headers)
    ).json()

    liked = await client.post(f"/api/v1/reviews/{review['id']}/like", headers=admin_headers)
    assert liked.status_code == 200
    assert liked.json() == {"review_id": review["id"], "liked": True, "likes_count": 1}

    unliked = await client.post(f"/api/v1/reviews/{review['id']}/like", headers=admin_headers)
    assert unliked.json() == {"review_id": review["id"], "liked": False, "likes_count": 0}


async def test_delete_own_review(
    client, admin_headers, customer_headers, kitchen_headers, delivery_headers, delivery_partner, seeded_zone
):
    order = await place_order(client, admin_headers, customer_headers, IN_CAMPUS_LAT, IN_CAMPUS_LNG)
    food_id = order["items"][0]["food_id"]
    await advance_order_to_delivered(client, kitchen_headers, delivery_headers, customer_headers, order["id"])
    review = (
        await client.post(f"/api/v1/foods/{food_id}/reviews", json={"rating": 5}, headers=customer_headers)
    ).json()

    resp = await client.delete(f"/api/v1/reviews/{review['id']}", headers=customer_headers)
    assert resp.status_code == 204

    resp = await client.delete(f"/api/v1/reviews/{review['id']}", headers=admin_headers)
    assert resp.status_code == 404
