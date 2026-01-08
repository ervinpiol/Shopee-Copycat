from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from app.models.users import User
from app.db import get_user_db
from app.core.config import settings
from app.core.cache import CacheManager
from app.core.redis import get_redis

class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request: Request | None = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Request | None = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_login(
        self,
        user: User,
        request: Request | None = None,
        authenticate_call: bool = False,
    ) -> None:
        """Clear user cache on login"""
        try:
            redis = request.app.state.redis if request else None
            if redis:
                cache = CacheManager(redis)
                await cache.clear_user_cache(user.id)
                print(f"Cache cleared for user {user.id}")
        except Exception as e:
            print(f"Error clearing cache: {e}")

    # 🔑 REQUIRED when not using UUIDs
    def parse_id(self, id: str) -> int:
        return int(id)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


# ✅ COOKIE transport (works with frontend)
cookie_transport = CookieTransport(
    cookie_name="auth",
    cookie_max_age=3600,
    cookie_secure=False,   # ❗ required for localhost
    cookie_httponly=True,
    cookie_samesite="lax",
)


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)


# backend using cookie instead of bearer
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)