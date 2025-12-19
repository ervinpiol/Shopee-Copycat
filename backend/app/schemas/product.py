from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

CategoryLiteral = Literal["Electronics", "Accessories", "Storage"]
StatusLiteral = Literal["in_stock", "low_stock", "out_of_stock"]

class ProductBase(BaseModel):
    """
    Shared fields between create and read models
    """
    name: str = Field(..., example="Gaming Mouse")
    description: Optional[str] = Field(None, example="RGB Wireless Mouse")
    price: float = Field(..., ge=0, example=59.99)
    stock: int = Field(..., ge=0, example=100)
    is_active: bool = Field(default=True)
    image: Optional[str] = Field(None, example="https://your-supabase-url/products/image.png")
    rating: Optional[float] = Field(0.0, ge=0, le=5, example=4.5)
    reviews: Optional[int] = Field(0, ge=0, example=123)
    category: Optional[CategoryLiteral] = Field(None, example="Accessories")
    status: Optional[StatusLiteral] = Field(None, example="out_of_stock")


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    image: Optional[str] = None
    rating: Optional[float] = Field(None, ge=0, le=5)
    reviews: Optional[int] = Field(None, ge=0)
    category: Optional[CategoryLiteral] = None


class ProductRead(ProductBase):
    id: int
    seller_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
