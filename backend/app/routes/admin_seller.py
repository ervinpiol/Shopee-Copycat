from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from app.db import get_async_session
from app.models.seller import Seller, SellerStatus
from app.schemas.seller import SellerRead
from app.routes.users import fastapi_users
from app.models.users import User, UserRole
from app.core.dependencies import admin_required
from app.core.redis import get_redis
from app.core.cache import CacheManager
import json

router = APIRouter(prefix="/admin/seller", tags=["admin"])

ADMIN_SELLERS_CACHE_KEY = "admin_seller:all"
ADMIN_SELLER_CACHE_KEY = "admin_seller:{id}"
   
@router.get("", response_model=List[SellerRead])
async def get_all_sellers(
    _: User = Depends(admin_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis),
    page: int = Query(1, ge=1),                # page number, default 1
    limit: int = Query(20, ge=1, le=500),     # items per page
):
    try:
        cache = CacheManager(redis)

        # Calculate offset from page
        offset = (page - 1) * limit

        # Use page and limit in cache key
        cache_key = f"{ADMIN_SELLERS_CACHE_KEY}:page:{page}:limit:{limit}"

        # 1️⃣ Check cache first
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # 2️⃣ Query database with limit & offset
        result = await session.execute(select(Seller).offset(offset).limit(limit))
        sellers = result.scalars().all()

        # Convert to dicts
        data = [SellerRead.model_validate(s).model_dump() for s in sellers]

        # 3️⃣ Save to cache (handle datetime serialization)
        await cache.set(cache_key, json.dumps(data, default=str))

        return data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{seller_id}", response_model=SellerRead)
async def get_seller_by_id(
    seller_id: int,
    _: User = Depends(admin_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis),
):
    try:
        cache = CacheManager(redis)
        cache_key = ADMIN_SELLER_CACHE_KEY.format(id=seller_id)

        # 1️⃣ Check cache first
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # 2️⃣ If not cached, query database
        result = await session.execute(select(Seller).where(Seller.id == seller_id))
        seller = result.scalars().first()

        if not seller:
            raise HTTPException(status_code=404, detail="Seller not found")

        data = SellerRead.model_validate(seller).model_dump()

        # 3️⃣ Save to cache
        await cache.set(cache_key, json.dumps(data, default=str))

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{seller_id}/activate-reject", response_model=SellerRead)
async def toggle_seller_status(
    seller_id: int,
    status: SellerStatus,  # admin must send either "approved" or "declined"
    _: User = Depends(admin_required),
    session: AsyncSession = Depends(get_async_session),
    redis = Depends(get_redis),
):
    try:
        # Fetch seller with owner
        result = await session.execute(
            select(Seller).options(selectinload(Seller.owner)).where(Seller.id == seller_id)
        )
        seller = result.scalars().first()

        if not seller:
            raise HTTPException(status_code=404, detail="Seller not found")

        # Update seller status
        seller.status = status

        # Update user role if approved
        if seller.owner:
            seller.owner.role = UserRole.seller if status == SellerStatus.approved else UserRole.customer
            session.add(seller.owner)

        # Commit changes
        session.add(seller)
        await session.commit()
        await session.refresh(seller)

        # 🔄 Invalidate cache using your CacheManager
        cache = CacheManager(redis)
        await cache.invalidate(ADMIN_SELLERS_CACHE_KEY)
        await cache.invalidate(ADMIN_SELLER_CACHE_KEY.format(id=seller.id))

        return SellerRead.model_validate(seller)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))