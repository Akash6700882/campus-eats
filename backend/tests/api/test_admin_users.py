import pytest

pytestmark = pytest.mark.asyncio


async def _me(client, headers) -> dict:
    return (await client.get("/api/v1/auth/me", headers=headers)).json()


async def test_non_admin_cannot_list_customers(client, customer_headers):
    resp = await client.get("/api/v1/admin/customers", headers=customer_headers)
    assert resp.status_code == 403


async def test_admin_lists_customers_with_zero_stats_when_no_orders(client, admin_headers, customer_headers):
    me = await _me(client, customer_headers)
    resp = await client.get("/api/v1/admin/customers", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    customer = next(c for c in resp.json() if c["id"] == me["id"])
    assert customer["total_orders"] == 0
    assert customer["total_spend"] == 0
    assert customer["last_order_at"] is None
    assert customer["is_active"] is True


async def test_admin_blocks_and_unblocks_user(client, admin_headers, customer_headers):
    me = await _me(client, customer_headers)

    resp = await client.post(f"/api/v1/admin/users/{me['id']}/block", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["is_active"] is False

    # blocked account can no longer log in
    login = await client.post(
        "/api/v1/auth/login", json={"email": me["email"], "password": "CustomerPass1"}
    )
    assert login.status_code == 401

    resp = await client.post(f"/api/v1/admin/users/{me['id']}/unblock", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["is_active"] is True

    login = await client.post(
        "/api/v1/auth/login", json={"email": me["email"], "password": "CustomerPass1"}
    )
    assert login.status_code == 200


async def test_admin_cannot_block_own_account(client, admin_headers):
    me = await _me(client, admin_headers)
    resp = await client.post(f"/api/v1/admin/users/{me['id']}/block", headers=admin_headers)
    assert resp.status_code == 400


async def test_admin_resets_user_password(client, admin_headers, customer_headers):
    me = await _me(client, customer_headers)
    resp = await client.post(f"/api/v1/admin/users/{me['id']}/reset-password", headers=admin_headers)
    assert resp.status_code == 204


async def test_admin_reset_password_unknown_user_404s(client, admin_headers):
    resp = await client.post(
        "/api/v1/admin/users/00000000-0000-0000-0000-000000000000/reset-password", headers=admin_headers
    )
    assert resp.status_code == 404


async def test_admin_deletes_user_anonymizes_and_deactivates(client, admin_headers, customer_headers):
    me = await _me(client, customer_headers)

    resp = await client.delete(f"/api/v1/admin/users/{me['id']}", headers=admin_headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["full_name"] == "Deleted User"
    assert body["email"] != me["email"]
    assert body["is_active"] is False

    login = await client.post(
        "/api/v1/auth/login", json={"email": me["email"], "password": "CustomerPass1"}
    )
    assert login.status_code == 401


async def test_admin_cannot_delete_own_account(client, admin_headers):
    me = await _me(client, admin_headers)
    resp = await client.delete(f"/api/v1/admin/users/{me['id']}", headers=admin_headers)
    assert resp.status_code == 400
