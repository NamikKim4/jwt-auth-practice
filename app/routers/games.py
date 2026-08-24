"""미니게임 점수 제출/랭킹 조회 라우트."""
from fastapi import APIRouter, Depends, HTTPException

from models import GameScoreSubmit
from repositories import games as games_repo
from security import get_current_user

router = APIRouter(prefix="/api/games", tags=["games"])


@router.post("/scores")
def submit_score(payload: GameScoreSubmit, current_user: dict = Depends(get_current_user)):
    if payload.game not in games_repo.LOWER_IS_BETTER:
        raise HTTPException(status_code=400, detail="존재하지 않는 게임이에요.")
    games_repo.submit_score(current_user["username"], payload.game, payload.score)
    # 갱신 성공/실패(더 나쁜 점수라 무시됨)와 무관하게, 이 응답 하나로 랭킹을 다시 그리면 되게
    # 갱신된(또는 그대로인) 랭킹 전체를 돌려준다.
    return games_repo.get_leaderboard(payload.game, current_user["username"])


@router.get("/scores/{game}")
def get_leaderboard(game: str, current_user: dict = Depends(get_current_user)):
    if game not in games_repo.LOWER_IS_BETTER:
        raise HTTPException(status_code=400, detail="존재하지 않는 게임이에요.")
    return games_repo.get_leaderboard(game, current_user["username"])
