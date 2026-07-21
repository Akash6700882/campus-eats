import re

from pydantic import BaseModel, Field, field_validator

_TIME_PATTERN = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class AppSettingsResponse(BaseModel):
    restaurant_name: str
    gst_percent: float
    delivery_charge: float
    packing_charge: float
    business_hours_open: str
    business_hours_close: str

    @staticmethod
    def from_settings(settings) -> "AppSettingsResponse":
        return AppSettingsResponse(
            restaurant_name=settings.restaurant_name,
            gst_percent=float(settings.gst_percent),
            delivery_charge=float(settings.delivery_charge),
            packing_charge=float(settings.packing_charge),
            business_hours_open=settings.business_hours_open,
            business_hours_close=settings.business_hours_close,
        )


class AppSettingsUpdateRequest(BaseModel):
    restaurant_name: str = Field(min_length=1, max_length=120)
    gst_percent: float = Field(ge=0, le=100)
    delivery_charge: float = Field(ge=0)
    packing_charge: float = Field(ge=0)
    business_hours_open: str
    business_hours_close: str

    @field_validator("business_hours_open", "business_hours_close")
    @classmethod
    def validate_time(cls, value: str) -> str:
        if not _TIME_PATTERN.match(value):
            raise ValueError("must be in 24-hour HH:MM format")
        return value
