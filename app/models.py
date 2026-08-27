"""요청/응답 바디의 모양을 정의하는 Pydantic 모델들."""
from pydantic import BaseModel


class SignupRequest(BaseModel):
    username: str
    password: str
    admin_code: str | None = None  # "관리자로 가입"을 선택했을 때만 값이 들어옴


class RefreshRequest(BaseModel):
    refresh_token: str


class PostCreate(BaseModel):
    title: str
    content: str
    category: str = "자유"


class PostUpdate(BaseModel):
    title: str
    content: str
    category: str = "자유"


class CommentCreate(BaseModel):
    content: str


class ProfileUpdate(BaseModel):
    bio: str | None = None
    profile_image: str | None = None  # data:image/...;base64,... 형태. null이면 사진 없앰.


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class AccountDeleteRequest(BaseModel):
    password: str


class WeatherCreate(BaseModel):
    city: str
    temperature_c: float
    description: str
    humidity_percent: float | None = None
    wind_speed_ms: float | None = None


class ProductCreate(BaseModel):
    name: str
    description: str
    image_data: str  # data:image/...;base64,... 형태의 문자열


class ProductUpdate(BaseModel):
    name: str
    description: str
    image_data: str | None = None  # 안 보내면 기존 이미지 유지


class GameScoreSubmit(BaseModel):
    game: str  # "baseball" | "mole" | "simon" | "reaction"
    score: int
