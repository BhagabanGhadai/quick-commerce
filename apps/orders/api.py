from fastapi import APIRouter

from . import service
from .schemas import Order, OrderCreate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=list[Order])
def list_orders():
    return service.list_orders()


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: int):
    return service.get_order(order_id)


@router.post("/", response_model=Order, status_code=201)
def place_order(data: OrderCreate):
    return service.place_order(data)
