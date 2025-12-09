from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import relationship
from fastapi_users.db import SQLAlchemyBaseUserTable
from app.db import Base

class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    # Todos owned by user
    todos = relationship(
        "Todo",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    # Products owned by user
    products = relationship(
        "Product",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    # Orders (historical)
    orders = relationship(
        "Order",
        back_populates="owner",
        cascade=None
    )
