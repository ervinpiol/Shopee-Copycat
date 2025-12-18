from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, func, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.db import Base
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    owner_name = Column(String, nullable=False)
    total_price = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(
        SqlEnum(
            OrderStatus,
            name="order_status_enum",
            values_callable=lambda x: [e.value for e in x],  # store lowercase
        ),
        nullable=False,
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value,
    )

    owner = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_item"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    seller_id = Column(Integer, ForeignKey("sellers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    product_name = Column(String, nullable=False)
    status = Column(
        SqlEnum(
            OrderStatus,
            name="order_status_enum",
            values_callable=lambda x: [e.value for e in x],  # store lowercase
        ),
        nullable=False,
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING.value,
    )

    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    seller = relationship("Seller", back_populates="order_items")


