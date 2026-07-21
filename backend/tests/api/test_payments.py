import json
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.core.deps import get_payment_gateway
from app.main import app
from app.models.enums import PaymentStatus
from app.models.payment import Payment
from tests.conftest import IN_CAMPUS_LAT, IN_CAMPUS_LNG
from tests.helpers import create_category, create_food

pytestmark = pytest.mark.asyncio

VALID_WEBHOOK_SIGNATURE = "valid-webhook-signature"


class FakeGateway:
    """Stands in for Razorpay in tests — the real gateway needs live test-mode
    API keys and a network call, which CI/local runs shouldn't depend on."""

    def create_order(self, amount_rupees: float, receipt: str) -> dict:
        return {"id": f"order_fake_{uuid.uuid4().hex[:12]}", "amount": int(amount_rupees * 100), "currency": "INR"}

    def verify_signature(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        return razorpay_signature == f"valid-{razorpay_payment_id}"

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        return signature == VALID_WEBHOOK_SIGNATURE


@pytest_asyncio.fixture(autouse=True)
async def _fake_gateway(client):
    app.dependency_overrides[get_payment_gateway] = lambda: FakeGateway()
    yield
    app.dependency_overrides.pop(get_payment_gateway, None)


async def _place_order(client, admin_headers, customer_headers, seeded_zone, price=100):
    category = await create_category(client, admin_headers)
    food = await create_food(client, admin_headers, category["id"], price=price)
    await client.post(
        "/api/v1/cart/items", json={"food_id": food["id"], "quantity": 1}, headers=customer_headers
    )
    address = (
        await client.post(
            "/api/v1/addresses",
            json={"label": "Hostel", "latitude": IN_CAMPUS_LAT, "longitude": IN_CAMPUS_LNG},
            headers=customer_headers,
        )
    ).json()
    order = (
        await client.post("/api/v1/orders", json={"address_id": address["id"]}, headers=customer_headers)
    ).json()
    return order


async def test_initiate_payment(client, admin_headers, customer_headers, seeded_zone):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)

    resp = await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["razorpay_order_id"].startswith("order_fake_")
    assert body["amount"] == order["grand_total"]


async def test_verify_payment_success(client, admin_headers, customer_headers, seeded_zone):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()

    payment_id = "pay_fake_123"
    resp = await client.post(
        f"/api/v1/orders/{order['id']}/payment/verify",
        json={
            "razorpay_order_id": initiate["razorpay_order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": f"valid-{payment_id}",
        },
        headers=customer_headers,
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "paid"


async def test_verify_payment_wrong_signature_fails(client, admin_headers, customer_headers, seeded_zone):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()

    resp = await client.post(
        f"/api/v1/orders/{order['id']}/payment/verify",
        json={
            "razorpay_order_id": initiate["razorpay_order_id"],
            "razorpay_payment_id": "pay_fake_456",
            "razorpay_signature": "totally-wrong",
        },
        headers=customer_headers,
    )
    assert resp.status_code == 400


async def test_verify_unknown_razorpay_order_id_rejected(client, admin_headers, customer_headers, seeded_zone):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)

    resp = await client.post(
        f"/api/v1/orders/{order['id']}/payment/verify",
        json={
            "razorpay_order_id": "order_never_created",
            "razorpay_payment_id": "pay_fake_789",
            "razorpay_signature": "valid-pay_fake_789",
        },
        headers=customer_headers,
    )
    assert resp.status_code == 400


async def test_cannot_initiate_payment_for_already_paid_order(
    client, admin_headers, customer_headers, seeded_zone
):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()
    payment_id = "pay_fake_paid"
    await client.post(
        f"/api/v1/orders/{order['id']}/payment/verify",
        json={
            "razorpay_order_id": initiate["razorpay_order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": f"valid-{payment_id}",
        },
        headers=customer_headers,
    )

    resp = await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    assert resp.status_code == 422


async def test_cancel_unpaid_order_restores_cart(client, admin_headers, customer_headers, seeded_zone):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)

    resp = await client.post(f"/api/v1/orders/{order['id']}/payment/cancel", headers=customer_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"

    cart = (await client.get("/api/v1/cart", headers=customer_headers)).json()
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 1


async def test_cannot_cancel_already_paid_order_via_payment_cancel(
    client, admin_headers, customer_headers, seeded_zone
):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()
    payment_id = "pay_fake_done"
    await client.post(
        f"/api/v1/orders/{order['id']}/payment/verify",
        json={
            "razorpay_order_id": initiate["razorpay_order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": f"valid-{payment_id}",
        },
        headers=customer_headers,
    )

    resp = await client.post(f"/api/v1/orders/{order['id']}/payment/cancel", headers=customer_headers)
    assert resp.status_code == 409


async def test_get_invoice_returns_pdf(client, admin_headers, customer_headers, seeded_zone):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)

    resp = await client.get(f"/api/v1/orders/{order['id']}/invoice", headers=customer_headers)
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert resp.content[:4] == b"%PDF"


def _webhook_payload(event: str, provider_order_id: str, payment_id: str, error_description: str | None = None) -> bytes:
    entity = {"id": payment_id, "order_id": provider_order_id}
    if error_description:
        entity["error_description"] = error_description
    return json.dumps({"event": event, "payload": {"payment": {"entity": entity}}}).encode()


async def _get_payment(db_session, provider_order_id: str) -> Payment:
    result = await db_session.execute(select(Payment).where(Payment.provider_order_id == provider_order_id))
    return result.scalar_one()


async def test_webhook_payment_captured_marks_payment_paid(
    client, admin_headers, customer_headers, seeded_zone, db_session
):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()

    body = _webhook_payload("payment.captured", initiate["razorpay_order_id"], "pay_webhook_1")
    resp = await client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={"X-Razorpay-Signature": VALID_WEBHOOK_SIGNATURE, "Content-Type": "application/json"},
    )
    assert resp.status_code == 200, resp.text

    payment = await _get_payment(db_session, initiate["razorpay_order_id"])
    assert payment.status == PaymentStatus.PAID
    assert payment.provider_payment_id == "pay_webhook_1"


async def test_webhook_payment_failed_marks_payment_failed(
    client, admin_headers, customer_headers, seeded_zone, db_session
):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()

    body = _webhook_payload(
        "payment.failed", initiate["razorpay_order_id"], "pay_webhook_2", error_description="card declined"
    )
    resp = await client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={"X-Razorpay-Signature": VALID_WEBHOOK_SIGNATURE, "Content-Type": "application/json"},
    )
    assert resp.status_code == 200, resp.text

    payment = await _get_payment(db_session, initiate["razorpay_order_id"])
    assert payment.status == PaymentStatus.FAILED
    assert payment.failure_reason == "card declined"


