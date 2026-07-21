import json
import uuid

from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:
    def __init__(self, audit_log_repo: AuditLogRepository):
        self.audit_log_repo = audit_log_repo

    async def record(
        self,
        actor: User,
        action: str,
        target_type: str,
        target_id: str | None = None,
        details: dict | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            id=uuid.uuid4(),
            actor_id=actor.id,
            actor_name_snapshot=actor.full_name,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=json.dumps(details) if details else None,
        )
        await self.audit_log_repo.create(entry)
        return entry

    async def list_recent(self, limit: int = 100, offset: int = 0) -> list[AuditLog]:
        return await self.audit_log_repo.list_recent(limit, offset)
