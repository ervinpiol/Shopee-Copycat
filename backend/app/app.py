from collections.abc import AsyncGenerator
from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware

from app.core.engine import warm_up_connections
from app.core.redis import RedisClient
from app.core.config import settings

from app.routes.users import auth_backend, fastapi_users
from app.schemas.users import UserRead, UserCreate, UserUpdate

# Routers
from app.routes.todo import router as todo_router
from app.routes.product import router as product_router
from app.routes.cart import router as cart_router
from app.routes.checkout import router as checkout_router
from app.routes.order import router as order_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("API lifespan started")

    await warm_up_connections()  # DB, external APIs, etc.
    await RedisClient.init()

    print("Redis connected")

    yield

    await RedisClient.close()
    print("Redis closed")


app = FastAPI(
    lifespan=lifespan, title="Fullstack", version="v0.1.0"
)

# ----------------------------
# CORS Middleware
# ----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# ----------------------------
# Auth Routes (Cookie-based)
# ----------------------------
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


# ----------------------------
# Other Routers
# ----------------------------
app.include_router(todo_router)
app.include_router(product_router)
app.include_router(cart_router)
app.include_router(checkout_router)
app.include_router(order_router)