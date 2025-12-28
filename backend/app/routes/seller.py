from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.db import get_async_session
from app.models.seller import Seller, SellerOrder
from app.schemas.seller import SellerCreate, SellerRead, SellerUpdate, SellerOrderRead
from app.routes.users import fastapi_users
from app.models.users import User
from typing import List
from fastapi.encoders import jsonable_encoder

from redis.asyncio import Redis
import json
from app.core.redis import get_redis
from app.core.cache import CacheManager

from app.core.upload import upload_to_supabase

router = APIRouter(prefix="/seller", tags=["seller"])

# Cache keys
SELLERS_CACHE_KEY = "sellers:all"
SELLER_CACHE_KEY = "sellers:{id}"

SELLER_ORDERS_CACHE_KEY = "seller_orders:all"
SELLER_ORDER_CACHE_KEY = "seller_orders:{id}"


@router.get("/{seller_id}", response_model=SellerRead)
async def get_order(
    seller_id: int,
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis)
):  
    try:
        cache = CacheManager(redis)
        cache_key = SELLER_CACHE_KEY.format(id=seller_id)
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        result = await session.execute(
            select(Seller).options(selectinload(Seller.items)).where(Seller.id == seller_id)
        )
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail="Seller not found")
        
        # Pydantic handles datetime serialization
        data_json = SellerRead.model_validate(order).model_dump_json()
        await cache.set(cache_key, data_json)

        return json.loads(data_json)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    



@router.get("/order", response_model=List[SellerOrderRead])
async def get_orders(
    current_user: User = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        cached = await cache.get(SELLER_ORDERS_CACHE_KEY)
        if cached:
            return json.loads(cached)

        # Query seller orders for current user
        result = await session.execute(
            select(SellerOrder)
            .where(SellerOrder.owner_id == current_user.id)
        )

        orders = result.scalars().all()

        # Serialize using Pydantic
        data = [SellerOrderRead.model_validate(o).model_dump(mode="json") for o in orders]

        # Store in cache
        await cache.set(SELLER_ORDERS_CACHE_KEY, json.dumps(data))

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))