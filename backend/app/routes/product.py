from fastapi import APIRouter, Depends, HTTPException, status, Body, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db import get_async_session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.routes.users import fastapi_users
from app.models.users import User
from typing import List

from redis.asyncio import Redis
import json
from app.core.redis import get_redis
from app.core.cache import CacheManager

from app.core.upload import upload_to_supabase

router = APIRouter(prefix="/product", tags=["product"])

# Cache keys
PRODUCTS_CACHE_KEY = "products:all"
PRODUCT_CACHE_KEY = "products:{id}"


@router.get("", response_model=List[ProductRead])
async def get_products(
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        cached = await cache.get(PRODUCTS_CACHE_KEY)
        if cached:
            return json.loads(cached)

        result = await session.execute(select(Product))
        products = result.scalars().all()
        data = [ProductRead.model_validate(p).model_dump() for p in products]

        await cache.set(PRODUCTS_CACHE_KEY, json.dumps(data))

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{product_id}", response_model=ProductRead)
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

        data = ProductRead.model_validate(product).model_dump()
        await cache.set(cache_key, json.dumps(data))

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_create: ProductCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        product = Product(
            **product_create.model_dump(exclude_unset=True),
            owner_id=current_user.id
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)

        # Invalidate cache
        await cache.invalidate(PRODUCTS_CACHE_KEY)

        return ProductRead.model_validate(product)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    product_update: ProductUpdate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        await session.commit()
        await session.refresh(product)

        # Invalidate caches
        await cache.invalidate(PRODUCTS_CACHE_KEY)
        await cache.invalidate(PRODUCT_CACHE_KEY.format(id=product_id))

        return ProductRead.model_validate(product)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if product.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        await session.delete(product)
        await session.commit()

        # Invalidate caches
        await cache.invalidate(PRODUCTS_CACHE_KEY)
        await cache.invalidate(PRODUCT_CACHE_KEY.format(id=product_id))

        return {"success": True, "message": "Product successfully deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{product_id}/image", response_model=ProductRead)
async def upload_product_image(
    product_id: int,
    image: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis),
):
    cache = CacheManager(redis)

    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    product.image = await upload_to_supabase(image)

    await session.commit()
    await session.refresh(product)

    await cache.invalidate("products:all")
    await cache.invalidate(f"products:{product_id}")

    return ProductRead.model_validate(product)
