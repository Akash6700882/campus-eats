import uuid

from app.models.delivery import DeliveryPartner
from app.models.enums import RoleName
from app.repositories.delivery_partner_repository import DeliveryPartnerRepository
from app.repositories.user_repository import UserRepository


class DeliveryError(Exception):
    pass


class DeliveryPartnerService:
    def __init__(self, delivery_partner_repo: DeliveryPartnerRepository, user_repo: UserRepository):
        self.delivery_partner_repo = delivery_partner_repo
        self.user_repo = user_repo

    async def create_profile(self, user_id: uuid.UUID, vehicle_number: str | None) -> DeliveryPartner:
        user = await self.user_repo.get_with_role(user_id)
        if user is None:
            raise DeliveryError("user not found")
        if user.role.name != RoleName.DELIVERY.value:
            raise DeliveryError("user does not have the delivery role")
        if await self.delivery_partner_repo.get_by_user_id(user_id):
            raise DeliveryError("this user already has a delivery partner profile")

        partner = DeliveryPartner(id=uuid.uuid4(), user_id=user_id, vehicle_number=vehicle_number)
        await self.delivery_partner_repo.create(partner)
        partner.user = user
        return partner

    async def get_self(self, user_id: uuid.UUID) -> DeliveryPartner:
        partner = await self.delivery_partner_repo.get_by_user_id(user_id)
        if partner is None:
            raise DeliveryError("no delivery partner profile for this user — ask an admin to create one")
        return partner

    async def update_self(
        self,
        user_id: uuid.UUID,
        latitude: float | None,
        longitude: float | None,
        is_available: bool | None,
    ) -> DeliveryPartner:
        partner = await self.get_self(user_id)
        if latitude is not None:
            partner.current_latitude = latitude
        if longitude is not None:
            partner.current_longitude = longitude
        if is_available is not None:
            partner.is_available = is_available
        return partner
