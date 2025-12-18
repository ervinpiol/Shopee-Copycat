from pydantic import BaseModel, Field
from typing import Optional


class SellerBase(BaseModel):
    store_name: str
    store_description: Optional[str] = None
    is_active: bool = Field(default=False)
    store_category: str


class SellerRequest(SellerBase):
    pass

class SellerRead(SellerBase):
    id: int
    owner_id: int
    is_active: bool

    class Config:
        from_attributes = True
