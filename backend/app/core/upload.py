import re
import unicodedata
from supabase import create_client, Client
from fastapi import UploadFile, HTTPException
from uuid import uuid4
from app.core.config import settings


BUCKET_NAME = "products"

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def ensure_bucket_exists(bucket_name: str) -> None:
    buckets = supabase.storage.list_buckets()

    if not any(b.name == bucket_name for b in buckets):
        supabase.storage.create_bucket(
            id=bucket_name,
            options={"public": True}
        )

def sanitize_filename(filename: str) -> str:
    # Normalize unicode (removes weird spaces)
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    # Replace spaces with dashes
    filename = filename.replace(" ", "-")

    # Remove anything not safe
    filename = re.sub(r"[^a-zA-Z0-9._-]", "", filename)

    return filename.lower()


async def upload_to_supabase(file: UploadFile) -> str:
    ensure_bucket_exists(BUCKET_NAME)

    safe_name = sanitize_filename(file.filename)
    filename = f"{uuid4().hex}_{safe_name}"

    content = await file.read()

    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path=filename,
            file=content,
            file_options={
                "content-type": file.content_type,
                "upsert": False,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    return supabase.storage.from_(BUCKET_NAME).get_public_url(filename)
