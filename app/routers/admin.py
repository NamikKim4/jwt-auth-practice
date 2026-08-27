"""관리자 전용: 회원 목록/삭제, 사이트 전체 현황."""
from fastapi import APIRouter, Depends, HTTPException

from repositories.users import get_user, delete_user, count_users, list_users_with_stats
from repositories.posts import count_posts
from repositories.files import count_files
from repositories.products import count_products
from repositories.weather import count_weather
from repositories import tokens as tokens_repo
from security import require_admin

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/stats")
def get_stats(current_admin: dict = Depends(require_admin)):
    return {
        "users": count_users(),
        "posts": count_posts(),
        "files": count_files(),
        "products": count_products(),
        "weather": count_weather(),
    }


@router.get("/users")
def list_users(current_admin: dict = Depends(require_admin)):
    return list_users_with_stats()


@router.delete("/users/{username}")
def delete_user_route(username: str, current_admin: dict = Depends(require_admin)):
    if username == current_admin["username"]:
        raise HTTPException(status_code=400, detail="본인 계정은 여기서 삭제할 수 없어요. 계정관리에서 탈퇴해주세요.")
    if get_user(username) is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 계정이에요.")

    delete_user(username)
    tokens_repo.revoke_all_for_user(username)
    return {"message": f"{username} 계정을 삭제했어요."}
