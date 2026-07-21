from fastapi import APIRouter, Depends

from app.core.deps import AppSettingsSvc, AuditLogSvc, CurrentUser, DbSession, require_role
from app.models.enums import RoleName
from app.schemas.app_settings import AppSettingsResponse, AppSettingsUpdateRequest

router = APIRouter(tags=["settings"])

RequireAdmin = Depends(require_role(RoleName.ADMIN.value))


@router.get("/settings", response_model=AppSettingsResponse)
async def get_app_settings(app_settings_service: AppSettingsSvc) -> AppSettingsResponse:
    settings = await app_settings_service.get()
    return AppSettingsResponse.from_settings(settings)


@router.put("/admin/settings", response_model=AppSettingsResponse, dependencies=[RequireAdmin])
async def update_app_settings(
    payload: AppSettingsUpdateRequest,
    current_user: CurrentUser,
    db: DbSession,
    app_settings_service: AppSettingsSvc,
    audit_log_service: AuditLogSvc,
) -> AppSettingsResponse:
    settings = await app_settings_service.update(
        payload.restaurant_name,
        payload.gst_percent,
        payload.delivery_charge,
        payload.packing_charge,
        payload.business_hours_open,
        payload.business_hours_close,
    )
    await audit_log_service.record(current_user, "settings.update", "app_settings", str(settings.id))
    await db.commit()
    return AppSettingsResponse.from_settings(settings)
