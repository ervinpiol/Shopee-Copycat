from fastapi_users import schemas

class UserRead(schemas.BaseUser[int]):
    first_name: str
    last_name: str
    is_seller: bool

class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    is_seller: bool = False

class UserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = None
    last_name: str | None = None
    is_seller: bool | None = None