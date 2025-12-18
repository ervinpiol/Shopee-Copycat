from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, func, Enum as SqlEnum, Boolean, Text
from sqlalchemy.orm import relationship
from app.db import Base
from enum import Enum

class CategoryEnum(str, Enum):
    ELECTRONICS = "Electronics"
    ACCESSORIES = "Accessories"
    STORAGE = "Storage"

class StatusEnum(str, Enum):
    in_stock = "in_stock"
    low_stock = "low_stock"
    out_of_stock = "out_of_stock"


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    stock = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True)
    image = Column(String, nullable=True)
    rating = Column(Float, nullable=False, default=0.0)
    reviews = Column(Integer, nullable=False, default=0)
    category = Column(SqlEnum(CategoryEnum, name="category_enum"), nullable=True)
    status = Column(SqlEnum(StatusEnum, name="status_enum"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    seller = relationship("Seller", back_populates="products")

    # ✅ Correct relationship
    order_items = relationship(
        "OrderItem",
        back_populates="product",
        cascade="all, delete-orphan"
    )