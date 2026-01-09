from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db import get_async_session
from app.models.product import Product
from app.schemas.product import PublicProductRead
from typing import List
from fastapi.encoders import jsonable_encoder

from redis.asyncio import Redis
import json
from app.core.redis import get_redis
from app.core.cache import CacheManager


router = APIRouter(prefix="/product", tags=["product"])

# Cache keys
PRODUCTS_CACHE_KEY = "products:all"
PRODUCT_CACHE_KEY = "products:{id}"


@router.get("", response_model=List[PublicProductRead])
async def get_products(
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
    page: int = Query(1, ge=1),                 # page number, default 1
    limit: int = Query(20, ge=1, le=500),      # items per page, max 500
):
    try:
        cache = CacheManager(redis)
        offset = (page - 1) * limit

        # Include page and limit in cache key
        cache_key = f"{PRODUCTS_CACHE_KEY}:page:{page}:limit:{limit}"

        # 1️⃣ Return cached products if available
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # 2️⃣ Query database with pagination
        result = await session.execute(select(Product).offset(offset).limit(limit))
        products = result.scalars().all()

        # 3️⃣ Serialize using Pydantic
        data = [PublicProductRead.model_validate(p) for p in products]
        encoded = jsonable_encoder(data)

        # 4️⃣ Cache the page
        await cache.set(cache_key, json.dumps(encoded, default=str))

        return encoded

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}", response_model=PublicProductRead)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        cache_key = PRODUCT_CACHE_KEY.format(id=product_id)
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        data = PublicProductRead.model_validate(product)
        encoded = jsonable_encoder(data)

        await cache.set(cache_key, json.dumps(encoded))
        return encoded

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
