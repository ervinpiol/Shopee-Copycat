from sqlalchemy.orm import DeclarativeBase
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.engine import get_async_session

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Dependency for retrieving the user database adapter.
    User model imported here to break the circular dependency.
    """
    from app.models.users import User 
    yield SQLAlchemyUserDatabase(session, User)