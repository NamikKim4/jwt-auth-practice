"""notifications 테이블에 직접 접근하는 함수들만 모아둔 파일 (SQL은 여기에만 있음)."""
from database import get_conn

# 알림 목록에 미리보기로 보여줄 글자 수. 너무 길면 뒤를 잘라내고 …을 붙인다.
PREVIEW_MAX_LEN = 60


def create_notification(recipient: str, actor: str, post_id: int, post_title: str,
                        preview: str, kind: str = "comment") -> int:
    """알림 하나를 남긴다. recipient(받는 사람)에게 actor(행동한 사람)의 소식이 쌓인다."""
    preview = preview.strip().replace("\n", " ")
    if len(preview) > PREVIEW_MAX_LEN:
        preview = preview[:PREVIEW_MAX_LEN] + "…"

    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO notifications (recipient, actor, kind, post_id, post_title, preview)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
                """,
                (recipient, actor, kind, post_id, post_title, preview),
            )
            new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        conn.close()


def list_notifications(recipient: str, limit: int = 20):
    """내 알림을 최신순으로 가져온다."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, actor, kind, post_id, post_title, preview, is_read, created_at
                FROM notifications
                WHERE recipient = %s
                ORDER BY id DESC
                LIMIT %s;
                """,
                (recipient, limit),
            )
            rows = cur.fetchall()
            return [
                {
                    "id": r[0],
                    "actor": r[1],
                    "kind": r[2],
                    "post_id": r[3],
                    "post_title": r[4],
                    "preview": r[5],
                    "is_read": r[6],
                    "created_at": r[7],
                }
                for r in rows
            ]
    finally:
        conn.close()


def count_unread(recipient: str) -> int:
    """아직 안 읽은 알림 개수. 종 아이콘 위의 빨간 배지에 쓰인다."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM notifications WHERE recipient = %s AND is_read = FALSE;",
                (recipient,),
            )
            return cur.fetchone()[0]
    finally:
        conn.close()


def mark_read(notification_id: int, recipient: str) -> bool:
    """알림 하나를 읽음 처리. recipient 조건을 같이 걸어서 남의 알림은 건드릴 수 없게 했다.
    실제로 바뀐 행이 있으면 True."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE notifications SET is_read = TRUE WHERE id = %s AND recipient = %s;",
                (notification_id, recipient),
            )
            changed = cur.rowcount
        conn.commit()
        return changed > 0
    finally:
        conn.close()


def mark_all_read(recipient: str) -> int:
    """내 알림을 전부 읽음 처리하고, 몇 개가 바뀌었는지 돌려준다."""
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE notifications SET is_read = TRUE WHERE recipient = %s AND is_read = FALSE;",
                (recipient,),
            )
            changed = cur.rowcount
        conn.commit()
        return changed
    finally:
        conn.close()
