import uuid

from app.models.delivery import DeliveryZone
from app.repositories.delivery_zone_repository import DeliveryZoneRepository


class DeliveryZoneService:
    def __init__(self, delivery_zone_repo: DeliveryZoneRepository):
        self.delivery_zone_repo = delivery_zone_repo

    async def get_active(self) -> DeliveryZone | None:
        return await self.delivery_zone_repo.get_first_active()

    async def upsert(self, name: str, polygon_geojson: str) -> DeliveryZone:
        zone = await self.delivery_zone_repo.get_first_active()
        if zone is None:
            zone = DeliveryZone(id=uuid.uuid4(), name=name, polygon_geojson=polygon_geojson, is_active=True)
            await self.delivery_zone_repo.create(zone)
        else:
            zone.name = name
            zone.polygon_geojson = polygon_geojson
        return zone
