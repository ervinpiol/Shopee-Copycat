from pydantic import BaseModel
from typing import Optional

class AddressBase(BaseModel):
    label: Optional[str] = None
    recipient_name: str
    phone: int
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    province: str
    postal_code: int
    country: str = "PH"
    is_default: bool = False

class AddressCreate(AddressBase):
    pass

class AddressUpdate(BaseModel):
    label: Optional[str] = None
    recipient_name: Optional[str] = None
    phone: Optional[int] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[int] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None

class AddressRead(AddressBase):
    id: int

    class Config:
        from_attributes = True
