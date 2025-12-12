import threading
from sqlalchemy import text
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


ASYNC_DB_API = "asyncpg"


def build_connecting_string_supabase_async(
    db_password: str = settings.postgres_password,
) -> str:
    """Async connection string for Supabase"""
    return f"postgresql+asyncpg://postgres.bzyxwswrtcdatuwyvhmv:{db_password}@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"


class SupabaseAsyncEngine:
    """Handles async database connections"""
    _engine: AsyncEngine | None = None
    _lock: threading.Lock = threading.Lock()

    @classmethod
    def _init_engine(cls) -> AsyncEngine:
        try:
            if not cls._engine:
                conn_string = build_connecting_string_supabase_async()
                cls._engine = create_async_engine(
                    conn_string,
                    pool_size=40,
                    max_overflow=10,
                )
        except Exception as e:
            print(f"Error initializing async database engine: {e}")
            raise
        return cls._engine

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        """Gets the async sql alchemy engine."""
        try:
            if not cls._engine:
                with cls._lock:
                    if not cls._engine:
                        cls._engine = cls._init_engine()
        except Exception as e:
            print(f"Error getting async database engine: {e}")
            raise
        return cls._engine


def get_async_engine() -> AsyncEngine:
    """Get the async database engine."""
    print("Getting async engine")
    return SupabaseAsyncEngine.get_engine()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with AsyncSession(
        get_async_engine(), expire_on_commit=False
    ) as async_session:
        yield async_session


async def warm_up_connections(async_conn_to_warmup: int = 10) -> None:
    """Warm up async database connection pool on startup."""
    print("Warming up async database connections...")
    async_engine = get_async_engine()
    
    async_connections = []
    for _ in range(async_conn_to_warmup):
        conn = await async_engine.connect()
        async_connections.append(conn)
    
    for async_conn in async_connections:
        await async_conn.execute(text("SELECT 1"))
    
    for async_conn in async_connections:
        await async_conn.close()
    
    print(f"Warmed up {async_conn_to_warmup} async connections")