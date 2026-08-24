"""posts 테이블에 직접 접근하는 함수들만 모아둔 파일 (SQL은 여기에만 있음)."""
from database import get_conn


def list_posts(q: str | None = None, sort: str = "latest"):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            order_by = "p.views DESC, p.id DESC" if sort == "views" else "p.id DESC"
            sql = f"""
                SELECT p.id, p.author, p.title, p.content, p.views, p.created_at,
                       COALESCE(c.comment_count, 0) AS comment_count
                FROM posts p
                LEFT JOIN (
                    SELECT post_id, COUNT(*) AS comment_count
                    FROM comments
                    GROUP BY post_id
                ) c ON c.post_id = p.id
                {{where}}
                ORDER BY {order_by};
            """
            params = ()
            where = ""
            if q:
                # 제목뿐 아니라 본문에서도 찾는다. ILIKE는 대소문자를 구분하지 않는 검색.
                where = "WHERE (p.title ILIKE %s OR p.content ILIKE %s)"
                params = (f"%{q}%", f"%{q}%")
            cur.execute(sql.format(where=where), params)
            rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "author": r[1],
                    "title": r[2],
                    "excerpt": (r[3][:80] + "…") if len(r[3]) > 80 else r[3],
                    "views": r[4],
                    "created_at": r[5],
                    "comment_count": r[6],
                }
                for r in rows
            ]
    finally:
        conn.close()


def get_post(post_id: int, increment_view: bool = True):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if increment_view:
                cur.execute("UPDATE posts SET views = views + 1 WHERE id = %s;", (post_id,))

            cur.execute(
                "SELECT id, author, title, content, views, created_at, updated_at FROM posts WHERE id = %s;",
                (post_id,),
            )
            row = cur.fetchone()
        conn.commit()
        if row is None:
            return None
        return {
            "id": row[0],
            "author": row[1],
            "title": row[2],
            "content": row[3],
            "views": row[4],
            "created_at": row[5],
            "updated_at": row[6],
        }
    finally:
        conn.close()


def list_posts_page(q: str | None = None, sort: str = "latest", page: int = 1, page_size: int = 10):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            order_by = "p.views DESC, p.id DESC" if sort == "views" else "p.id DESC"
            where = ""
            params = []
            if q:
                # 제목뿐 아니라 본문에서도 찾는다. ILIKE는 대소문자를 구분하지 않는 검색.
                where = "WHERE (p.title ILIKE %s OR p.content ILIKE %s)"
                params.append(f"%{q}%")
                params.append(f"%{q}%")

            count_sql = f"SELECT COUNT(*) FROM posts p {where};"
            cur.execute(count_sql, tuple(params))
            total = cur.fetchone()[0]

            offset = max(page - 1, 0) * page_size
            sql = f"""
                SELECT p.id, p.author, p.title, p.content, p.views, p.created_at,
                       COALESCE(c.comment_count, 0) AS comment_count
                FROM posts p
                LEFT JOIN (
                    SELECT post_id, COUNT(*) AS comment_count
                    FROM comments
                    GROUP BY post_id
                ) c ON c.post_id = p.id
                {where}
                ORDER BY {order_by}
                LIMIT %s OFFSET %s;
            """
            cur.execute(sql, tuple(params) + (page_size, offset))
            rows = cur.fetchall()
            items = [
                {
                    "id": r[0],
                    "author": r[1],
                    "title": r[2],
                    "excerpt": (r[3][:80] + "…") if len(r[3]) > 80 else r[3],
                    "views": r[4],
                    "created_at": r[5],
                    "comment_count": r[6],
                }
                for r in rows
            ]
            return {"items": items, "total": total, "page": page, "page_size": page_size}
    finally:
        conn.close()


def list_posts_by_author(author: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, views, created_at FROM posts WHERE author = %s ORDER BY id DESC;",
                (author,),
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "title": r[1], "views": r[2], "created_at": r[3]}
                for r in rows
            ]
    finally:
        conn.close()


def get_post_author(post_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT author FROM posts WHERE id = %s;", (post_id,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        conn.close()


def create_post(author: str, title: str, content: str) -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO posts (author, title, content) VALUES (%s, %s, %s) RETURNING id;",
                (author, title, content),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def update_post(post_id: int, title: str, content: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE posts SET title = %s, content = %s, updated_at = NOW() WHERE id = %s;",
                (title, content, post_id),
            )
        conn.commit()
    finally:
        conn.close()


def delete_post(post_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM posts WHERE id = %s;", (post_id,))
        conn.commit()
    finally:
        conn.close()


def list_all_posts_full():
    """PostgreSQL → MongoDB 백업용: 페이지네이션 없이 게시글 전체를 그대로 가져온다."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, author, title, content, views, created_at, updated_at FROM posts ORDER BY id ASC;"
            )
            rows = cur.fetchall()
            return [
                {
                    "id": r[0], "author": r[1], "title": r[2], "content": r[3],
                    "views": r[4], "created_at": r[5], "updated_at": r[6],
                }
                for r in rows
            ]
    finally:
        conn.close()


def count_posts() -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM posts;")
            return cur.fetchone()[0]
    finally:
        conn.close()
