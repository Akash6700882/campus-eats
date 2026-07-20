async def create_category(client, admin_headers, name="Beverages"):
    resp = await client.post("/api/v1/admin/categories", json={"name": name}, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def create_food(client, admin_headers, category_id, **overrides):
    payload = {
        "category_id": category_id,
        "name": "Masala Dosa",
        "price": 70,
        "is_veg": True,
        **overrides,
    }
    resp = await client.post("/api/v1/admin/foods", json=payload, headers=admin_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def place_order(client, admin_headers, customer_headers, latitude, longitude, price=100):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=price)
    resp = await client.post(
        "/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers
    )
    assert resp.status_code == 201, resp.text
    address = (
        await client.post(
            "/api/v1/addresses",
            json={"label": "Hostel", "latitude": latitude, "longitude": longitude},
            headers=customer_headers,
        )
    ).json()
    resp = await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    assert resp.status_code == 201, resp.text
    return resp.json()


async def advance_order_to_delivered(client, kitchen_headers, delivery_headers, customer_headers, order_id):
    """Requires an available `delivery_partner` fixture so mark-ready auto-assigns."""
    await client.post(f"/api/v1/kitchen/orders/{order_id}/accept", headers=kitchen_headers)
    await client.post(f"/api/v1/kitchen/orders/{order_id}/start-preparing", headers=kitchen_headers)
    ready = await client.post(f"/api/v1/kitchen/orders/{order_id}/ready", headers=kitchen_headers)
    assert ready.json()["status"] == "assigned", ready.text

    await client.post(f"/api/v1/delivery/orders/{order_id}/pickup", headers=delivery_headers)
    await client.post(f"/api/v1/delivery/orders/{order_id}/on-the-way", headers=delivery_headers)
    otp = (await client.get(f"/api/v1/orders/{order_id}", headers=customer_headers)).json()["delivery_otp"]
    resp = await client.post(
        f"/api/v1/delivery/orders/{order_id}/deliver", json={"otp": otp}, headers=delivery_headers
    )
    assert resp.status_code == 200, resp.text
    return resp.json()
