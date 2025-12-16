from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    total_price: float
    product_name: str

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderRead(BaseModel):
    id: int
    owner_id: int
    owner_name: str
    status: str
    total_price: float
    items: List[OrderItemRead] = []
    order_date: datetime

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]  # list of items in the order
    status: Optional[str] = "pending"
    total_price: Optional[float] = 0.0


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    total_price: Optional[float] = None
