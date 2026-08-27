"""posts 테이블에 직접 접근하는 함수들만 모아둔 파일 (SQL은 여기에만 있음)."""
from database import get_conn

# 글쓰기 화면에서 고를 수 있는 카테고리들. "공지"는 관리자만 고를 수 있게 라우터에서 따로 막는다.
POST_CATEGORIES = ["자유", "질문", "정보", "기타", "공지"]
ADMIN_ONLY_CATEGORY = "공지"


def _category_filter(category: str | None):
    """카테고리 필터 조건 하나를 (SQL 조각, 파라미터) 형태로 돌려준다. 필터가 없으면 빈 조각."""
    if category and category in POST_CATEGORIES:
        return "p.category = %s", category
    return None, None


def list_posts(q: str | None = None, sort: str = "latest", category: str | None = None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            order_by = "p.views DESC, p.id DESC" if sort == "views" else "p.id DESC"
            sql = f"""
                SELECT p.id, p.author, p.title, p.content, p.views, p.created_at, p.category,
                       COALESCE(c.comment_count, 0) AS comment_count,
                       COALESCE(rx.reaction_count, 0) AS reaction_count
                FROM posts p
                LEFT JOIN (
                    SELECT post_id, COUNT(*) AS comment_count
                    FROM comments
                    GROUP BY post_id
                ) c ON c.post_id = p.id
                LEFT JOIN (
                    SELECT post_id, COUNT(*) AS reaction_count
                    FROM post_reactions
                    GROUP BY post_id
                ) rx ON rx.post_id = p.id
                {{where}}
                ORDER BY {order_by};
            """
            conditions = []
            params = []
            if q:
                # 제목뿐 아니라 본문에서도 찾는다. ILIKE는 대소문자를 구분하지 않는 검색.
                conditions.append("(p.title ILIKE %s OR p.content ILIKE %s)")
                params.extend([f"%{q}%", f"%{q}%"])
            cat_cond, cat_param = _category_filter(category)
            if cat_cond:
                conditions.append(cat_cond)
                params.append(cat_param)
            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            cur.execute(sql.format(where=where), tuple(params))
            rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "author": r[1],
                    "title": r[2],
                    "excerpt": (r[3][:80] + "…") if len(r[3]) > 80 else r[3],
                    "views": r[4],
                    "created_at": r[5],
                    "category": r[6],
                    "comment_count": r[7],
                    "reaction_count": r[8],
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
                "SELECT id, author, title, content, views, created_at, updated_at, category FROM posts WHERE id = %s;",
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
            "category": row[7],
        }
    finally:
        conn.close()


def list_posts_page(q: str | None = None, sort: str = "latest", page: int = 1, page_size: int = 10, category: str | None = None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            order_by = "p.views DESC, p.id DESC" if sort == "views" else "p.id DESC"
            conditions = []
            params = []
            if q:
                # 제목뿐 아니라 본문에서도 찾는다. ILIKE는 대소문자를 구분하지 않는 검색.
                conditions.append("(p.title ILIKE %s OR p.content ILIKE %s)")
                params.extend([f"%{q}%", f"%{q}%"])
            cat_cond, cat_param = _category_filter(category)
            if cat_cond:
                conditions.append(cat_cond)
                params.append(cat_param)
            where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

            count_sql = f"SELECT COUNT(*) FROM posts p {where};"
            cur.execute(count_sql, tuple(params))
            total = cur.fetchone()[0]

            offset = max(page - 1, 0) * page_size
            sql = f"""
                SELECT p.id, p.author, p.title, p.content, p.views, p.created_at, p.category,
                       COALESCE(c.comment_count, 0) AS comment_count,
                       COALESCE(rx.reaction_count, 0) AS reaction_count
                FROM posts p
                LEFT JOIN (
                    SELECT post_id, COUNT(*) AS comment_count
                    FROM comments
                    GROUP BY post_id
                ) c ON c.post_id = p.id
                LEFT JOIN (
                    SELECT post_id, COUNT(*) AS reaction_count
                    FROM post_reactions
                    GROUP BY post_id
                ) rx ON rx.post_id = p.id
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
                    "category": r[6],
                    "comment_count": r[7],
                    "reaction_count": r[8],
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


def create_post(author: str, title: str, content: str, category: str = "자유") -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO posts (author, title, content, category) VALUES (%s, %s, %s, %s) RETURNING id;",
                (author, title, content, category),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def update_post(post_id: int, title: str, content: str, category: str = "자유"):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE posts SET title = %s, content = %s, category = %s, updated_at = NOW() WHERE id = %s;",
                (title, content, category, post_id),
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
                "SELECT id, author, title, content, views, created_at, updated_at, category FROM posts ORDER BY id ASC;"
            )
            rows = cur.fetchall()
            return [
                {
                    "id": r[0], "author": r[1], "title": r[2], "content": r[3],
                    "views": r[4], "created_at": r[5], "updated_at": r[6], "category": r[7],
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
