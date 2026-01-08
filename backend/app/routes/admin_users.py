from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_async_session
from app.models.users import User, UserRole
from app.schemas.users import UserRead
from app.core.dependencies import admin_required

import json
from app.core.redis import get_redis
from app.core.cache import CacheManager

router = APIRouter(prefix="/admin/users", tags=["admin"])

# Cache keys
ADMIN_USERS_CACHE_KEY = "admin_user:all"
ADMIN_USER_CACHE_KEY = "admin_user:{id}"


@router.get("", response_model=list[UserRead])
async def get_admin_users(
    _: User = Depends(admin_required),  # 🔒 only admin
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis),
):
    """
    Get all users. Admin-only endpoint with Redis caching.
    """
    try:
        cache = CacheManager(redis)

        # 1️⃣ Check cache first
        cached = await cache.get(ADMIN_USERS_CACHE_KEY)
        if cached:
            # cached is a JSON string → convert back to Python list
            return json.loads(cached)

        # 2️⃣ If not cached, query database
        result = await session.execute(select(User))
        users = result.scalars().all()

        # Convert to Pydantic models and then to dicts
        data = [UserRead.model_validate(u).model_dump() for u in users]

        # 3️⃣ Save to cache
        await cache.set(ADMIN_USERS_CACHE_KEY, json.dumps(data))

        return data

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

        # Prevent admin from changing their own role
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

        user.role = role
        await session.commit()
        await session.refresh(user)

        # Invalidate caches
        await cache.invalidate(ADMIN_USERS_CACHE_KEY)
        await cache.invalidate(ADMIN_USER_CACHE_KEY.format(id=user_id))

        return {
            "success": True,
            "user_id": user.id,
            "new_role": user.role,
        }

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
