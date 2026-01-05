from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_async_session
from app.models.user_order import Order
from app.schemas.user_order import OrderRead, OrderUpdate
from app.routes.users import fastapi_users
from app.models.users import User
from typing import List
from sqlalchemy.orm import selectinload

import json
from app.core.redis import get_redis
from app.core.cache import CacheManager

router = APIRouter(prefix="/order", tags=["order"])

# Cache keys
ORDERS_CACHE_KEY = "orders:user:{user_id}"
ORDER_CACHE_KEY = "orders:user:{user_id}:{order_id}"

@router.get("", response_model=List[OrderRead])
async def get_orders(
    current_user: User = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis),
):
    try:
        cache = CacheManager(redis)
        cache_key = ORDERS_CACHE_KEY.format(user_id=current_user.id)

        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        result = await session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.owner_id == current_user.id)
        )

        orders = result.scalars().all()

        data = [
            OrderRead.model_validate(order).model_dump(mode="json")
            for order in orders
        ]

        await cache.set(cache_key, json.dumps(data))

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis=Depends(get_redis),
):
    try:
        cache = CacheManager(redis)
        cache_key = ORDER_CACHE_KEY.format(
            user_id=current_user.id,
            order_id=order_id,
        )

        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        result = await session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(
                Order.id == order_id,
                Order.owner_id == current_user.id,  # 🔐 ownership check
            )
        )
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        data = OrderRead.model_validate(order).model_dump(mode="json")
        await cache.set(cache_key, json.dumps(data))

        return data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.patch("/{order_id}", response_model=OrderRead)
async def update_order(
    order_id: int,
    order_update: OrderUpdate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis=Depends(get_redis),
):
    try:
        cache = CacheManager(redis)

        result = await session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(
                Order.id == order_id,
                Order.owner_id == current_user.id,
            )
        )
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        update_data = order_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(order, key, value)

        await session.commit()
        await session.refresh(order)

        # ♻️ Invalidate only this user's cache
        await cache.invalidate(
            ORDERS_CACHE_KEY.format(user_id=current_user.id)
        )
        await cache.invalidate(
            ORDER_CACHE_KEY.format(
                user_id=current_user.id,
                order_id=order_id,
            )
        )

        return OrderRead.model_validate(order)

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{order_id}")
async def remove_order(
    order_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis=Depends(get_redis),
):
    try:
        cache = CacheManager(redis)

        result = await session.execute(
            select(Order).where(
                Order.id == order_id,
                Order.owner_id == current_user.id,
            )
        )
        order = result.scalars().first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        await session.delete(order)
        await session.commit()

        await cache.invalidate(
            ORDERS_CACHE_KEY.format(user_id=current_user.id)
        )
        await cache.invalidate(
            ORDER_CACHE_KEY.format(
                user_id=current_user.id,
                order_id=order_id,
            )
        )

        return {"success": True, "message": "Order successfully deleted"}

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
