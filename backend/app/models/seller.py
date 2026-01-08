# models/seller.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Enum as SqlEnum, Float
from sqlalchemy.orm import relationship
from app.db import Base
from enum import Enum

class SellerStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"

class SellerOrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)

    store_name = Column(String, nullable=False, unique=True)
    store_description = Column(String)
    phone = Column(String, nullable=False)

    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    province = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    country = Column(String, default="PH")
    store_category = Column(String, nullable=False)
    status=Column(String, nullable=False, default="pending")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="seller")
    products = relationship("Product", back_populates="seller")
    order_items = relationship("OrderItem", back_populates="seller")


## SELLER ORDER
class SellerOrder(Base):
    __tablename__ = "seller_orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    owner_name = Column(String, nullable=False)
    total_price = Column(Float, nullable=False, default=0.0)
    status = Column(
        SqlEnum(SellerOrderStatus, name="seller_order_status_enum", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=SellerOrderStatus.PENDING,
        server_default=SellerOrderStatus.PENDING.value,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    owner = relationship("User", back_populates="seller_orders")
    shipping_address = relationship("OrderAddress", uselist=False, back_populates="seller_order", cascade="all, delete-orphan")

