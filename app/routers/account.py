"""계정관리: 비밀번호 변경, 회원 탈퇴."""
from fastapi import APIRouter, Depends, HTTPException

from models import PasswordChangeRequest, AccountDeleteRequest
from repositories.users import get_user, update_password, delete_user
from security import verify_password, hash_password, get_current_user

router = APIRouter(prefix="/account", tags=["account"])


@router.put("/password")
def change_password(payload: PasswordChangeRequest, current_user: dict = Depends(get_current_user)):
    user = get_user(current_user["username"])
    if not verify_password(payload.current_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 일치하지 않아요.")
    if len(payload.new_password) < 4:
        raise HTTPException(status_code=400, detail="새 비밀번호는 4자 이상이어야 해요.")

    update_password(current_user["username"], hash_password(payload.new_password))
    return {"message": "비밀번호가 변경됐어요."}


@router.delete("")
def delete_account(payload: AccountDeleteRequest, current_user: dict = Depends(get_current_user)):
    user = get_user(current_user["username"])
    if not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않아요.")

    delete_user(current_user["username"])
    return {"message": "계정이 삭제됐어요. 그동안 작성하신 글/댓글/파일은 남아있어요."}
