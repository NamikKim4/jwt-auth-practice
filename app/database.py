"""DB 연결과 테이블 준비를 담당하는 파일. 다른 파일들은 여기 get_conn()만 가져다 쓴다."""
import time
import psycopg2

from config import DB_CONFIG


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def wait_for_db():
    while True:
        try:
            conn = get_conn()
            conn.close()
            print("[DB] 연결 성공")
            return
        except Exception:
            print("[DB] 아직 준비 안 됨, 2초 후 재시도...")
            time.sleep(2)


def ensure_tables():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            # 예전 버전 DB에 이미 users 테이블이 있던 경우를 위한 안전장치
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;")
            # 프로필 사진(base64 이미지 문자열)과 자기소개. 둘 다 안 정해도 되니 NULL 허용.
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_image TEXT;")
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    author TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    views INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            # 예전 버전 DB에 이미 posts 테이블이 있던 경우를 위한 안전장치
            cur.execute("ALTER TABLE posts ADD COLUMN IF NOT EXISTS views INTEGER DEFAULT 0;")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id SERIAL PRIMARY KEY,
                    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                    author TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            # 알림: "내 글에 누가 댓글을 달았다" 같은 소식을 받는 사람(recipient)별로 쌓아두는 테이블.
            # 글이 지워지면 그 글에 딸린 알림도 같이 지워지게 ON DELETE CASCADE를 걸어뒀다.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id SERIAL PRIMARY KEY,
                    recipient TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    kind TEXT NOT NULL DEFAULT 'comment',
                    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
                    post_title TEXT NOT NULL,
                    preview TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            # "내 안 읽은 알림"을 자주 세게 되므로, 그 조건에 맞춘 인덱스를 만들어둔다.
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_notifications_recipient
                ON notifications (recipient, is_read, id DESC);
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id SERIAL PRIMARY KEY,
                    uploader TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    stored_name TEXT NOT NULL,
                    size_bytes BIGINT NOT NULL,
                    uploaded_at TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    author TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    image_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()
    finally:
        conn.close()
