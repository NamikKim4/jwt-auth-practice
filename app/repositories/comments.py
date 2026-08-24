"""comments 테이블에 직접 접근하는 함수들만 모아둔 파일 (SQL은 여기에만 있음)."""
from database import get_conn


def list_comments(post_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, author, content, created_at FROM comments WHERE post_id = %s ORDER BY id ASC;",
                (post_id,),
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "author": r[1], "content": r[2], "created_at": r[3]}
                for r in rows
            ]
    finally:
        conn.close()


def list_comments_by_author(author: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.id, c.content, c.created_at, c.post_id, p.title
                FROM comments c
                JOIN posts p ON p.id = c.post_id
                WHERE c.author = %s
                ORDER BY c.id DESC;
                """,
                (author,),
            )
            rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "content": r[1],
                    "created_at": r[2],
                    "post_id": r[3],
                    "post_title": r[4],
                }
                for r in rows
            ]
    finally:
        conn.close()


def create_comment(post_id: int, author: str, content: str) -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO comments (post_id, author, content) VALUES (%s, %s, %s) RETURNING id;",
                (post_id, author, content),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def get_comment_author(comment_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT author FROM comments WHERE id = %s;", (comment_id,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        conn.close()


def delete_comment(comment_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM comments WHERE id = %s;", (comment_id,))
        conn.commit()
    finally:
        conn.close()
