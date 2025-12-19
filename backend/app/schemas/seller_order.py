from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

# Define specific Literals for SellerOrders vs Products
SellerOrderStatusLiteral = Literal["pending", "processing", "shipped", "delivered", "cancelled"]


class SellerOrderRead(BaseModel):
    id: int
    owner_id: int
    owner_name: str
    status: SellerOrderStatusLiteral
    total_price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SellerOrderCreate(BaseModel):
    status: SellerOrderStatusLiteral = "pending"
    total_price: float = 0.0


class SellerOrderUpdate(BaseModel):
    status: Optional[SellerOrderStatusLiteral] = None
    total_price: Optional[float] = None