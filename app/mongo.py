"""MongoDB 연결. database.py(PostgreSQL)와는 완전히 별개의 데이터베이스예요.
회원/게시글/파일 등은 관계형 데이터라 원래는 PostgreSQL을 쓰지만, 여기서는
(1) 외부 API에서 그대로 받아오는 날씨 데이터, (2) PostgreSQL 게시글의 백업 사본,
이 두 가지 용도로 MongoDB(NoSQL, 문서형 DB)를 같이 써봤어요."""
from pymongo import MongoClient

from config import MONGO_URI

_client = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_weather_collection():
    """weather_db 데이터베이스의 weather_records 컬렉션(=SQL의 테이블과 비슷한 개념)."""
    return get_mongo_client()["weather_db"]["weather_records"]


def get_posts_backup_collection():
    """backup_db 데이터베이스의 posts_backup 컬렉션. PostgreSQL의 posts 테이블을 그대로 복사해두는 곳."""
    return get_mongo_client()["backup_db"]["posts_backup"]
