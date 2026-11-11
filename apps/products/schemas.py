from typing import Annotated

from pydantic import BaseModel, Field

from core.sanitize import SafeStr


class ProductCreate(BaseModel):
    # Length is checked after cleaning, so a name that is only HTML is rejected.
    name: Annotated[SafeStr, Field(min_length=1, max_length=200)]
    price: float = Field(gt=0)
    stock: int = Field(ge=0, default=0)


class Product(ProductCreate):
    id: int
