import uuid

from pydantic import BaseModel, Field


class DeliveryPartnerBrief(BaseModel):
    id: uuid.UUID
    full_name: str
    phone: str
    vehicle_number: str | None
    current_latitude: float | None
    current_longitude: float | None

    @staticmethod
    def from_partner(partner) -> "DeliveryPartnerBrief":
        return DeliveryPartnerBrief(
            id=partner.id,
            full_name=partner.user.full_name,
            phone=partner.user.phone,
            vehicle_number=partner.vehicle_number,
            current_latitude=partner.current_latitude,
            current_longitude=partner.current_longitude,
        )


class DeliveryPartnerCreateRequest(BaseModel):
    user_id: uuid.UUID
    vehicle_number: str | None = None


class DeliveryPartnerResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    phone: str
    vehicle_number: str | None
    is_available: bool
    current_latitude: float | None
    current_longitude: float | None
    rating_avg: float
    total_deliveries: int
    today_earnings: float

    @staticmethod
    def from_partner(partner) -> "DeliveryPartnerResponse":
        return DeliveryPartnerResponse(
            id=partner.id,
            user_id=partner.user_id,
            full_name=partner.user.full_name,
            phone=partner.user.phone,
            vehicle_number=partner.vehicle_number,
            is_available=partner.is_available,
            current_latitude=partner.current_latitude,
            current_longitude=partner.current_longitude,
            rating_avg=float(partner.rating_avg),
            total_deliveries=partner.total_deliveries,
            today_earnings=float(partner.today_earnings),
        )


class DeliveryLocationUpdateRequest(BaseModel):
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    is_available: bool | None = None


class DeliverOrderRequest(BaseModel):
    otp: str


class KitchenRejectRequest(BaseModel):
    reason: str | None = None


class AdminCancelRequest(BaseModel):
    reason: str | None = None


class AdminAssignPartnerRequest(BaseModel):
    delivery_partner_id: uuid.UUID


class AdminUserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    phone: str
    role: str

    @staticmethod
    def from_user(user) -> "AdminUserResponse":
        return AdminUserResponse(
            id=user.id, full_name=user.full_name, email=user.email, phone=user.phone, role=user.role.name
        )
