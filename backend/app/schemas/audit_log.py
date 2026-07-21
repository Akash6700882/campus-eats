import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: uuid.UUID
    actor_id: uuid.UUID
    actor_name: str
    action: str
    target_type: str
    target_id: str | None
    details: str | None
    created_at: datetime

    @staticmethod
    def from_log(log) -> "AuditLogResponse":
        return AuditLogResponse(
            id=log.id,
            actor_id=log.actor_id,
            actor_name=log.actor_name_snapshot,
            action=log.action,
            target_type=log.target_type,
            target_id=log.target_id,
            details=log.details,
            created_at=log.created_at,
        )
