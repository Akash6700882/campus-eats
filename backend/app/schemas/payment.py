import uuid

from pydantic import BaseModel

from app.core.config import get_settings
from app.models.enums import PaymentStatus


class PaymentInitiateResponse(BaseModel):
    payment_id: uuid.UUID
    razorpay_order_id: str
    razorpay_key_id: str
    amount: float
    currency: str

    @staticmethod
    def build(payment_id: uuid.UUID, razorpay_order: dict, amount: float) -> "PaymentInitiateResponse":
        return PaymentInitiateResponse(
            payment_id=payment_id,
            razorpay_order_id=razorpay_order["id"],
            razorpay_key_id=get_settings().razorpay_key_id,
            amount=amount,
            currency="INR",
        )


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class PaymentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    status: PaymentStatus
    amount: float
    currency: str
    provider_order_id: str | None
    provider_payment_id: str | None
    failure_reason: str | None

    model_config = {"from_attributes": True}
