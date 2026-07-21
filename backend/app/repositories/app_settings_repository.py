from sqlalchemy import select

from app.models.app_settings import AppSettings
from app.repositories.base import BaseRepository


class AppSettingsRepository(BaseRepository[AppSettings]):
    model = AppSettings

    async def get_singleton(self) -> AppSettings | None:
        result = await self.session.execute(select(AppSettings).limit(1))
        return result.scalar_one_or_none()
