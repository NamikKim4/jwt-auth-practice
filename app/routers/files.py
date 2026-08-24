"""자료실: 파일 업로드 / 목록 / 다운로드 / 삭제."""
import os
import uuid
import mimetypes

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

from config import UPLOAD_DIR, MAX_FILE_SIZE_MB
from repositories import files as files_repo
from security import get_current_user

router = APIRouter(prefix="/api/files", tags=["files"])

MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def _ensure_upload_dir():
    os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("")
def list_files():
    return files_repo.list_files()


@router.post("")
async def upload_file(upload: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    _ensure_upload_dir()

    content = await upload.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"파일은 최대 {MAX_FILE_SIZE_MB}MB까지만 올릴 수 있어요.")
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="빈 파일은 업로드할 수 없어요.")

    ext = os.path.splitext(upload.filename or "")[1]
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = os.path.join(UPLOAD_DIR, stored_name)

    with open(stored_path, "wb") as f:
        f.write(content)

    new_id = files_repo.create_file(
        uploader=current_user["username"],
        original_name=upload.filename or stored_name,
        stored_name=stored_name,
        size_bytes=len(content),
    )
    return {"id": new_id, "message": "파일이 업로드됐어요."}


@router.get("/{file_id}/download")
def download_file(file_id: int, current_user: dict = Depends(get_current_user)):
    record = files_repo.get_file(file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 파일이에요.")

    path = os.path.join(UPLOAD_DIR, record["stored_name"])
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="파일이 서버에서 사라졌어요.")

    media_type = mimetypes.guess_type(record["original_name"])[0] or "application/octet-stream"
    return FileResponse(path, filename=record["original_name"], media_type=media_type)


@router.delete("/{file_id}")
def delete_file(file_id: int, current_user: dict = Depends(get_current_user)):
    record = files_repo.get_file(file_id)
    if record is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 파일이에요.")
    if record["uploader"] != current_user["username"]:
        raise HTTPException(status_code=403, detail="본인이 올린 파일만 삭제할 수 있어요.")

    path = os.path.join(UPLOAD_DIR, record["stored_name"])
    if os.path.exists(path):
        os.remove(path)
    files_repo.delete_file(file_id)
    return {"message": "파일이 삭제됐어요."}
