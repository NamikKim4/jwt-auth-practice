"""PostgreSQL의 날씨 기록(weather_records)을 MongoDB로 백업(복사)하는 작업.
backup_sync.py(게시글 백업)와 구조가 완전히 똑같고, 대상 테이블만 날씨로 바뀐 버전이에요.
날씨는 30분마다 계속 새로 쌓이는 데이터라, 게시글(1시간)보다 훨씬 자주(기본 10분마다) 백업해요."""
import asyncio

from config import WEATHER_BACKUP_INTERVAL_SECONDS
from repositories.weather import list_all_weather_full
from repositories.weather_backup import sync_all_weather


def run_weather_backup_sync() -> int:
    """지금 이 순간의 날씨 기록 전체를 MongoDB로 백업한다. 몇 개를 백업했는지 돌려준다."""
    records = list_all_weather_full()
    count = sync_all_weather(records)
    print(f"[날씨 백업] 날씨 기록 {count}개를 PostgreSQL → MongoDB로 백업 완료")
    return count


async def weather_backup_background_loop():
    """서버가 켜져있는 동안 계속 돌면서, WEATHER_BACKUP_INTERVAL_SECONDS(기본 10분)마다
    한 번씩 날씨 기록 전체를 다시 백업한다. 이미 백업된 기록은 upsert라서 덮어쓰기만 되고
    중복 생성되지 않는다."""
    while True:
        try:
            await asyncio.to_thread(run_weather_backup_sync)
        except Exception as e:
            print(f"[날씨 백업] 실패 (다음 주기에 재시도): {e}")
        await asyncio.sleep(WEATHER_BACKUP_INTERVAL_SECONDS)
