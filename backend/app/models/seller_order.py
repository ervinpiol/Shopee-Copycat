from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, func, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.db import Base
from enum import Enum

class SellerOrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class SellerOrder(Base):
    __tablename__ = "seller_orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    owner_name = Column(String, nullable=False)
    total_price = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(
        SqlEnum(
            SellerOrderStatus,
            name="seller_order_status_enum",
            values_callable=lambda x: [e.value for e in x],  # store lowercase
        ),
        nullable=False,
        default=SellerOrderStatus.PENDING,
        server_default=SellerOrderStatus.PENDING.value,
    )

    owner = relationship("User", back_populates="seller_orders")


