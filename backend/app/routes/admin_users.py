from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import get_async_session
from app.models.users import User, UserRole
from app.schemas.users import UserRead
from app.models.seller import Seller
from app.core.dependencies import admin_required

import json
from app.core.redis import get_redis
from app.core.cache import CacheManager

router = APIRouter(prefix="/admin/users", tags=["admin_users"])

# Cache keys
ADMIN_USERS_CACHE_KEY = "admin_user:all"
ADMIN_USER_CACHE_KEY = "admin_user:{id}"


@router.get("", response_model=list[UserRead])
async def get_admin_users(
    _: User = Depends(admin_required),   # 🔒 admin-only
    session: AsyncSession = Depends(get_async_session),
):
    try:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return users
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{user_id}", response_model=UserRead)
async def get_admin_user(
    user_id: int,
    _: User = Depends(admin_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis),
):
    try:
        cache = CacheManager(redis)
        cache_key = ADMIN_USER_CACHE_KEY.format(id=user_id)

        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        data_json = UserRead.model_validate(user).model_dump_json()
        await cache.set(cache_key, data_json)

        return json.loads(data_json)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    _: User = Depends(admin_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis),
):
    try:
        cache = CacheManager(redis)

        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Prevent admin from deleting themselves
        # admin_required already gives us the current user
        current_admin = _
        if current_admin.id == user_id:
            raise HTTPException(
                status_code=400,
                detail="You cannot delete your own account",
            )

        await session.delete(user)
        await session.commit()

        # Invalidate cache
        await cache.invalidate(ADMIN_USERS_CACHE_KEY)
        await cache.invalidate(ADMIN_USER_CACHE_KEY.format(id=user_id))

        return {"success": True, "message": "User successfully deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{user_id}/role")
async def update_user_role(
    user_id: int,
    role: str = Body(..., embed=True),
    current_admin: User = Depends(admin_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis),
):
    try:
        cache = CacheManager(redis)

        # Prevent admin from changing own role
        if current_admin.id == user_id:
            raise HTTPException(
                status_code=400,
                detail="You cannot change your own role",
            )

        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if role not in UserRole.__members__:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role. Allowed: {[r.value for r in UserRole]}",
            )

        user.role = UserRole[role]

        await session.commit()

        # Invalidate cache
        await cache.invalidate(ADMIN_USERS_CACHE_KEY)
        await cache.invalidate(ADMIN_USER_CACHE_KEY.format(id=user_id))

        return {
            "success": True,
            "user_id": user.id,
            "new_role": user.role.value,
        }

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/sellers/{seller_id}/activate")
async def activate_seller(
    seller_id: int,
    _: User = Depends(admin_required),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        result = await session.execute(
            select(Seller)
            .options(selectinload(Seller.owner))  # ✅ eager load
            .where(Seller.id == seller_id)
        )
        seller = result.scalars().first()

        if not seller:
            raise HTTPException(404, "Seller not found")

        if seller.owner.role != UserRole.seller:
            raise HTTPException(
                status_code=400,
                detail="Cannot activate seller: user role is not 'seller'",
            )

        if seller.is_active:
            return {"success": True, "message": "Seller already active"}

        seller.is_active = True
        await session.commit()

        return {"success": True, "message": "Seller activated"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.patch("/sellers/{seller_id}/deactivate")
async def deactivate_seller(
    seller_id: int,
    _: User = Depends(admin_required),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        result = await session.execute(
            select(Seller)
            .options(selectinload(Seller.owner))  # ✅ eager load
            .where(Seller.id == seller_id)
        )
        seller = result.scalars().first()

        if not seller:
            raise HTTPException(404, "Seller not found")

        if seller.owner.role != UserRole.seller:
            raise HTTPException(
                status_code=400,
                detail="Cannot deactivate seller: user role is not 'seller'",
            )

        if not seller.is_active:
            return {"success": True, "message": "Seller already inactive"}

        seller.is_active = False
        await session.commit()

        return {"success": True, "message": "Seller deactivated"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))