import uuid

from app.models.address import Address
from app.repositories.address_repository import AddressRepository
from app.schemas.address import AddressCreateRequest, AddressUpdateRequest


class AddressError(Exception):
    pass


class AddressService:
    def __init__(self, address_repo: AddressRepository):
        self.address_repo = address_repo

    async def _unset_other_defaults(self, user_id: uuid.UUID) -> None:
        for existing in await self.address_repo.list_for_user(user_id):
            existing.is_default = False

    async def create_address(self, user_id: uuid.UUID, payload: AddressCreateRequest) -> Address:
        if payload.is_default:
            await self._unset_other_defaults(user_id)

        address = Address(
            id=uuid.uuid4(),
            user_id=user_id,
            label=payload.label,
            building=payload.building,
            hostel=payload.hostel,
            block=payload.block,
            room_number=payload.room_number,
            department=payload.department,
            notes=payload.notes,
            latitude=payload.latitude,
            longitude=payload.longitude,
            is_default=payload.is_default,
        )
        return await self.address_repo.create(address)

    async def update_address(
        self, address_id: uuid.UUID, user_id: uuid.UUID, payload: AddressUpdateRequest
    ) -> Address:
        address = await self.address_repo.get_for_user(address_id, user_id)
        if address is None:
            raise AddressError("address not found")

        data = payload.model_dump(exclude_unset=True)
        if data.get("is_default"):
            await self._unset_other_defaults(user_id)

        for field, value in data.items():
            setattr(address, field, value)
        return address

    async def delete_address(self, address_id: uuid.UUID, user_id: uuid.UUID) -> None:
        address = await self.address_repo.get_for_user(address_id, user_id)
        if address is None:
            raise AddressError("address not found")
        await self.address_repo.delete(address)
