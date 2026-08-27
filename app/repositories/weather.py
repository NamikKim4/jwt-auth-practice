"""weather_records 테이블에 직접 접근하는 함수들만 모아둔 파일 (SQL은 여기에만 있음).

원래는 MongoDB에 바로 저장했었는데, 게시글이랑 똑같이 "PostgreSQL을 원본으로 두고
주기적으로 MongoDB에 백업"하는 구조로 바꿨다. MongoDB 쪽 백업 코드는 weather_backup.py에 있다."""
from database import get_conn

_SELECT_COLUMNS = "id, city, temperature_c, humidity_percent, wind_speed_ms, description, emoji, source, created_by, recorded_at"


def _row_to_dict(row: tuple) -> dict:
    return {
        "id": row[0],
        "city": row[1],
        "temperature_c": row[2],
        "humidity_percent": row[3],
        "wind_speed_ms": row[4],
        "description": row[5],
        "emoji": row[6],
        "source": row[7],
        "created_by": row[8],
        "recorded_at": row[9],
    }


def list_weather(limit: int = 30):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT {_SELECT_COLUMNS} FROM weather_records ORDER BY recorded_at DESC LIMIT %s;",
                (limit,),
            )
            return [_row_to_dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def list_weather_page(page: int = 1, page_size: int = 10):
    """'이전 기록' 화면에서 쓰는 페이지네이션 버전. 게시판(list_posts_page)과 같은 모양으로 돌려준다."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM weather_records;")
            total = cur.fetchone()[0]

            offset = max(page - 1, 0) * page_size
            cur.execute(
                f"SELECT {_SELECT_COLUMNS} FROM weather_records ORDER BY recorded_at DESC LIMIT %s OFFSET %s;",
                (page_size, offset),
            )
            items = [_row_to_dict(r) for r in cur.fetchall()]
            return {"items": items, "total": total, "page": page, "page_size": page_size}
    finally:
        conn.close()


def get_latest_weather():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {_SELECT_COLUMNS} FROM weather_records ORDER BY recorded_at DESC LIMIT 1;")
            row = cur.fetchone()
            return _row_to_dict(row) if row else None
    finally:
        conn.close()


def _insert(city, temperature_c, humidity_percent, wind_speed_ms, description, emoji, source, created_by) -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO weather_records
                    (city, temperature_c, humidity_percent, wind_speed_ms, description, emoji, source, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (city, temperature_c, humidity_percent, wind_speed_ms, description, emoji, source, created_by),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def create_auto_weather(city: str, temperature_c: float, humidity_percent, wind_speed_ms, description: str, emoji: str) -> int:
    """weather_fetcher.py의 자동 수집 루프에서 호출한다."""
    return _insert(city, temperature_c, humidity_percent, wind_speed_ms, description, emoji, "auto", "자동 수집")


def create_manual_weather(
    username: str,
    city: str,
    temperature_c: float,
    description: str,
    humidity_percent: float | None,
    wind_speed_ms: float | None,
) -> int:
    return _insert(city, temperature_c, humidity_percent, wind_speed_ms, description, "📝", "manual", username)


def count_weather() -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM weather_records;")
            return cur.fetchone()[0]
    finally:
        conn.close()


def list_all_weather_full():
    """PostgreSQL → MongoDB 백업용: 페이지네이션 없이 날씨 기록 전체를 그대로 가져온다."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {_SELECT_COLUMNS} FROM weather_records ORDER BY id ASC;")
            return [_row_to_dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
