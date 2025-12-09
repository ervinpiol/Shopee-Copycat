from fastapi_users import schemas

class UserRead(schemas.BaseUser[int]):
    pass

class UserCreate(schemas.BaseUserCreate):
    first_name: str
    last_name: str
    pass

class UserUpdate(schemas.BaseUserUpdate):
    pass