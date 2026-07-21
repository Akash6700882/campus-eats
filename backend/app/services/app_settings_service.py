import uuid

from app.models.app_settings import AppSettings
from app.repositories.app_settings_repository import AppSettingsRepository


class AppSettingsService:
    def __init__(self, app_settings_repo: AppSettingsRepository):
        self.app_settings_repo = app_settings_repo

    async def get(self) -> AppSettings:
        settings = await self.app_settings_repo.get_singleton()
        if settings is None:
            settings = AppSettings(id=uuid.uuid4())
            await self.app_settings_repo.create(settings)
        return settings

    async def update(
        self,
        restaurant_name: str,
        gst_percent: float,
        delivery_charge: float,
        packing_charge: float,
        business_hours_open: str,
        business_hours_close: str,
    ) -> AppSettings:
        settings = await self.get()
        settings.restaurant_name = restaurant_name
        settings.gst_percent = gst_percent
        settings.delivery_charge = delivery_charge
        settings.packing_charge = packing_charge
        settings.business_hours_open = business_hours_open
        settings.business_hours_close = business_hours_close
        return settings
