"""post_reactions 테이블에 직접 접근하는 함수들만 모아둔 파일 (SQL은 여기에만 있음)."""
from database import get_conn

# 고를 수 있는 이모지 종류. 화면에도 항상 이 순서대로 버튼이 뜬다.
ALLOWED_EMOJIS = ["👍", "❤️", "😂", "😮", "😢"]


def toggle_reaction(post_id: int, username: str, emoji: str) -> bool:
    """이미 눌러둔 반응이면 취소(삭제)하고, 안 눌러뒀으면 새로 추가한다.
    같은 사람이 같은 글에 여러 종류의 이모지를 동시에 남기는 건 가능하다 (예: 👍랑 😂 둘 다)."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM post_reactions WHERE post_id = %s AND username = %s AND emoji = %s;",
                (post_id, username, emoji),
            )
            existing = cur.fetchone()
            if existing:
                cur.execute("DELETE FROM post_reactions WHERE id = %s;", (existing[0],))
            else:
                cur.execute(
                    "INSERT INTO post_reactions (post_id, username, emoji) VALUES (%s, %s, %s);",
                    (post_id, username, emoji),
                )
        conn.commit()
    finally:
        conn.close()


def get_reactions_summary(post_id: int, current_username: str):
    """이모지별 개수와, 그중에 내가 누른 것도 있는지를 같이 돌려준다.
    항상 ALLOWED_EMOJIS 5개를 전부(0개짜리도) 순서대로 돌려줘서, 화면에서 버튼 5개를 그대로 그리면 된다."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT emoji, COUNT(*) AS cnt, BOOL_OR(username = %s) AS reacted_by_me
                FROM post_reactions
                WHERE post_id = %s
                GROUP BY emoji;
                """,
                (current_username, post_id),
            )
            rows = {r[0]: {"count": r[1], "reacted_by_me": bool(r[2])} for r in cur.fetchall()}
    finally:
        conn.close()

    return [
        {
            "emoji": emoji,
            "count": rows.get(emoji, {}).get("count", 0),
            "reacted_by_me": rows.get(emoji, {}).get("reacted_by_me", False),
        }
        for emoji in ALLOWED_EMOJIS
    ]
