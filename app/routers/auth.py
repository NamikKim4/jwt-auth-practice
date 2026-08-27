"""회원가입 / 로그인 / 토큰 재발급 / 로그아웃 / 내 정보 조회 라우트."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from config import ADMIN_SIGNUP_CODE, REFRESH_TOKEN_EXPIRE_DAYS
from models import SignupRequest, RefreshRequest
from repositories.users import get_user, create_user, count_users
from repositories import tokens as tokens_repo
from security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    get_current_user,
)

router = APIRouter()


def _issue_token_pair(username: str) -> dict:
    """액세스 토큰 + 리프레시 토큰을 한 쌍 새로 만들고, 리프레시 토큰은 해시로 DB에 저장해둔다."""
    access_token = create_access_token(data={"sub": username})
    refresh_token = create_refresh_token()
    expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    tokens_repo.store_refresh_token(username, hash_refresh_token(refresh_token), expires_at)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/signup")
def signup(payload: SignupRequest):
    if get_user(payload.username) is not None:
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디예요.")

    # "관리자로 가입"을 선택하고 코드를 넣은 경우: 코드가 맞아야만 관리자로 만들어줌.
    wants_admin = bool(payload.admin_code)
    if wants_admin and payload.admin_code != ADMIN_SIGNUP_CODE:
        raise HTTPException(status_code=400, detail="관리자 코드가 올바르지 않아요.")

    # 사이트에 아무도 없을 때(첫 번째 가입자)는 코드를 몰라도 자동으로 관리자가 됨
    # (관리자가 단 한 명도 없는 상황을 막기 위한 안전장치).
    is_first_user = count_users() == 0

    is_admin = wants_admin or is_first_user

    hashed = hash_password(payload.password)
    create_user(payload.username, hashed, is_admin=is_admin)
    return {"message": "회원가입 완료", "username": payload.username, "is_admin": is_admin}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
    if user is None or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 틀렸습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 로그인이라는, 어차피 자주 일어나는 이벤트에 슬쩍 끼워서 만료된 리프레시 토큰들을 청소한다.
    # (따로 백그라운드 작업을 만들 정도의 일은 아니라서 이렇게 처리했다)
    tokens_repo.delete_expired_tokens()
    return _issue_token_pair(user["username"])


@router.post("/refresh")
def refresh(payload: RefreshRequest):
    """리프레시 토큰으로 액세스 토큰을 새로 받는다.
    쓸 때마다 리프레시 토큰 자체도 새 걸로 교체(로테이션)해서, 하나의 리프레시 토큰은 딱 한 번만 쓸 수 있다.
    이미 폐기됐어야 할 옛날 토큰이 다시 들어오면 "누가 훔쳐서 같이 쓰고 있을 수도 있다"고 보고
    그 계정의 모든 로그인을 강제로 끊어버린다."""
    token_hash = hash_refresh_token(payload.refresh_token)
    record = tokens_repo.find_refresh_token(token_hash)

    if record is None:
        raise HTTPException(status_code=401, detail="로그인이 만료됐어요. 다시 로그인해주세요.")

    if record["revoked"]:
        tokens_repo.revoke_all_for_user(record["username"])
        raise HTTPException(
            status_code=401,
            detail="비정상적인 접근이 감지돼서 모든 로그인이 해제됐어요. 다시 로그인해주세요.",
        )

    if record["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=401, detail="로그인이 만료됐어요. 다시 로그인해주세요.")

    tokens_repo.revoke_refresh_token(token_hash)
    return _issue_token_pair(record["username"])


@router.post("/logout")
def logout(payload: RefreshRequest):
    """리프레시 토큰을 DB에서 무효화한다. 이미 없거나 지워진 토큰이어도 에러 없이 그냥 성공 처리한다
    (로그아웃은 "결과적으로 로그인 상태가 아니면" 되는 동작이라, 굳이 실패시킬 이유가 없다)."""
    tokens_repo.revoke_refresh_token(hash_refresh_token(payload.refresh_token))
    return {"message": "로그아웃 완료"}


@router.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "is_admin": current_user["is_admin"],
        "가입일": current_user["created_at"],
        "bio": current_user.get("bio"),
        "profile_image": current_user.get("profile_image"),
    }
