from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from fastapi.encoders import jsonable_encoder
from app.db import get_async_session
from app.models.seller import Seller, SellerOrder
from app.schemas.seller import SellerRead, SellerOrderRead, SellerCreate
from app.models.users import UserRole
from app.routes.users import fastapi_users
from app.models.users import User
from app.core.redis import get_redis
from app.core.cache import CacheManager
import json

router = APIRouter(prefix="/seller", tags=["seller"])

# Cache keys
SELLER_CACHE_KEY = "sellers:{id}"
SELLER_ORDERS_CACHE_KEY = "seller_orders:{id}"


@router.get("", response_model=SellerRead)
async def get_seller(
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis),
    current_user: User = Depends(fastapi_users.current_user()),
):
    try:
        if current_user.role != "seller":
            raise HTTPException(status_code=403, detail="User is not a seller")

        cache = CacheManager(redis)
        cache_key = SELLER_CACHE_KEY.format(id=current_user.id)

        # Return cached seller if available
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # Fetch seller from DB
        result = await session.execute(
            select(Seller).where(Seller.owner_id == current_user.id)
        )
        seller = result.scalars().first()

        if not seller:
            raise HTTPException(status_code=404, detail="Seller not found")

        data = SellerRead.model_validate(seller)
        encoded = jsonable_encoder(data)

        # Cache the seller
        await cache.set(cache_key, json.dumps(encoded))

        return encoded

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/order", response_model=List[SellerOrderRead])
async def get_seller_orders(
    current_user: User = Depends(fastapi_users.current_user()),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis)
):
    try:
        # Only sellers can access
        if current_user.role != "seller":
            raise HTTPException(status_code=403, detail="User is not a seller")

        cache = CacheManager(redis)
        cache_key = SELLER_ORDERS_CACHE_KEY.format(id=current_user.id)

        # Return cached orders if available
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # Fetch orders where owner_id is the seller's user id
        result = await session.execute(
            select(SellerOrder)
            .options(selectinload(SellerOrder.shipping_address))
            .where(SellerOrder.owner_id == current_user.id)
        )

        orders = result.scalars().all()

        # Serialize using Pydantic
        data = [
            SellerOrderRead.model_validate(o).model_dump(mode="json")
            for o in orders
        ]

        # Cache per seller
        await cache.set(cache_key, json.dumps(data))

        return data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register", status_code=201)
async def register_seller(
    seller_create: SellerCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
):
    try:
        result = await session.execute(
            select(Seller).where(Seller.owner_id == current_user.id)
        )
        if result.scalars().first():
            raise HTTPException(400, "Seller profile already exists")

        seller = Seller(
            owner_id=current_user.id,
            **seller_create.model_dump()
        )

        session.add(seller)
        await session.commit()

        return {"message": "Seller profile created"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
