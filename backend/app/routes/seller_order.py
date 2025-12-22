from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_async_session
from app.models.seller_order import SellerOrder
from app.schemas.seller_order import SellerOrderRead, SellerOrderUpdate
from app.routes.users import fastapi_users
from app.models.users import User
from typing import List

import json
from app.core.redis import get_redis
from app.core.cache import CacheManager

router = APIRouter(prefix="/seller/order", tags=["seller_order"])

# Cache keys
SELLER_ORDERS_CACHE_KEY = "seller_orders:all"
SELLER_ORDER_CACHE_KEY = "seller_orders:{id}"

@router.get("", response_model=List[SellerOrderRead])
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