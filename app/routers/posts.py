"""게시판(글 목록/상세/작성/수정/삭제 + 댓글) 라우트."""
from fastapi import APIRouter, Depends, HTTPException, Query

from models import PostCreate, PostUpdate, CommentCreate
from repositories import posts as posts_repo
from repositories import comments as comments_repo
from repositories import notifications as notifications_repo
from repositories import reactions as reactions_repo
from security import get_current_user

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("")
def list_posts(
    q: str | None = Query(default=None),
    sort: str = Query(default="latest"),
    page: int | None = Query(default=None),
    page_size: int = Query(default=10),
):
    # page가 없으면 예전처럼 전체 목록(엑셀 출력, 홈 화면 개수 표시용)
    # page가 있으면 {items, total, page, page_size} 형태로 페이지네이션된 결과
    if page is None:
        return posts_repo.list_posts(q=q, sort=sort)
    return posts_repo.list_posts_page(q=q, sort=sort, page=page, page_size=page_size)


@router.get("/{post_id}")
def get_post(post_id: int):
    post = posts_repo.get_post(post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글이에요.")
    return post


@router.post("")
def create_post(payload: PostCreate, current_user: dict = Depends(get_current_user)):
    new_id = posts_repo.create_post(current_user["username"], payload.title, payload.content)
    return {"id": new_id, "message": "게시글이 등록됐어요."}


def _check_owner(post_id: int, username: str):
    author = posts_repo.get_post_author(post_id)
    if author is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글이에요.")
    if author != username:
        raise HTTPException(status_code=403, detail="본인이 작성한 글만 수정/삭제할 수 있어요.")


@router.put("/{post_id}")
def update_post(post_id: int, payload: PostUpdate, current_user: dict = Depends(get_current_user)):
    _check_owner(post_id, current_user["username"])
    posts_repo.update_post(post_id, payload.title, payload.content)
    return {"message": "수정됐어요."}


@router.delete("/{post_id}")
def delete_post(post_id: int, current_user: dict = Depends(get_current_user)):
    _check_owner(post_id, current_user["username"])
    posts_repo.delete_post(post_id)
    return {"message": "삭제됐어요."}


# ---------- 댓글 ----------

@router.get("/{post_id}/comments")
def list_comments(post_id: int):
    if posts_repo.get_post_author(post_id) is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글이에요.")
    return comments_repo.list_comments(post_id)


@router.post("/{post_id}/comments")
def create_comment(post_id: int, payload: CommentCreate, current_user: dict = Depends(get_current_user)):
    # 알림에 글 제목을 같이 저장할 거라서 작성자만이 아니라 글 정보를 통째로 가져온다.
    # 댓글을 다는 것뿐인데 조회수가 오르면 이상하니까 increment_view=False.
    post = posts_repo.get_post(post_id, increment_view=False)
    if post is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글이에요.")

    new_id = comments_repo.create_comment(post_id, current_user["username"], payload.content)

    # 글쓴이에게 알림을 남긴다. 내 글에 내가 댓글을 단 경우는 알릴 필요가 없으니 건너뛴다.
    if post["author"] != current_user["username"]:
        try:
            notifications_repo.create_notification(
                recipient=post["author"],
                actor=current_user["username"],
                post_id=post_id,
                post_title=post["title"],
                preview=payload.content,
            )
        except Exception as e:
            # 알림은 부가 기능이라, 여기서 실패하더라도 댓글 등록 자체는 성공으로 둔다.
            print(f"[알림] 생성 실패 (댓글은 정상 등록됨): {e}")

    return {"id": new_id, "message": "댓글이 등록됐어요."}


@router.delete("/{post_id}/comments/{comment_id}")
def delete_comment(post_id: int, comment_id: int, current_user: dict = Depends(get_current_user)):
    author = comments_repo.get_comment_author(comment_id)
    if author is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 댓글이에요.")
    if author != current_user["username"]:
        raise HTTPException(status_code=403, detail="본인이 작성한 댓글만 삭제할 수 있어요.")
    comments_repo.delete_comment(comment_id)
    return {"message": "댓글이 삭제됐어요."}


# ---------- 이모지 반응 ----------

@router.get("/{post_id}/reactions")
def list_reactions(post_id: int, current_user: dict = Depends(get_current_user)):
    if posts_repo.get_post_author(post_id) is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글이에요.")
    return reactions_repo.get_reactions_summary(post_id, current_user["username"])


@router.post("/{post_id}/reactions/{emoji}")
def toggle_reaction(post_id: int, emoji: str, current_user: dict = Depends(get_current_user)):
    if emoji not in reactions_repo.ALLOWED_EMOJIS:
        raise HTTPException(status_code=400, detail="지원하지 않는 이모지예요.")
    if posts_repo.get_post_author(post_id) is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 게시글이에요.")

    reactions_repo.toggle_reaction(post_id, current_user["username"], emoji)
    # 눌렀다/취소했다를 따로 알려주는 대신, 그냥 갱신된 전체 반응 현황을 돌려준다.
    # (화면에서는 이 응답 하나로 버튼 5개를 통째로 다시 그리면 되니까 더 단순하다.)
    return reactions_repo.get_reactions_summary(post_id, current_user["username"])
