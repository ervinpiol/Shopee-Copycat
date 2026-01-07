from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from app.schemas.user_order import OrderAddressRead


class SellerBase(BaseModel):
    store_name: str = Field(..., min_length=2, max_length=100)
    store_description: Optional[str] = Field(None, max_length=500)
    store_category: str = Field(..., max_length=50)


class SellerCreate(SellerBase):
    phone: str

    address_line1: str
    address_line2: Optional[str] = None
    city: str
    province: str
    postal_code: str
    country: str = "PH"


class SellerUpdate(BaseModel):
    store_name: Optional[str] = None
    store_description: Optional[str] = None
    store_category: Optional[str] = None

    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class SellerRead(SellerBase):
    id: int
    owner_id: int

    phone: str
    address_line1: str
    address_line2: Optional[str]
    city: str
    province: str
    postal_code: str
    country: str

    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



## SELLER ORDER
SellerOrderStatusLiteral = Literal["pending", "processing", "shipped", "delivered", "cancelled"]


class SellerOrderRead(BaseModel):
    id: int
    owner_id: int
    owner_name: str
    status: SellerOrderStatusLiteral
    total_price: float
    created_at: datetime
    updated_at: datetime

    shipping_address: Optional[OrderAddressRead] = None

    class Config:
        from_attributes = True


class SellerOrderCreate(BaseModel):
    status: SellerOrderStatusLiteral = "pending"
    total_price: float = 0.0


class SellerOrderUpdate(BaseModel):
    status: Optional[SellerOrderStatusLiteral] = None
    total_price: Optional[float] = None