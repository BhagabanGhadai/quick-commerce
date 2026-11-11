from fastapi import APIRouter

from core.schemas import ApiResponse

from . import service
from .schemas import Order, OrderCreate

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=ApiResponse[list[Order]])
def list_orders():
    return ApiResponse(data=service.list_orders())


@router.get("/{order_id}", response_model=ApiResponse[Order])
def get_order(order_id: int):
    return ApiResponse(data=service.get_order(order_id))


@router.post("/", response_model=ApiResponse[Order], status_code=201)
def place_order(data: OrderCreate):
    return ApiResponse(data=service.place_order(data))
