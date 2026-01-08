from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.user_order import OrderAddressRead
from app.models.seller import SellerStatus, SellerOrderStatus


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
    status: Optional[SellerStatus] = None


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
    status: SellerStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True



## SELLER ORDER
class SellerOrderRead(BaseModel):
    id: int
    owner_id: int
    owner_name: str
    status: SellerOrderStatus
    total_price: float
    created_at: datetime
    updated_at: datetime

    shipping_address: Optional[OrderAddressRead] = None

    class Config:
        from_attributes = True


class SellerOrderCreate(BaseModel):
    status: SellerOrderStatus = "pending"
    total_price: float = 0.0


class SellerOrderUpdate(BaseModel):
    status: Optional[SellerOrderStatus] = None
    total_price: Optional[float] = None