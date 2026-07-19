import pytest

from app.core.redis_client import get_redis

pytestmark = pytest.mark.asyncio

SIGNUP_PAYLOAD = {
    "full_name": "Test Student",
    "email": "student@campus.edu",
    "phone": "9876543210",
    "password": "SuperSecret1",
}


async def test_signup_returns_tokens(client):
    resp = await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_signup_duplicate_email_rejected(client):
    await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    resp = await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    assert resp.status_code == 409


async def test_signup_rejects_short_password(client):
    payload = {**SIGNUP_PAYLOAD, "password": "short"}
    resp = await client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 422


async def test_signup_rejects_invalid_phone(client):
    payload = {**SIGNUP_PAYLOAD, "phone": "123"}
    resp = await client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 422


async def test_login_success(client):
    await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    resp = await client.post(
        "/api/v1/auth/login", json={"email": SIGNUP_PAYLOAD["email"], "password": SIGNUP_PAYLOAD["password"]}
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_login_wrong_password_rejected(client):
    await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    resp = await client.post(
        "/api/v1/auth/login", json={"email": SIGNUP_PAYLOAD["email"], "password": "WrongPassword1"}
    )
    assert resp.status_code == 401


async def test_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_me_returns_current_user(client):
    signup_resp = await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    access_token = signup_resp.json()["access_token"]
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == SIGNUP_PAYLOAD["email"]
    assert body["role"] == "customer"


async def test_me_rejects_garbage_token(client):
    resp = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


async def test_refresh_issues_new_access_token(client):
    signup_resp = await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    refresh_token = signup_resp.json()["refresh_token"]
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_refresh_rejects_access_token_used_as_refresh(client):
    signup_resp = await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    access_token = signup_resp.json()["access_token"]
    resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": access_token})
    assert resp.status_code == 401


async def test_otp_login_round_trip(client):
    await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    phone = SIGNUP_PAYLOAD["phone"]

    resp = await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    assert resp.status_code == 204

    redis = get_redis()
    code = await redis.get(f"otp:{phone}")
    assert code is not None

    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "otp_code": code})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

    # OTP is single-use
    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "otp_code": code})
    assert resp.status_code == 401


async def test_otp_verify_wrong_code_rejected(client):
    await client.post("/api/v1/auth/signup", json=SIGNUP_PAYLOAD)
    phone = SIGNUP_PAYLOAD["phone"]
    await client.post("/api/v1/auth/otp/request", json={"phone": phone})
    resp = await client.post("/api/v1/auth/otp/verify", json={"phone": phone, "otp_code": "000000"})
    assert resp.status_code == 401


async def test_forgot_password_does_not_leak_account_existence(client):
    resp = await client.post("/api/v1/auth/forgot-password", json={"email": "nobody@campus.edu"})
    assert resp.status_code == 204


async def test_reset_password_with_invalid_token_rejected(client):
    resp = await client.post(
        "/api/v1/auth/reset-password", json={"token": "garbage", "new_password": "NewSecret1"}
    )
    assert resp.status_code == 400
