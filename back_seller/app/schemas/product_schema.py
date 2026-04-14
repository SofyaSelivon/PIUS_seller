from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.enums.product_category import ProductCategory


class ProductCreate(BaseModel):
    name: str
    description: str
    category: ProductCategory
    price: Decimal
    available: int
    img: Optional[str]


class ProductUpdate(BaseModel):
    name: Optional[str]
    price: Optional[Decimal]
    available: Optional[int]


class ProductResponse(BaseModel):
    id: UUID
    name: str
    price: Decimal
    category: ProductCategory
    available: int
    img: Optional[str]

    class Config:
        from_attributes = True
