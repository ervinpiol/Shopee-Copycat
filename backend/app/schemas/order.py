from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

# Define specific Literals for Orders vs Products
OrderStatusLiteral = Literal["pending", "processing", "shipped", "delivered", "cancelled"]

class OrderItemRead(BaseModel):
    id: int
    product_id: int
    seller_id: int 
    quantity: int
    total_price: float
    product_name: str
    image: Optional[str] = None
    status: OrderStatusLiteral

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderRead(BaseModel):
    id: int
    owner_id: int
    owner_name: str
    status: OrderStatusLiteral
    total_price: float
    items: List[OrderItemRead] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    status: OrderStatusLiteral = "pending"
    total_price: float = 0.0


class OrderUpdate(BaseModel):
    status: Optional[OrderStatusLiteral] = None
    total_price: Optional[float] = None