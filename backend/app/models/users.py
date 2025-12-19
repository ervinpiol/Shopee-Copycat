from sqlalchemy import Integer, Column, String, Enum as SQLEnum
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db import Base
from enum import Enum

class UserRole(str, Enum):
    customer = "customer"
    seller = "seller"
    admin = "admin"

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.customer)

    todos = relationship("Todo", back_populates="owner", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="owner")

    # ✅ ONE-TO-ONE
    seller = relationship(
        "Seller",
        back_populates="owner",
        uselist=False
    )
