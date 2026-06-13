from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=64)
    price: Decimal = Field(gt=0)
    current_stock: int = Field(ge=0)
    safety_stock: int = Field(ge=0)
    status: str = Field(pattern="^(active|inactive)$")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class StockAdjust(BaseModel):
    delta: int


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
