from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_async_session
from app.models.users import User
from app.schemas.users import UserRead
from app.routes.dependencies import admin_required

router = APIRouter(prefix="/admin/users", tags=["admin_users"])

@router.get("/", response_model=list[UserRead])
async def get_all_users(
    _: User = Depends(admin_required),   # 🔒 admin-only
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users