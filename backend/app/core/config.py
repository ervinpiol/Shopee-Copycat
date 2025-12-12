from dotenv import load_dotenv
import os

from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    postgres_user: str = os.getenv("POSTGRES_USER", "postgres")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "changethis")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_db: str = os.getenv("POSTGRES_DB", "postgres")
    SUPABASE_DB_URL: str = os.getenv("SUPABASE_DB_URL", "changeths")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeths")

    cors_allowed_origins: list[str] = ["http://localhost:3000"]


settings = Settings()