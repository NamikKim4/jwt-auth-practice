"""관리자 전용: PostgreSQL 게시글을 MongoDB로 백업하는 기능의 API."""
from fastapi import APIRouter, Depends

from backup_sync import run_backup_sync
from repositories.posts import count_posts
from repositories.backup import count_backup_posts, get_last_synced_at, list_backup_posts
from security import require_admin

router = APIRouter(prefix="/api/admin/backup", tags=["backup"])


@router.get("/status")
def get_backup_status(current_admin: dict = Depends(require_admin)):
    return {
        "postgres_post_count": count_posts(),
        "backed_up_count": count_backup_posts(),
        "last_synced_at": get_last_synced_at(),
    }


@router.get("/posts")
def list_backup_posts_route(current_admin: dict = Depends(require_admin)):
    """MongoDB에 백업된 게시글 목록 (화면에 눈으로 보여주기 위한 API)."""
    return list_backup_posts()


@router.post("/run")
def trigger_backup_now(current_admin: dict = Depends(require_admin)):
    count = run_backup_sync()
    return {"message": f"게시글 {count}개를 MongoDB로 백업했어요.", "backed_up_count": count}
