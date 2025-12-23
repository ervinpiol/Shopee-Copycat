from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import get_async_session
from app.routes.users import fastapi_users
from app.models.user_address import UserAddress
from app.schemas.user_address import (
    AddressCreate,
    AddressRead,
    AddressUpdate,
)
from app.routes.users import current_active_user
from app.models.users import User

from redis.asyncio import Redis
import json
from fastapi.encoders import jsonable_encoder
from app.core.redis import get_redis
from app.core.cache import CacheManager

router = APIRouter(prefix="/users/me/addresses", tags=["user_address"])

# Cache keys
ADDRESS_CACHE_KEY = "address:{id}"


@router.get("", response_model=list[AddressRead])
async def get_my_addresses(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        cache_key = f"user:{user.id}:addresses"

        # Try to get cached addresses
        cached = await cache.get(cache_key)
        if cached:
            # Return list of addresses from cache
            addresses = json.loads(cached)
            return addresses

        # Fetch from DB if cache miss
        result = await session.execute(
            select(UserAddress).where(UserAddress.user_id == user.id)
        )
        addresses = result.scalars().all()

        # Convert to Pydantic models
        data = [AddressRead.model_validate(a) for a in addresses]

        # Cache for 5 minutes
        await cache.set(cache_key, json.dumps(jsonable_encoder(data)), ttl=300)

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("", response_model=AddressRead)
async def create_address(
    address_create: AddressCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis),
):
    try:
        address = UserAddress(
            **address_create.model_dump(),
            user_id=current_user.id,
        )

        session.add(address)
        await session.commit()
        await session.refresh(address)

        await CacheManager(redis).invalidate(f"user:{current_user.id}:addresses")

        return AddressRead.model_validate(address)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.patch("/{address_id}", response_model=AddressRead)
async def update_address(
    address_id: int,
    address_update: AddressUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis),
):
    try:
        result = await session.execute(
            select(UserAddress).where(
                UserAddress.id == address_id,
                UserAddress.user_id == current_user.id,
            )
        )
        address = result.scalars().first()

        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        for key, value in address_update.model_dump(exclude_unset=True).items():
            setattr(address, key, value)

        await session.commit()
        await session.refresh(address)

        await CacheManager(redis).invalidate(f"user:{current_user.id}:addresses")

        return AddressRead.model_validate(address)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
