from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_async_session
from app.models.users import User
from app.models.order import Order, OrderItem
from app.routes.users import fastapi_users
from app.models.cart import CartItem

from redis.asyncio import Redis
from app.core.redis import get_redis
from app.routes.product import invalidate_product_cache, invalidate_products_list_cache

router = APIRouter(prefix="/checkout", tags=["Checkout"])

CACHE_TTL = 300  # 5 minutes
CARTS_CACHE_KEY = "carts:{user_id}"  # per-user cart cache

async def invalidate_carts_cache(redis: Redis, user_id: int) -> None:
    """Invalidate cart list cache for a specific user"""
    await redis.delete(CARTS_CACHE_KEY.format(user_id=user_id))

@router.post("")
async def checkout(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    try:
        result = await session.execute(
            select(CartItem).where(CartItem.owner_id == current_user.id)
        )
        cart_items = result.scalars().all()

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        total_price = 0
        product_ids: set[int] = set()

        for item in cart_items:
            product = item.product
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for {product.name}"
                )
            total_price += product.price * item.quantity
            product_ids.add(product.id)

        # Create order
        new_order = Order(
            owner_id=current_user.id,
            status="pending",
            total_price=total_price
        )
        session.add(new_order)
        await session.flush()

        for item in cart_items:
            product = item.product

            session.add(
                OrderItem(
                    order_id=new_order.id,
                    product_id=product.id,
                    quantity=item.quantity,
                    total_price=product.price * item.quantity
                )
            )

            # Deduct stock
            product.stock -= item.quantity
            if product.stock <= 0:
                product.is_active = False

            session.add(product)
            await session.delete(item)

        await session.commit()

        # ======================
        # Cache invalidation
        # ======================

        # Invalidate cart cache
        await invalidate_carts_cache(redis, current_user.id)

        # Invalidate product caches
        for product_id in product_ids:
            await invalidate_product_cache(redis, product_id)

        # Invalidate product list cache
        await invalidate_products_list_cache(redis)

        return {"success": True, "message": "Checkout successful!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
