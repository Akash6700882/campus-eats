from typing import Protocol

import razorpay
import razorpay.errors

from app.core.config import get_settings


class PaymentError(Exception):
    pass


class PaymentGateway(Protocol):
    def create_order(self, amount_rupees: float, receipt: str) -> dict: ...

    def verify_signature(
        self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str
    ) -> bool: ...


class RazorpayGateway:
    """Thin wrapper around the Razorpay SDK. Injected via DI (see
    app/core/deps.py) so tests can substitute a fake implementation instead
    of calling the real Razorpay API with placeholder test keys."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client: razorpay.Client | None = None
        if settings.razorpay_key_id and settings.razorpay_key_secret:
            self._client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))

    @property
    def configured(self) -> bool:
        return self._client is not None

    def create_order(self, amount_rupees: float, receipt: str) -> dict:
        if self._client is None:
            raise PaymentError("Razorpay is not configured — set RAZORPAY_KEY_ID/SECRET in .env")
        amount_paise = int(round(amount_rupees * 100))
        try:
            return self._client.order.create(
                {"amount": amount_paise, "currency": "INR", "receipt": receipt, "payment_capture": 1}
            )
        except razorpay.errors.BadRequestError as exc:
            raise PaymentError(
                "Razorpay rejected the request — RAZORPAY_KEY_ID/SECRET in .env are placeholders, "
                "not real test-mode keys"
            ) from exc

    def verify_signature(
        self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str
    ) -> bool:
        if self._client is None:
            raise PaymentError("Razorpay is not configured — set RAZORPAY_KEY_ID/SECRET in .env")
        try:
            self._client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature,
                }
            )
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
