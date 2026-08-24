"""날씨: 외부 API(Open-Meteo)에서 30분마다 자동으로 가져오고, 사람이 직접 손으로도 남길 수 있는 기록.
데이터는 PostgreSQL이 아니라 별도의 MongoDB(weather_db)에 저장돼요."""
from fastapi import APIRouter, Depends, HTTPException

from models import WeatherCreate
from repositories import weather as weather_repo
from security import get_current_user

router = APIRouter(prefix="/api/weather", tags=["weather"])


@router.get("")
def list_weather(limit: int = 30):
    return weather_repo.list_weather(limit=limit)


@router.get("/latest")
def get_latest_weather():
    latest = weather_repo.get_latest_weather()
    if latest is None:
        raise HTTPException(status_code=404, detail="아직 수집된 날씨 데이터가 없어요.")
    return latest


@router.post("")
def create_manual_weather(payload: WeatherCreate, current_user: dict = Depends(get_current_user)):
    new_id = weather_repo.create_manual_weather(
        current_user["username"],
        payload.city,
        payload.temperature_c,
        payload.description,
        payload.humidity_percent,
        payload.wind_speed_ms,
    )
    return {"id": new_id, "message": "등록됐어요."}
