"""미니게임 랭킹(계정별 최고 기록) 테이블에 접근하는 함수들만 모아둔 파일."""
from database import get_conn

# 게임별로 "낮을수록 좋은 점수"인지 여부.
# 숫자야구 = 시도 횟수 (적을수록 좋음), 두더지잡기 = 잡은 개수 (많을수록 좋음),
# 색깔 기억 게임 = 성공한 라운드 (많을수록 좋음), 반응속도 테스트 = 반응 시간 ms (적을수록 좋음)
LOWER_IS_BETTER = {
    "baseball": True,
    "mole": False,
    "simon": False,
    "reaction": True,
    "memory": True,
    "minesweeper": True,
}


def submit_score(username: str, game: str, score: int):
    """이미 저장된 기록보다 더 좋을 때만 덮어쓴다. (더 나쁜 점수가 들어오면 조용히 무시됨)"""
    better_than = "<" if LOWER_IS_BETTER[game] else ">"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO game_scores (username, game, score)
                VALUES (%s, %s, %s)
                ON CONFLICT (username, game) DO UPDATE
                SET score = EXCLUDED.score, created_at = NOW()
                WHERE EXCLUDED.score {better_than} game_scores.score;
                """,
                (username, game, score),
            )
        conn.commit()
    finally:
        conn.close()


def get_leaderboard(game: str, current_username: str, limit: int = 10):
    order = "ASC" if LOWER_IS_BETTER[game] else "DESC"
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT username, score
                FROM game_scores
                WHERE game = %s
                ORDER BY score {order}
                LIMIT %s;
                """,
                (game, limit),
            )
            rows = cur.fetchall()
            return [
                {"username": r[0], "score": r[1], "is_me": r[0] == current_username}
                for r in rows
            ]
    finally:
        conn.close()
