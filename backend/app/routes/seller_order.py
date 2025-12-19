from fastapi import APIRouter

router = APIRouter(prefix="/seller/order", tags=["seller_order"])

# Cache keys
SELLER_ORDERS_CACHE_KEY = "seller_orders:all"
SELLER_ORDER_CACHE_KEY = "seller_orders:{id}"

@router.get("")
async def health_check():
    return {"status": "ok"}
