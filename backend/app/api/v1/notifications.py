import uuid

from fastapi import APIRouter, HTTPException, status

from app.core.deps import CurrentUser, DbSession, NotificationRepo
from app.schemas.notification import NotificationListResponse, NotificationResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    current_user: CurrentUser, notification_repo: NotificationRepo
) -> NotificationListResponse:
    items = await notification_repo.list_for_user(current_user.id)
    unread = await notification_repo.count_unread(current_user.id)
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in items], unread_count=unread
    )


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: uuid.UUID, current_user: CurrentUser, db: DbSession, notification_repo: NotificationRepo
) -> NotificationResponse:
    notification = await notification_repo.get(notification_id)
    if notification is None or notification.user_id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "notification not found")
    notification.is_read = True
    await db.commit()
    return NotificationResponse.model_validate(notification)


@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    current_user: CurrentUser, db: DbSession, notification_repo: NotificationRepo
) -> None:
    await notification_repo.mark_all_read(current_user.id)
    await db.commit()
