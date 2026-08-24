"""내 활동: 내가 쓴 글 / 댓글 / 올린 파일을 한 번에 모아 보여준다."""
from fastapi import APIRouter, Depends

from repositories.posts import list_posts_by_author
from repositories.comments import list_comments_by_author
from repositories.files import list_files_by_uploader
from security import get_current_user

router = APIRouter(prefix="/api/me", tags=["activity"])


@router.get("/activity")
def my_activity(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    return {
        "posts": list_posts_by_author(username),
        "comments": list_comments_by_author(username),
        "files": list_files_by_uploader(username),
    }
