"""MongoDB 연결. database.py(PostgreSQL)와는 완전히 별개의 데이터베이스예요.
회원/게시글/날씨 등 데이터 원본은 전부 PostgreSQL에 있고, 여기 MongoDB는 그 원본들을
주기적으로 복사해두는 백업 전용 용도로 써요(게시글은 1시간마다, 날씨는 10분마다).

원래는 날씨 데이터를 MongoDB에 바로 저장했었는데(스키마 없는 NoSQL을 한 번 다르게 써보고
싶어서), 나중에 "관리자가 백업 현황을 볼 수 있게 하자"는 걸 게시글 백업이랑 똑같은
패턴으로 만들다 보니, 아예 날씨도 게시글처럼 PostgreSQL을 원본으로 두는 구조로 통일했어요."""
from pymongo import MongoClient

from config import MONGO_URI

_client = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_posts_backup_collection():
    """backup_db 데이터베이스의 posts_backup 컬렉션. PostgreSQL의 posts 테이블을 그대로 복사해두는 곳."""
    return get_mongo_client()["backup_db"]["posts_backup"]


def get_weather_backup_collection():
    """backup_db 데이터베이스의 weather_backup 컬렉션. PostgreSQL의 weather_records 테이블을 그대로 복사해두는 곳."""
    return get_mongo_client()["backup_db"]["weather_backup"]
