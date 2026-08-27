"""weather_backup 컬렉션(MongoDB)에 접근하는 함수들.
PostgreSQL의 weather_records 테이블을 그대로 복사해두는 백업 사본이에요. 원본은 건드리지 않아요.
(repositories/backup.py의 게시글 백업이랑 완전히 같은 구조 — 대상 테이블만 다르다.)"""
from datetime import datetime, timezone

from mongo import get_weather_backup_collection


def _upsert_one(collection, record: dict):
    """날씨 기록 하나를 백업 컬렉션에 저장한다. 이미 있으면 덮어쓰고, 없으면 새로 만든다.
    PostgreSQL의 id를 MongoDB 문서의 _id로 그대로 써서 upsert가 되게 한다."""
    doc = dict(record)
    doc["_id"] = doc.pop("id")
    doc["backed_up_at"] = datetime.now(timezone.utc)
    if isinstance(doc.get("recorded_at"), datetime):
        doc["recorded_at"] = doc["recorded_at"].isoformat()
    collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)


def sync_all_weather(records: list[dict]) -> int:
    """날씨 기록 전체를 한 번에 백업한다. 몇 개를 백업했는지 개수를 돌려준다."""
    collection = get_weather_backup_collection()
    for record in records:
        _upsert_one(collection, record)
    return len(records)


def list_backup_weather(limit: int = 50):
    cursor = get_weather_backup_collection().find().sort("_id", -1).limit(limit)
    results = []
    for doc in cursor:
        doc = dict(doc)
        doc["id"] = doc.pop("_id")
        results.append(doc)
    return results


def count_backup_weather() -> int:
    return get_weather_backup_collection().count_documents({})


def get_last_synced_at():
    """가장 최근에 백업된(갱신된) 문서의 backed_up_at 값을 돌려준다. 백업 기록이 하나도 없으면 None."""
    doc = get_weather_backup_collection().find_one(sort=[("backed_up_at", -1)])
    if doc is None:
        return None
    backed_up_at = doc.get("backed_up_at")
    return backed_up_at.isoformat() if isinstance(backed_up_at, datetime) else backed_up_at
