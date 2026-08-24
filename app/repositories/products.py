"""products 테이블(상품등록 및 후기)에 접근하는 함수들."""
from database import get_conn


def list_products():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, author, name, description, image_data, created_at FROM products ORDER BY id DESC;"
            )
            rows = cur.fetchall()
            return [
                {
                    "id": r[0], "author": r[1], "name": r[2],
                    "description": r[3], "image_data": r[4], "created_at": r[5],
                }
                for r in rows
            ]
    finally:
        conn.close()


def get_product(product_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, author, name, description, image_data, created_at FROM products WHERE id = %s;",
                (product_id,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return {
                "id": row[0], "author": row[1], "name": row[2],
                "description": row[3], "image_data": row[4], "created_at": row[5],
            }
    finally:
        conn.close()


def get_product_author(product_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT author FROM products WHERE id = %s;", (product_id,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        conn.close()


def create_product(author: str, name: str, description: str, image_data: str) -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO products (author, name, description, image_data)
                VALUES (%s, %s, %s, %s) RETURNING id;
                """,
                (author, name, description, image_data),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def update_product(product_id: int, name: str, description: str, image_data: str | None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            if image_data:
                cur.execute(
                    "UPDATE products SET name = %s, description = %s, image_data = %s WHERE id = %s;",
                    (name, description, image_data, product_id),
                )
            else:
                cur.execute(
                    "UPDATE products SET name = %s, description = %s WHERE id = %s;",
                    (name, description, product_id),
                )
        conn.commit()
    finally:
        conn.close()


def delete_product(product_id: int):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM products WHERE id = %s;", (product_id,))
        conn.commit()
    finally:
        conn.close()


def count_products() -> int:
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM products;")
            return cur.fetchone()[0]
    finally:
        conn.close()
