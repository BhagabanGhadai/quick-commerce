from fastapi import APIRouter, HTTPException

from .schemas import Product, ProductCreate

router = APIRouter(prefix="/products", tags=["products"])

# In-memory store; swap for a database later.
_products: dict[int, Product] = {}
_next_id = 1


@router.get("/", response_model=list[Product])
def list_products():
    return list(_products.values())


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = _products.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=Product, status_code=201)
def create_product(data: ProductCreate):
    global _next_id
    product = Product(id=_next_id, **data.model_dump())
    _products[product.id] = product
    _next_id += 1
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int):
    if _products.pop(product_id, None) is None:
        raise HTTPException(status_code=404, detail="Product not found")