async def test_webhook_rejects_invalid_signature(client, admin_headers, customer_headers, seeded_zone):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()

    body = _webhook_payload("payment.captured", initiate["razorpay_order_id"], "pay_webhook_3")
    resp = await client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={"X-Razorpay-Signature": "not-valid", "Content-Type": "application/json"},
    )
    assert resp.status_code == 400


async def test_webhook_unknown_order_id_is_a_noop(client):
    body = _webhook_payload("payment.captured", "order_never_existed", "pay_webhook_4")
    resp = await client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={"X-Razorpay-Signature": VALID_WEBHOOK_SIGNATURE, "Content-Type": "application/json"},
    )
    assert resp.status_code == 200


async def test_webhook_does_not_override_client_side_verified_payment(
    client, admin_headers, customer_headers, seeded_zone, db_session
):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()

    payment_id = "pay_client_side"
    await client.post(
        f"/api/v1/orders/{order['id']}/payment/verify",
        json={
            "razorpay_order_id": initiate["razorpay_order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": f"valid-{payment_id}",
        },
        headers=customer_headers,
    )

    # Webhook arrives afterwards with a different payment id — should not
    # overwrite what the client-side verify already recorded.
    body = _webhook_payload("payment.captured", initiate["razorpay_order_id"], "pay_webhook_late")
    resp = await client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={"X-Razorpay-Signature": VALID_WEBHOOK_SIGNATURE, "Content-Type": "application/json"},
    )
    assert resp.status_code == 200

    payment = await _get_payment(db_session, initiate["razorpay_order_id"])
    assert payment.status == PaymentStatus.PAID
    assert payment.provider_payment_id == payment_id


async def test_verify_payment_auto_confirms_without_kitchen(client, admin_headers, customer_headers, seeded_zone):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()

    payment_id = "pay_autoconfirm_1"
    resp = await client.post(
        f"/api/v1/orders/{order['id']}/payment/verify",
        json={
            "razorpay_order_id": initiate["razorpay_order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": f"valid-{payment_id}",
        },
        headers=customer_headers,
    )
    assert resp.status_code == 200, resp.text

    order_detail = (await client.get(f"/api/v1/orders/{order['id']}", headers=customer_headers)).json()
    assert order_detail["status"] == "ready"
    assert order_detail["delivery_partner"] is None


async def test_verify_payment_auto_assigns_available_delivery_partner(
    client, admin_headers, customer_headers, seeded_zone, delivery_partner
):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()

    payment_id = "pay_autoconfirm_2"
    await client.post(
        f"/api/v1/orders/{order['id']}/payment/verify",
        json={
            "razorpay_order_id": initiate["razorpay_order_id"],
            "razorpay_payment_id": payment_id,
            "razorpay_signature": f"valid-{payment_id}",
        },
        headers=customer_headers,
    )

    order_detail = (await client.get(f"/api/v1/orders/{order['id']}", headers=customer_headers)).json()
    assert order_detail["status"] == "assigned"
    assert order_detail["delivery_partner"]["id"] == str(delivery_partner.id)


async def test_webhook_auto_confirms_order_without_kitchen(client, admin_headers, customer_headers, seeded_zone):
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)
    initiate = (
        await client.post(f"/api/v1/orders/{order['id']}/payment/initiate", headers=customer_headers)
    ).json()

    body = _webhook_payload("payment.captured", initiate["razorpay_order_id"], "pay_webhook_autoconfirm")
    resp = await client.post(
        "/api/v1/payments/webhook",
        content=body,
        headers={"X-Razorpay-Signature": VALID_WEBHOOK_SIGNATURE, "Content-Type": "application/json"},
    )
    assert resp.status_code == 200, resp.text

    order_detail = (await client.get(f"/api/v1/orders/{order['id']}", headers=customer_headers)).json()
    assert order_detail["status"] == "ready"


async def test_kitchen_endpoints_still_work_directly_when_never_paid(
    client, admin_headers, customer_headers, kitchen_headers, seeded_zone
):
    """The kitchen API isn't deleted, just no longer required — an order
    that's never paid still sits in the kitchen queue exactly as before."""
    order = await _place_order(client, admin_headers, customer_headers, seeded_zone)

    resp = await client.post(f"/api/v1/kitchen/orders/{order['id']}/accept", headers=kitchen_headers)
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "accepted"
