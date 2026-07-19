import uuid

from pydantic import BaseModel, Field


class AddressCreateRequest(BaseModel):
    label: str = Field(default="Hostel", max_length=50)
    building: str | None = None
    hostel: str | None = None
    block: str | None = None
    room_number: str | None = None
    department: str | None = None
    notes: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    is_default: bool = False


class AddressUpdateRequest(BaseModel):
    label: str | None = Field(default=None, max_length=50)
    building: str | None = None
    hostel: str | None = None
    block: str | None = None
    room_number: str | None = None
    department: str | None = None
    notes: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    is_default: bool | None = None


class AddressResponse(BaseModel):
    id: uuid.UUID
    label: str
    building: str | None
    hostel: str | None
    block: str | None
    room_number: str | None
    department: str | None
    notes: str | None
    latitude: float
    longitude: float
    is_default: bool

    model_config = {"from_attributes": True}
