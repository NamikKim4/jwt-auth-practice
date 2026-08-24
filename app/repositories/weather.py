"""weather_records 컬렉션(MongoDB)에 접근하는 함수들.
다른 repositories/*.py 파일들은 PostgreSQL(SQL)을 쓰지만, 여기만 MongoDB 쿼리를 써요."""
from datetime import datetime, timezone

from mongo import get_weather_collection


def _serialize(doc: dict) -> dict:
    """MongoDB 문서를 JSON으로 내려줄 수 있는 모양으로 바꾼다 (_id → id 문자열, datetime → 문자열)."""
    doc = dict(doc)
    doc["id"] = str(doc.pop("_id"))
    recorded_at = doc.get("recorded_at")
    if isinstance(recorded_at, datetime):
        doc["recorded_at"] = recorded_at.isoformat()
    return doc


def list_weather(limit: int = 30):
    cursor = get_weather_collection().find().sort("recorded_at", -1).limit(limit)
    return [_serialize(doc) for doc in cursor]


def list_weather_page(page: int = 1, page_size: int = 10):
    """'이전 기록' 화면에서 쓰는 페이지네이션 버전. 게시판(list_posts_page)과 같은 모양으로 돌려준다."""
    total = count_weather()
    skip = max(page - 1, 0) * page_size
    cursor = get_weather_collection().find().sort("recorded_at", -1).skip(skip).limit(page_size)
    items = [_serialize(doc) for doc in cursor]
    return {"items": items, "total": total, "page": page, "page_size": page_size}


def get_latest_weather():
    doc = get_weather_collection().find_one(sort=[("recorded_at", -1)])
    return _serialize(doc) if doc else None


def create_manual_weather(
    username: str,
    city: str,
    temperature_c: float,
    description: str,
    humidity_percent: float | None,
    wind_speed_ms: float | None,
) -> str:
    doc = {
        "city": city,
        "temperature_c": temperature_c,
        "humidity_percent": humidity_percent,
        "wind_speed_ms": wind_speed_ms,
        "description": description,
        "emoji": "📝",
        "source": "manual",
        "created_by": username,
        "recorded_at": datetime.now(timezone.utc),
    }
    result = get_weather_collection().insert_one(doc)
    return str(result.inserted_id)


def count_weather() -> int:
    return get_weather_collection().count_documents({})
