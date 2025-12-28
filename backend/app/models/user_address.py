from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class UserAddress(Base):
    __tablename__ = "user_addresses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)

    label = Column(String, nullable=True)  # Home, Office
    recipient_name = Column(String, nullable=False)
    phone = Column(Integer, nullable=False)

    address_line1 = Column(String, nullable=False)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=False)
    province = Column(String, nullable=False)
    postal_code = Column(Integer, nullable=False)
    country = Column(String, default="PH")

    is_default = Column(Boolean, default=False)

    user = relationship("User", back_populates="addresses")
