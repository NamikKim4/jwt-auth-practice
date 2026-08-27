"""계정관리: 비밀번호 변경, 회원 탈퇴, 프로필(사진/자기소개) 수정."""
from fastapi import APIRouter, Depends, HTTPException

from models import PasswordChangeRequest, AccountDeleteRequest, ProfileUpdate
from repositories.users import get_user, update_password, delete_user, update_profile
from repositories import tokens as tokens_repo
from security import verify_password, hash_password, get_current_user

router = APIRouter(prefix="/account", tags=["account"])

# 프로필 사진은 DB에 base64 문자열로 저장하기 때문에 너무 크면 DB가 무거워진다.
# 화면(JS)에서는 원본 파일 2MB로 막아두는데, base64로 인코딩하면 문자열이 원본보다 커지므로
# 여기서는 그 여유분까지 감안해서 조금 더 넉넉하게(3MB) 잡아둔다.
MAX_PROFILE_IMAGE_LEN = 3 * 1024 * 1024


@router.put("/profile")
def update_profile_route(payload: ProfileUpdate, current_user: dict = Depends(get_current_user)):
    bio = (payload.bio or "").strip() or None
    if bio and len(bio) > 150:
        raise HTTPException(status_code=400, detail="자기소개는 150자 이내로 적어주세요.")
    if payload.profile_image and len(payload.profile_image) > MAX_PROFILE_IMAGE_LEN:
        raise HTTPException(status_code=400, detail="프로필 사진 용량이 너무 커요.")

    update_profile(current_user["username"], bio, payload.profile_image)
    return {"message": "프로필이 저장됐어요."}


@router.put("/password")
def change_password(payload: PasswordChangeRequest, current_user: dict = Depends(get_current_user)):
    user = get_user(current_user["username"])
    if not verify_password(payload.current_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 일치하지 않아요.")
    if len(payload.new_password) < 4:
        raise HTTPException(status_code=400, detail="새 비밀번호는 4자 이상이어야 해요.")

    update_password(current_user["username"], hash_password(payload.new_password))
    # 비밀번호를 바꿨다면 그 전에 로그인해둔 리프레시 토큰들은 전부 무효화한다.
    # (다른 기기에 남아있던 로그인이, 비밀번호가 바뀐 뒤에도 계속 살아있으면 이상하니까)
    tokens_repo.revoke_all_for_user(current_user["username"])
    return {"message": "비밀번호가 변경됐어요. 다른 기기에 남아있던 로그인은 모두 해제됐어요."}


@router.delete("")
def delete_account(payload: AccountDeleteRequest, current_user: dict = Depends(get_current_user)):
    user = get_user(current_user["username"])
    if not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않아요.")

    delete_user(current_user["username"])
    tokens_repo.revoke_all_for_user(current_user["username"])
    return {"message": "계정이 삭제됐어요. 그동안 작성하신 글/댓글/파일은 남아있어요."}
