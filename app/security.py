"""비밀번호 해시, JWT 토큰 생성/검증, '로그인 필수' 의존성(get_current_user)을 담당하는 파일."""
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from repositories.users import get_user

# 비밀번호를 bcrypt 방식으로 해시(암호화)하기 위한 도구
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# /docs 페이지에서 "Authorize" 버튼이 뜨게 해주는 설정. 토큰은 /login에서 발급됨.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="로그인이 필요하거나 토큰이 유효하지 않습니다.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme)):
    """이 함수를 Depends()로 붙인 라우트는 유효한 토큰이 있어야만 접근할 수 있다."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """이 함수를 Depends()로 붙인 라우트는 관리자 계정만 접근할 수 있다."""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="관리자만 접근할 수 있어요.")
    return current_user
