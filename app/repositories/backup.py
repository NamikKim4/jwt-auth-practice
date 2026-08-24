"""posts_backup 컬렉션(MongoDB)에 접근하는 함수들.
PostgreSQL의 posts 테이블을 그대로 복사해두는 백업 사본이에요. 원본은 건드리지 않아요."""
from datetime import datetime, timezone

from mongo import get_posts_backup_collection


def _upsert_one(collection, post: dict):
    """게시글 하나를 백업 컬렉션에 저장한다. 이미 있으면 덮어쓰고(갱신), 없으면 새로 만든다.
    PostgreSQL의 post id를 MongoDB 문서의 _id로 그대로 써서, 같은 글을 여러 번 백업해도
    중복 생성되지 않고 항상 최신 내용으로 갱신되게 했어요 (이런 방식을 "upsert"라고 불러요)."""
    doc = dict(post)
    doc["_id"] = doc.pop("id")
    doc["backed_up_at"] = datetime.now(timezone.utc)
    for key in ("created_at", "updated_at"):
        if isinstance(doc.get(key), datetime):
            doc[key] = doc[key].isoformat()
    collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)


def sync_all_posts(posts: list[dict]) -> int:
    """게시글 목록 전체를 한 번에 백업한다. 몇 개를 백업했는지 개수를 돌려준다."""
    collection = get_posts_backup_collection()
    for post in posts:
        _upsert_one(collection, post)
    return len(posts)


def list_backup_posts(limit: int = 50):
    cursor = get_posts_backup_collection().find().sort("_id", -1).limit(limit)
    results = []
    for doc in cursor:
        doc = dict(doc)
        doc["id"] = doc.pop("_id")
        results.append(doc)
    return results


def count_backup_posts() -> int:
    return get_posts_backup_collection().count_documents({})


def get_last_synced_at():
    """가장 최근에 백업된(갱신된) 문서의 backed_up_at 값을 돌려준다. 백업 기록이 하나도 없으면 None."""
    doc = get_posts_backup_collection().find_one(sort=[("backed_up_at", -1)])
    if doc is None:
        return None
    backed_up_at = doc.get("backed_up_at")
    return backed_up_at.isoformat() if isinstance(backed_up_at, datetime) else backed_up_at
