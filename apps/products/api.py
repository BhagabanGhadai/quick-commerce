from fastapi import APIRouter

from core.schemas import ApiResponse

from . import service
from .schemas import Product, ProductCreate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ApiResponse[list[Product]])
def list_products():
    return ApiResponse(data=service.list_products())


@router.get("/{product_id}", response_model=ApiResponse[Product])
def get_product(product_id: int):
    return ApiResponse(data=service.get_product(product_id))


@router.post("/", response_model=ApiResponse[Product], status_code=201)
def create_product(data: ProductCreate):
    return ApiResponse(data=service.create_product(data))


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int):
    service.delete_product(product_id)
