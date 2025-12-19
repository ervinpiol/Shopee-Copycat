# models/seller.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.db import Base  # Your declarative base

class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,   # 🔥 enforces 1-to-1
    )

    store_name = Column(String, nullable=False, unique=True)
    store_description = Column(String)
    store_category = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # ✅ MUST MATCH User.seller
    owner = relationship("User", back_populates="seller")

    products = relationship("Product", back_populates="seller")

    order_items = relationship("OrderItem", back_populates="seller")
