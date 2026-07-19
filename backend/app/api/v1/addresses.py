import uuid

from fastapi import APIRouter, HTTPException, status

from app.core.deps import AddressRepo, AddressSvc, CurrentUser, DbSession
from app.schemas.address import AddressCreateRequest, AddressResponse, AddressUpdateRequest
from app.services.address_service import AddressError

router = APIRouter(prefix="/addresses", tags=["addresses"])


@router.get("", response_model=list[AddressResponse])
async def list_addresses(current_user: CurrentUser, address_repo: AddressRepo) -> list[AddressResponse]:
    addresses = await address_repo.list_for_user(current_user.id)
    return [AddressResponse.model_validate(a) for a in addresses]


@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    payload: AddressCreateRequest, current_user: CurrentUser, db: DbSession, address_service: AddressSvc
) -> AddressResponse:
    address = await address_service.create_address(current_user.id, payload)
    await db.commit()
    return AddressResponse.model_validate(address)


@router.patch("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: uuid.UUID,
    payload: AddressUpdateRequest,
    current_user: CurrentUser,
    db: DbSession,
    address_service: AddressSvc,
) -> AddressResponse:
    try:
        address = await address_service.update_address(address_id, current_user.id, payload)
        await db.commit()
    except AddressError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return AddressResponse.model_validate(address)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: uuid.UUID, current_user: CurrentUser, db: DbSession, address_service: AddressSvc
) -> None:
    try:
        await address_service.delete_address(address_id, current_user.id)
        await db.commit()
    except AddressError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
