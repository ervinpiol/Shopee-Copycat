from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_async_session
from app.models.users import User
from app.models.user_order import Order, OrderItem
from app.routes.users import fastapi_users
from app.models.cart import CartItem
from app.models.seller_order import SellerOrder

from redis.asyncio import Redis
from app.core.redis import get_redis
from app.core.cache import CacheManager

PRODUCTS_CACHE_KEY = "products:all"
PRODUCT_CACHE_KEY = "products:{id}"
CARTS_CACHE_KEY = "carts:{user_id}"
ORDERS_CACHE_KEY = "orders:all"
SELLER_ORDERS_CACHE_KEY = "seller_orders:all"

router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("")
async def checkout(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        result = await session.execute(
            select(CartItem).where(CartItem.owner_id == current_user.id)
        )
        cart_items = result.scalars().all()

        if not cart_items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        total_price = 0
        product_ids: set[int] = set()

        # Group items by seller
        seller_items: dict[int, list[CartItem]] = {}

        for item in cart_items:
            product = item.product
            if product.stock < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for {product.name}"
                )
            total_price += product.price * item.quantity
            product_ids.add(product.id)

            seller_items.setdefault(product.seller_id, []).append(item)

        # Create main order
        new_order = Order(
            owner_id=current_user.id,
            owner_name=" ".join(
                filter(None, [current_user.first_name, current_user.last_name])
            ),
            status="pending",
            total_price=total_price,
        )
        session.add(new_order)
        await session.flush()

        # Create order items and seller orders
        for seller_id, items in seller_items.items():
            seller_total_price = sum(item.product.price * item.quantity for item in items)

            # Create seller order
            seller_order = SellerOrder(
                owner_id=current_user.id,
                owner_name=" ".join(
                    filter(None, [current_user.first_name, current_user.last_name])
                ),
                total_price=seller_total_price,
            )
            session.add(seller_order)
            await session.flush()

            for item in items:
                product = item.product

                # Create order item
                session.add(
                    OrderItem(
                        order_id=new_order.id,
                        product_id=product.id,
                        product_name=product.name,
                        quantity=item.quantity,
                        total_price=product.price * item.quantity,
                        seller_id=product.seller_id,
                        image=product.image,
                    )
                )

                # Deduct stock
                product.stock -= item.quantity
                if product.stock <= 0:
                    product.is_active = False
                session.add(product)

                # Remove cart item
                await session.delete(item)

        await session.commit()

        # Invalidate caches
        await cache.invalidate(CARTS_CACHE_KEY.format(user_id=current_user.id))
        for product_id in product_ids:
            await cache.invalidate(PRODUCTS_CACHE_KEY)
            await cache.invalidate(PRODUCT_CACHE_KEY.format(id=product_id))
        await cache.invalidate(ORDERS_CACHE_KEY)
        await cache.invalidate(SELLER_ORDERS_CACHE_KEY)

        return {"success": True, "message": "Checkout successful!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
