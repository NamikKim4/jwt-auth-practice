"""관리자 전용: PostgreSQL 날씨 기록을 MongoDB로 백업하는 기능의 API.
routers/backup.py(게시글 백업)와 완전히 같은 구조예요."""
from fastapi import APIRouter, Depends

from weather_backup_sync import run_weather_backup_sync
from repositories.weather import count_weather
from repositories.weather_backup import count_backup_weather, get_last_synced_at, list_backup_weather
from security import require_admin

router = APIRouter(prefix="/api/admin/weather-backup", tags=["weather-backup"])


@router.get("/status")
def get_weather_backup_status(current_admin: dict = Depends(require_admin)):
    return {
        "postgres_weather_count": count_weather(),
        "backed_up_count": count_backup_weather(),
        "last_synced_at": get_last_synced_at(),
    }


@router.get("/records")
def list_backup_weather_route(current_admin: dict = Depends(require_admin)):
    """MongoDB에 백업된 날씨 기록 목록 (화면에 눈으로 보여주기 위한 API)."""
    return list_backup_weather()


@router.post("/run")
def trigger_weather_backup_now(current_admin: dict = Depends(require_admin)):
    count = run_weather_backup_sync()
    return {"message": f"날씨 기록 {count}개를 MongoDB로 백업했어요.", "backed_up_count": count}
