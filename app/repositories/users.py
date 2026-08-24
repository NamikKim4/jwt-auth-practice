"""users 테이블에 직접 접근하는 함수들만 모아둔 파일 (SQL은 여기에만 있음)."""
from database import get_conn


def get_user(username: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT username, hashed_password, is_admin, created_at, profile_image, bio
                FROM users WHERE username = %s;
                """,
                (username,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return {
                "username": row[0],
                "hashed_password": row[1],
                "is_admin": row[2],
                "created_at": row[3],
                "profile_image": row[4],
                "bio": row[5],
            }
    finally:
        conn.close()


def create_user(username: str, hashed_password: str, is_admin: bool = False):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, hashed_password, is_admin) VALUES (%s, %s, %s);",
                (username, hashed_password, is_admin),
            )
        conn.commit()
    finally:
        conn.close()


def update_profile(username: str, bio: str | None, profile_image: str | None):
    """자기소개/프로필 사진을 통째로 덮어쓴다. None을 넘기면 그 값은 지워진다(=비워짐)."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET bio = %s, profile_image = %s WHERE username = %s;",
                (bio, profile_image, username),
            )
        conn.commit()
    finally:
        conn.close()


def update_password(username: str, new_hashed_password: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET hashed_password = %s WHERE username = %s;",
                (new_hashed_password, username),
            )
        conn.commit()
    finally:
        conn.close()


def delete_user(username: str):
    """계정만 삭제한다. 이미 작성한 글/댓글/파일은 남겨둔다 (작성자 이름은 그대로 유지됨)."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE username = %s;", (username,))
        conn.commit()
    finally:
        conn.close()


def count_users() -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users;")
            return cur.fetchone()[0]
    finally:
        conn.close()


def list_users_with_stats():
    """관리자 화면용: 회원 목록 + 각자 작성한 글/파일 개수를 같이 가져온다."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT u.username, u.is_admin, u.created_at,
                       COALESCE(p.cnt, 0) AS post_count,
                       COALESCE(f.cnt, 0) AS file_count
                FROM users u
                LEFT JOIN (
                    SELECT author, COUNT(*) AS cnt FROM posts GROUP BY author
                ) p ON p.author = u.username
                LEFT JOIN (
                    SELECT uploader, COUNT(*) AS cnt FROM files GROUP BY uploader
                ) f ON f.uploader = u.username
                ORDER BY u.id ASC;
            """)
            rows = cur.fetchall()
            return [
                {
                    "username": r[0],
                    "is_admin": r[1],
                    "created_at": r[2],
                    "post_count": r[3],
                    "file_count": r[4],
                }
                for r in rows
            ]
    finally:
        conn.close()
