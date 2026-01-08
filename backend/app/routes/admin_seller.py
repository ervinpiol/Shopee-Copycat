from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from fastapi.encoders import jsonable_encoder
from app.db import get_async_session
from app.models.seller import Seller, SellerOrder
from app.schemas.seller import SellerRead, SellerOrderRead, SellerCreate
from app.routes.users import fastapi_users
from app.models.users import User
from app.core.dependencies import admin_required
from app.core.redis import get_redis
from app.core.cache import CacheManager
import json

router = APIRouter(prefix="/admin/seller", tags=["admin_seller"])


ADMIN_SELLERS_CACHE_KEY = "admin_seller:all"
ADMIN_SELLER_CACHE_KEY = "admin_seller:{id}"
   
@router.get("", response_model=List[SellerRead])
async def get_all_sellers(
    _: User = Depends(admin_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis),
):
    try:
        cache = CacheManager(redis)

        # 1️⃣ Check cache first
        cached = await cache.get(ADMIN_SELLERS_CACHE_KEY)
        if cached:
            # cached is a JSON string → convert back to Python list
            return json.loads(cached)

        # 2️⃣ If not cached, query database
        result = await session.execute(select(Seller))
        sellers = result.scalars().all()

        # Convert to dicts
        data = [SellerRead.model_validate(s).model_dump() for s in sellers]

        # 3️⃣ Save to cache (fix datetime serialization)
        await cache.set(ADMIN_SELLERS_CACHE_KEY, json.dumps(data, default=str))

        return data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{seller_id}/activate-reject", response_model=SellerRead)
async def toggle_seller_activation(
    seller_id: int,
    _: User = Depends(admin_required),
    session: AsyncSession = Depends(get_async_session),
    is_active: bool | None = None
):
    try:
        # Fetch the seller
        result = await session.execute(
            select(Seller).options(selectinload(Seller.owner)).where(Seller.id == seller_id)
        )
        seller = result.scalars().first()

        if not seller:
            raise HTTPException(status_code=404, detail="Seller not found")

        # Toggle or set is_active
        if is_active is not None:
            seller.is_active = is_active
        else:
            seller.is_active = not seller.is_active

        # Update the related user's role
        if seller.owner:
            from app.models.users import UserRole
            seller.owner.role = UserRole.seller if seller.is_active else UserRole.customer
            session.add(seller.owner)

        # Commit changes
        session.add(seller)
        await session.commit()
        await session.refresh(seller)

        return SellerRead.model_validate(seller)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))