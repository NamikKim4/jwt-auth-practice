"""PostgreSQL의 게시글(posts)을 MongoDB로 백업(복사)하는 작업.
weather_fetcher.py와 구조가 똑같아요 — 다른 점은, 외부 API가 아니라 우리 자신의
PostgreSQL에서 데이터를 읽어서 MongoDB로 옮긴다는 것뿐이에요. 원본(PostgreSQL)은
전혀 건드리지 않고, 그대로 복사만 해요."""
import asyncio

from config import BACKUP_SYNC_INTERVAL_SECONDS
from repositories.posts import list_all_posts_full
from repositories.backup import sync_all_posts


def run_backup_sync() -> int:
    """지금 이 순간의 게시글 전체를 MongoDB로 백업한다. 몇 개를 백업했는지 돌려준다."""
    posts = list_all_posts_full()
    count = sync_all_posts(posts)
    print(f"[백업] 게시글 {count}개를 PostgreSQL → MongoDB로 백업 완료")
    return count


async def backup_background_loop():
    """서버가 켜져있는 동안 계속 돌면서, BACKUP_SYNC_INTERVAL_SECONDS(기본 1시간)마다
    한 번씩 게시글 전체를 다시 백업한다. 이미 백업된 글은 upsert라서 덮어쓰기만 되고
    중복 생성되지 않아요."""
    while True:
        try:
            await asyncio.to_thread(run_backup_sync)
        except Exception as e:
            print(f"[백업] 실패 (다음 주기에 재시도): {e}")
        await asyncio.sleep(BACKUP_SYNC_INTERVAL_SECONDS)
