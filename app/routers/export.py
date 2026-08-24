"""엑셀(.xlsx) 출력 기능."""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from repositories import posts as posts_repo
from repositories import files as files_repo
from security import get_current_user
from excel_utils import build_excel

router = APIRouter(prefix="/api/export", tags=["export"])

XLSX_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/posts")
def export_posts(current_user: dict = Depends(get_current_user)):
    posts = posts_repo.list_posts()
    headers = ["ID", "제목", "작성자", "조회수", "댓글수", "작성일"]
    rows = [
        [p["id"], p["title"], p["author"], p["views"], p["comment_count"], str(p["created_at"])]
        for p in posts
    ]
    buffer = build_excel(headers, rows)
    return StreamingResponse(
        buffer,
        media_type=XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": "attachment; filename=posts_export.xlsx"},
    )


@router.get("/files")
def export_files(current_user: dict = Depends(get_current_user)):
    files = files_repo.list_files()
    headers = ["ID", "파일명", "업로더", "용량(byte)", "업로드일"]
    rows = [
        [f["id"], f["original_name"], f["uploader"], f["size_bytes"], str(f["uploaded_at"])]
        for f in files
    ]
    buffer = build_excel(headers, rows)
    return StreamingResponse(
        buffer,
        media_type=XLSX_MEDIA_TYPE,
        headers={"Content-Disposition": "attachment; filename=files_export.xlsx"},
    )
