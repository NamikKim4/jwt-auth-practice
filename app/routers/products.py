"""상품등록 및 후기: 이미지 + 설명으로 남기는 리뷰 게시판."""
from fastapi import APIRouter, Depends, HTTPException

from models import ProductCreate, ProductUpdate
from repositories import products as products_repo
from security import get_current_user

router = APIRouter(prefix="/api/products", tags=["products"])

MAX_IMAGE_DATA_LEN = 4_000_000  # base64 문자열 기준 대략 3MB 원본 이미지 정도


@router.get("")
def list_products():
    return products_repo.list_products()


@router.get("/{product_id}")
def get_product(product_id: int):
    product = products_repo.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 항목이에요.")
    return product


@router.post("")
def create_product(payload: ProductCreate, current_user: dict = Depends(get_current_user)):
    if len(payload.image_data) > MAX_IMAGE_DATA_LEN:
        raise HTTPException(status_code=400, detail="이미지 용량이 너무 커요 (3MB 이하로 올려주세요).")
    if not payload.image_data.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="이미지 형식이 올바르지 않아요.")

    new_id = products_repo.create_product(
        current_user["username"], payload.name, payload.description, payload.image_data
    )
    return {"id": new_id, "message": "등록됐어요."}


def _check_owner(product_id: int, username: str):
    author = products_repo.get_product_author(product_id)
    if author is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 항목이에요.")
    if author != username:
        raise HTTPException(status_code=403, detail="본인이 등록한 항목만 수정/삭제할 수 있어요.")


@router.put("/{product_id}")
def update_product(product_id: int, payload: ProductUpdate, current_user: dict = Depends(get_current_user)):
    _check_owner(product_id, current_user["username"])
    if payload.image_data and len(payload.image_data) > MAX_IMAGE_DATA_LEN:
        raise HTTPException(status_code=400, detail="이미지 용량이 너무 커요 (3MB 이하로 올려주세요).")

    products_repo.update_product(product_id, payload.name, payload.description, payload.image_data)
    return {"message": "수정됐어요."}


@router.delete("/{product_id}")
def delete_product(product_id: int, current_user: dict = Depends(get_current_user)):
    _check_owner(product_id, current_user["username"])
    products_repo.delete_product(product_id)
    return {"message": "삭제됐어요."}
