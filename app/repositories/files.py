"""files 테이블(자료실 파일 메타데이터)에 접근하는 함수들."""
from database import get_conn


def list_files():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, uploader, original_name, size_bytes, uploaded_at FROM files ORDER BY id DESC;"
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "uploader": r[1], "original_name": r[2], "size_bytes": r[3], "uploaded_at": r[4]}
                for r in rows
            ]
    finally:
        conn.close()


def list_files_by_uploader(uploader: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, original_name, size_bytes, uploaded_at FROM files WHERE uploader = %s ORDER BY id DESC;",
                (uploader,),
            )
            rows = cur.fetchall()
            return [
                {"id": r[0], "original_name": r[1], "size_bytes": r[2], "uploaded_at": r[3]}
                for r in rows
            ]
    finally:
        conn.close()


def get_file(file_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, uploader, original_name, stored_name, size_bytes, uploaded_at FROM files WHERE id = %s;",
                (file_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return {
                "id": row[0],
                "uploader": row[1],
                "original_name": row[2],
                "stored_name": row[3],
                "size_bytes": row[4],
                "uploaded_at": row[5],
            }
    finally:
        conn.close()


def create_file(uploader: str, original_name: str, stored_name: str, size_bytes: int) -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO files (uploader, original_name, stored_name, size_bytes)
                VALUES (%s, %s, %s, %s) RETURNING id;
                """,
                (uploader, original_name, stored_name, size_bytes),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def delete_file(file_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM files WHERE id = %s;", (file_id,))
        conn.commit()
    finally:
        conn.close()


def count_files() -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM files;")
            return cur.fetchone()[0]
    finally:
        conn.close()
