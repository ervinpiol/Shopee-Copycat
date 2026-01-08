from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from fastapi.encoders import jsonable_encoder
from app.db import get_async_session
from app.models.seller import Seller, SellerOrder
from app.schemas.seller import SellerRead, SellerOrderRead, SellerCreate
from app.models.product import Product
from app.schemas.product import SellerProductRead, ProductCreate, ProductUpdate
from app.core.dependencies import seller_required
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


@router.post("/register", response_model=SellerRead)
async def register_seller(
    seller_create: SellerCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
):
    try:
        # Check if user is already a seller
        result = await session.execute(
            select(Seller).where(Seller.owner_id == current_user.id)
        )
        existing_seller = result.scalars().first()
        if existing_seller:
            raise HTTPException(status_code=400, detail="User is already a seller")

        # Create new seller with default values
        new_seller = Seller(
            owner_id=current_user.id,
            **seller_create.model_dump()
        )
        session.add(new_seller)
        await session.commit()
        await session.refresh(new_seller)

        return SellerRead.model_validate(new_seller)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Products
SELLER_PRODUCTS_CACHE_KEY = "seller_products:all"
SELLER_PRODUCT_CACHE_KEY = "seller_products:{id}"


@router.get("/products", response_model=List[SellerProductRead])
async def get_seller_products(
    current_user: User = Depends(seller_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        cache_key = SELLER_PRODUCTS_CACHE_KEY.format(id=current_user.id)

        # Return cached products if available
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # Fetch products where owner_id is the seller's user id
        result = await session.execute(
            select(Product).where(Product.owner_id == current_user.id)
        )

        products = result.scalars().all()

        # Serialize using Pydantic
        data = [
            SellerProductRead.model_validate(p).model_dump(mode="json")
            for p in products
        ]

        # Cache per seller
        await cache.set(cache_key, json.dumps(data))

        return data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/products/{product_id}", response_model=SellerProductRead)
async def get_seller_product(
    product_id: int,
    current_user: User = Depends(seller_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        cache_key = SELLER_PRODUCT_CACHE_KEY.format(id=product_id)

        # Return cached product if available
        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        # Fetch product by id and owner_id
        result = await session.execute(
            select(Product).where(
                Product.id == product_id,
                Product.owner_id == current_user.id
            )
        )

        product = result.scalars().first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Serialize using Pydantic
        data = SellerProductRead.model_validate(product).model_dump(mode="json")

        # Cache the product
        await cache.set(cache_key, json.dumps(data))

        return data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/products", response_model=SellerProductRead)
async def create_seller_product(
    product_create: ProductCreate,
    current_user: User = Depends(seller_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis)
):
    try:
        # Fetch the seller record to get the actual seller_id
        seller_result = await session.execute(
            select(Seller).where(Seller.owner_id == current_user.id)
        )
        seller = seller_result.scalars().first()
        
        if not seller:
            raise HTTPException(status_code=404, detail="Seller profile not found")
        
        # Create new product using the seller's ID, not the user's ID
        new_product = Product(
            owner_id=current_user.id,
            seller_id=seller.id,  # Use seller.id instead of current_user.id
            **product_create.model_dump()
        )
        session.add(new_product)
        await session.commit()
        await session.refresh(new_product)

        # Invalidate seller products cache
        cache = CacheManager(redis)
        await cache.invalidate(SELLER_PRODUCTS_CACHE_KEY.format(id=current_user.id))

        return SellerProductRead.model_validate(new_product)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.put("/products/{product_id}", response_model=SellerProductRead)
async def update_seller_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(seller_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis)
):
    try:
        # Fetch product by id and owner_id
        result = await session.execute(
            select(Product).where(
                Product.id == product_id,
                Product.owner_id == current_user.id
            )
        )

        product = result.scalars().first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Update fields
        for key, value in product_update.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        session.add(product)
        await session.commit()
        await session.refresh(product)

        # Invalidate caches
        cache = CacheManager(redis)
        await cache.invalidate(SELLER_PRODUCTS_CACHE_KEY.format(id=current_user.id))
        await cache.invalidate(SELLER_PRODUCT_CACHE_KEY.format(id=product_id))

        return SellerProductRead.model_validate(product)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/products/{product_id}")
async def delete_seller_product(
    product_id: int,
    current_user: User = Depends(seller_required),
    session: AsyncSession = Depends(get_async_session),
    redis=Depends(get_redis)
):
    try:
        # Fetch product by id and owner_id
        result = await session.execute(
            select(Product).where(
                Product.id == product_id,
                Product.owner_id == current_user.id
            )
        )

        product = result.scalars().first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        await session.delete(product)
        await session.commit()

        # Invalidate caches
        cache = CacheManager(redis)
        await cache.invalidate(SELLER_PRODUCTS_CACHE_KEY.format(id=current_user.id))
        await cache.invalidate(SELLER_PRODUCT_CACHE_KEY.format(id=product_id))

        return {"detail": "Product deleted successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))