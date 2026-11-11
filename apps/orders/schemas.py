from pydantic import BaseModel, Field


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItem(BaseModel):
    product_id: int
    name: str
    unit_price: float
    quantity: int


class Order(BaseModel):
    id: int
    items: list[OrderItem]
    total: float
