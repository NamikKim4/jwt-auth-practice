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
            # 게시글 카테고리(자유/질문/공지/정보/기타). 예전 글들은 전부 '자유'로 채워둔다.
            cur.execute("ALTER TABLE posts ADD COLUMN IF NOT EXISTS category TEXT NOT NULL DEFAULT '자유';")

            # 게시글 이모지 반응. (post_id, username, emoji)가 겹치면 안 되게 해서
            # 같은 사람이 같은 이모지를 두 번 누르면 "취소"로 처리할 수 있게 한다.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS post_reactions (
                    id SERIAL PRIMARY KEY,
                    post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                    username TEXT NOT NULL,
                    emoji TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE (post_id, username, emoji)
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_post_reactions_post ON post_reactions (post_id);
            """)

            # 미니게임 랭킹: 계정(username)별 게임(game)당 "본인 최고 기록" 딱 한 줄만 저장한다.
            # (game, username)이 겹치면 안 되게 해서, 더 잘했을 때만 갱신하는 로직을 UNIQUE + ON CONFLICT로 구현한다.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS game_scores (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    game TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE (username, game)
                );
            """)

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

            # 리프레시 토큰: 로그인할 때 액세스 토큰과 같이 발급되는, 훨씬 오래 사는 토큰.
            # 토큰 원본은 저장하지 않고 sha256 해시만 저장해서, DB가 유출돼도 토큰 자체를 못 꺼내가게 한다.
            # 한 번 쓰면(=리프레시할 때) revoked = TRUE로 바꾸고 새 토큰을 또 발급하는 "로테이션" 방식이라,
            # 이미 폐기된 토큰이 재사용되면 탈취를 의심할 수 있다.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    token_hash TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    revoked BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_refresh_tokens_username ON refresh_tokens (username);
            """)

            # 날씨 기록: 원래는 MongoDB에 바로 저장했었는데, 게시글이랑 똑같이
            # "PostgreSQL에 원본을 두고 주기적으로 MongoDB에 백업"하는 구조로 바꿨다.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS weather_records (
                    id SERIAL PRIMARY KEY,
                    city TEXT NOT NULL,
                    temperature_c DOUBLE PRECISION,
                    humidity_percent DOUBLE PRECISION,
                    wind_speed_ms DOUBLE PRECISION,
                    description TEXT NOT NULL,
                    emoji TEXT NOT NULL,
                    source TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    recorded_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_weather_records_recorded_at ON weather_records (recorded_at DESC);
            """)
        conn.commit()
    finally:
        conn.close()
