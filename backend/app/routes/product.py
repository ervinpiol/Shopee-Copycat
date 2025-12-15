from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_async_session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate
from app.routes.users import fastapi_users
from app.models.users import User
from typing import List

from redis.asyncio import Redis
import json
from app.core.redis import get_redis

router = APIRouter(prefix="/product", tags=["Product"])

# ======================
# Cache configuration
# ======================

CACHE_TTL = 300  # 5 minutes
PRODUCTS_CACHE_KEY = "products:all"
PRODUCT_CACHE_KEY = "products:{id}"

# ======================
# Cache helpers
# ======================

async def invalidate_products_cache(redis: Redis) -> None:
    """Invalidate product list cache"""
    await redis.delete(PRODUCTS_CACHE_KEY)


@router.get("", response_model=List[ProductRead])
async def get_products(
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis)
):
    try:
        cached = await redis.get(PRODUCTS_CACHE_KEY)
        if cached:
            return json.loads(cached)
        
        result = await session.execute(select(Product))
        products = result.scalars().all()

        data = [ProductRead.model_validate(p).model_dump() for p in products]

        await redis.setex(
            PRODUCTS_CACHE_KEY,
            CACHE_TTL,
            json.dumps(data)
        )

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
        cache_key = PRODUCT_CACHE_KEY.format(id=product_id)

        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        data = ProductRead.model_validate(product).model_dump()
        await redis.setex(cache_key, CACHE_TTL, json.dumps(data))

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
    """
    Create a new product and assign it to the current user
    """
    try:
        product = Product(
            **product_create.model_dump(exclude_unset=True),
            owner_id=current_user.id
        )

        session.add(product)
        await session.commit()
        await session.refresh(product)

        await invalidate_products_cache(redis)

        return ProductRead.model_validate(product)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating product: {str(e)}")

@router.patch("/{product_id}")
async def update_product(
    product_id: int,
    product_update: ProductUpdate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    """
    Partially update a product by ID
    """
    try:
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Ownership check
        if product.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this product")
        
        update_data = product_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        await session.commit()
        await session.refresh(product)

        await invalidate_products_cache(redis)
        await redis.delete(PRODUCT_CACHE_KEY.format(id=product_id))

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
        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Ownership check
        if product.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this product")
        
        await session.delete(product)
        await session.commit()

        await invalidate_products_cache(redis)
        await redis.delete(PRODUCT_CACHE_KEY.format(id=product_id))

        return {"success": True, "message": "Product successfully deleted"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
