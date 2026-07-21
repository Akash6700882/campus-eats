from fastapi import APIRouter, Depends, Query

from app.core.deps import AuditLogSvc, require_role
from app.models.enums import RoleName
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(tags=["admin"])

RequireAdmin = Depends(require_role(RoleName.ADMIN.value))


@router.get("/admin/audit-logs", response_model=list[AuditLogResponse], dependencies=[RequireAdmin])
async def list_audit_logs(
    audit_log_service: AuditLogSvc,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0),
) -> list[AuditLogResponse]:
    logs = await audit_log_service.list_recent(limit=limit, offset=offset)
    return [AuditLogResponse.from_log(log) for log in logs]
