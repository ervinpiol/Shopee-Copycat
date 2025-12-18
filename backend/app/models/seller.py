# models/seller.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base  # Your declarative base
from app.models.users import User  # Assuming you have a User model

class Seller(Base):
    __tablename__ = "sellers"

    id = Column(Integer, primary_key=True, index=True)
    
    # The user who requested / owns this seller account
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="sellers")

    store_name = Column(String, nullable=False, unique=True)
    store_description = Column(String, nullable=True)
    store_category = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)  # Admin approves → True

    # Optional timestamps
    created_at = Column(String, server_default="now()")  # you can use DateTime if you prefer
    updated_at = Column(String, server_default="now()", onupdate="now()")

    products = relationship("Product", back_populates="seller")
