from fastapi import APIRouter

from . import service
from .schemas import Product, ProductCreate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[Product])
def list_products():
    return service.list_products()


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    return service.get_product(product_id)


@router.post("/", response_model=Product, status_code=201)
def create_product(data: ProductCreate):
    return service.create_product(data)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int):
    service.delete_product(product_id)
