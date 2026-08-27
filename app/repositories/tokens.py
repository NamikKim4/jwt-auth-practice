"""리프레시 토큰(자동 로그인 연장용) 테이블에 접근하는 함수들만 모아둔 파일."""
from datetime import datetime

from database import get_conn


def store_refresh_token(username: str, token_hash: str, expires_at: datetime):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO refresh_tokens (username, token_hash, expires_at)
                VALUES (%s, %s, %s);
                """,
                (username, token_hash, expires_at),
            )
        conn.commit()
    finally:
        conn.close()


def find_refresh_token(token_hash: str):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT username, expires_at, revoked
                FROM refresh_tokens WHERE token_hash = %s;
                """,
                (token_hash,),
            )
            row = cur.fetchone()
            if row is None:
                return None
            return {"username": row[0], "expires_at": row[1], "revoked": row[2]}
    finally:
        conn.close()


def revoke_refresh_token(token_hash: str):
    """해당 토큰 하나만 무효화한다. 이미 없거나 이미 무효화된 토큰이어도 에러 없이 조용히 넘어간다."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE refresh_tokens SET revoked = TRUE WHERE token_hash = %s;",
                (token_hash,),
            )
        conn.commit()
    finally:
        conn.close()


def revoke_all_for_user(username: str):
    """그 계정이 갖고 있던 모든 리프레시 토큰(=모든 기기의 로그인)을 한 번에 끊는다.
    토큰 탈취가 의심되거나(로테이션된 옛 토큰 재사용), 비밀번호 변경/계정 삭제처럼
    "지금부터는 예전 로그인이 다 무효여야 하는" 상황에 쓴다."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE refresh_tokens SET revoked = TRUE WHERE username = %s AND revoked = FALSE;",
                (username,),
            )
        conn.commit()
    finally:
        conn.close()


def delete_expired_tokens():
    """유효기간이 지난 지 오래된 토큰들을 지운다. 안 지워도 동작엔 문제없지만
    테이블이 계속 커지기만 하는 걸 막기 위한 청소용 함수."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM refresh_tokens WHERE expires_at < NOW();")
        conn.commit()
    finally:
        conn.close()
