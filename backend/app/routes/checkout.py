from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db import get_async_session
from app.models.users import User
from app.models.user_order import Order, OrderItem, OrderAddress
from app.models.user_address import UserAddress
from app.models.cart import CartItem
from app.models.seller import SellerOrder
from app.routes.users import fastapi_users

from redis.asyncio import Redis
from app.core.redis import get_redis
from app.core.cache import CacheManager

PRODUCTS_CACHE_KEY = "products:all"
PRODUCT_CACHE_KEY = "products:{id}"
CARTS_CACHE_KEY = "carts:{user_id}"
ORDERS_CACHE_KEY = "orders:user:{user_id}"
SELLER_ORDERS_CACHE_KEY = "seller_orders:all"

router = APIRouter(prefix="/checkout", tags=["checkout"])


@router.post("")
async def checkout(
    cart_item_ids: List[int] = Body(..., embed=True),
    user_address_id: int = Body(..., embed=True),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis),
):
    try:
        cache = CacheManager(redis)

        # Validate cart items
        if not cart_item_ids:
            raise HTTPException(status_code=400, detail="No cart items provided")

        result = await session.execute(
            select(CartItem)
            .options(selectinload(CartItem.product))
            .where(
                CartItem.owner_id == current_user.id,
                CartItem.id.in_(cart_item_ids)
            )
        )
        cart_items = result.scalars().all()
        if not cart_items:
            raise HTTPException(status_code=400, detail="No valid cart items found")

        # Validate user address
        result = await session.execute(
            select(UserAddress).where(
                UserAddress.user_id == current_user.id,
                UserAddress.id == user_address_id
            )
        )
        user_address = result.scalars().first()
        if not user_address:
            raise HTTPException(status_code=400, detail="Invalid user address")

        total_price = 0
        product_ids: set[int] = set()
        seller_items: dict[int, list[CartItem]] = {}

        # Group items by seller and check stock
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
            owner_name=" ".join(filter(None, [current_user.first_name, current_user.last_name])),
            status="pending",
            total_price=total_price,
        )
        session.add(new_order)
        await session.flush()  # Get new_order.id

        # Create shipping address snapshot
        order_address = OrderAddress(
            order_id=new_order.id,
            recipient_name=user_address.recipient_name,
            phone=user_address.phone,
            address_line1=user_address.address_line1,
            address_line2=user_address.address_line2,
            city=user_address.city,
            province=user_address.province,
            postal_code=user_address.postal_code,
            country=user_address.country or "PH",
        )
        session.add(order_address)

        # Create order items and seller orders
        for seller_id, items in seller_items.items():
            seller_total_price = sum(item.product.price * item.quantity for item in items)

            # Create seller order
            seller_order = SellerOrder(
                owner_id=current_user.id,
                owner_name=" ".join(filter(None, [current_user.first_name, current_user.last_name])),
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
                        status="pending",
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
        await cache.invalidate(ORDERS_CACHE_KEY.format(user_id=current_user.id))
        await cache.invalidate(SELLER_ORDERS_CACHE_KEY)

        return {"success": True, "message": "Checkout successful!"}

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
