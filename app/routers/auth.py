"""회원가입 / 로그인 / 내 정보 조회 라우트."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from config import ADMIN_SIGNUP_CODE
from models import SignupRequest
from repositories.users import get_user, create_user, count_users
from security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()


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

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return {
        "username": current_user["username"],
        "is_admin": current_user["is_admin"],
        "가입일": current_user["created_at"],
        "bio": current_user.get("bio"),
        "profile_image": current_user.get("profile_image"),
    }
