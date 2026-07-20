from fastapi import APIRouter, Depends

from app.core.deps import DbSession, DeliveryZoneSvc, require_role
from app.models.enums import RoleName
from app.schemas.delivery_zone import DeliveryZoneResponse, DeliveryZoneUpdateRequest

router = APIRouter(tags=["delivery-zone"])

RequireAdmin = Depends(require_role(RoleName.ADMIN.value))


@router.get("/delivery-zone", response_model=DeliveryZoneResponse | None)
async def get_delivery_zone(delivery_zone_service: DeliveryZoneSvc) -> DeliveryZoneResponse | None:
    zone = await delivery_zone_service.get_active()
    return DeliveryZoneResponse.from_zone(zone) if zone else None


@router.put("/admin/delivery-zone", response_model=DeliveryZoneResponse, dependencies=[RequireAdmin])
async def update_delivery_zone(
    payload: DeliveryZoneUpdateRequest, db: DbSession, delivery_zone_service: DeliveryZoneSvc
) -> DeliveryZoneResponse:
    zone = await delivery_zone_service.upsert(payload.name, payload.polygon_geojson)
    await db.commit()
    return DeliveryZoneResponse.from_zone(zone)
