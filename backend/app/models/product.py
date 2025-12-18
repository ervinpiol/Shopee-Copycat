from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Float, Integer, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.db import Base
from enum import Enum

class CategoryEnum(str, Enum):
    ELECTRONICS = "Electronics"
    ACCESSORIES = "Accessories"
    STORAGE = "Storage"

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

    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    seller = relationship("Seller", back_populates="products")

    # ✅ Correct relationship
    order_items = relationship(
        "OrderItem",
        back_populates="product",
        cascade="all, delete-orphan"
    )