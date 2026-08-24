"""알림 라우트. 내 알림만 보고/읽음 처리할 수 있다 (로그인 필수)."""
from fastapi import APIRouter, Depends, HTTPException, Query

from repositories import notifications as notifications_repo
from security import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def list_my_notifications(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    return notifications_repo.list_notifications(current_user["username"], limit=limit)


@router.get("/unread-count")
def get_unread_count(current_user: dict = Depends(get_current_user)):
    """종 아이콘의 빨간 배지 숫자. 화면이 주기적으로 이 값만 가볍게 물어본다."""
    return {"count": notifications_repo.count_unread(current_user["username"])}


@router.post("/read-all")
def read_all(current_user: dict = Depends(get_current_user)):
    updated = notifications_repo.mark_all_read(current_user["username"])
    return {"message": f"알림 {updated}개를 읽음 처리했어요.", "updated": updated}


@router.post("/{notification_id}/read")
def read_one(notification_id: int, current_user: dict = Depends(get_current_user)):
    ok = notifications_repo.mark_read(notification_id, current_user["username"])
    if not ok:
        raise HTTPException(status_code=404, detail="존재하지 않는 알림이에요.")
    return {"message": "읽음 처리했어요."}
