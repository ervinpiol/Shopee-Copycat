from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.db import get_async_session
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoRead, TodoUpdate
from app.routes.users import fastapi_users
from app.models.users import User

from redis.asyncio import Redis
from app.core.redis import get_redis
from app.core.cache import CacheManager
import json

router = APIRouter(prefix="/todo", tags=["todo"])

TODO_CACHE_KEY = "todos:{id}"
TODOS_CACHE_KEY = "todos:{user_id}:all"
TODOS_COMPLETED_CACHE_KEY = "todos:{user_id}:completed:{completed}"


@router.get("", response_model=List[TodoRead])
async def get_todos(
    completed: Optional[bool] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis),
    page: int = Query(1, ge=1),                 # page number, default 1
    limit: int = Query(20, ge=1, le=100),       # items per page, default 20, max 100
):
    try:
        cache = CacheManager(redis)
        offset = (page - 1) * limit

        # Include completed, page, and limit in cache key
        cache_key = (
            TODOS_CACHE_KEY.format(user_id=current_user.id)
            if completed is None
            else TODOS_COMPLETED_CACHE_KEY.format(user_id=current_user.id, completed=completed)
        )
        cache_key = f"{cache_key}:page:{page}:limit:{limit}"

        # 1️⃣ Return cached todos if available
        cached = await cache.get(cache_key)
        if cached:
            return [TodoRead(**t) for t in json.loads(cached)]

        # 2️⃣ Query database with optional filter and pagination
        query = select(Todo).where(Todo.owner_id == current_user.id)
        if completed is not None:
            query = query.where(Todo.completed == completed)

        result = await session.execute(query.offset(offset).limit(limit))
        todos = result.scalars().all()

        # 3️⃣ Serialize
        data = [TodoRead.model_validate(t).model_dump() for t in todos]

        # 4️⃣ Cache the page
        await cache.set(cache_key, json.dumps(data, default=str))

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        cache_key = TODO_CACHE_KEY.format(id=todo_id)

        cached = await cache.get(cache_key)
        if cached:
            return json.loads(cached)

        todo = await session.get(Todo, todo_id)
        if not todo or todo.owner_id != current_user.id:
            raise HTTPException(status_code=404, detail="Todo not found")

        data = TodoRead.model_validate(todo).model_dump()
        await cache.set(cache_key, json.dumps(data))

        return data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=TodoRead)
async def create_todo(
    todo_create: TodoCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        todo = Todo(
            **todo_create.model_dump(exclude_unset=True),
            owner_id=current_user.id
        )

        session.add(todo)
        await session.commit()
        await session.refresh(todo)

        # Invalidate relevant caches
        await cache.invalidate(TODOS_CACHE_KEY.format(user_id=current_user.id))
        await cache.invalidate(TODOS_COMPLETED_CACHE_KEY.format(user_id=current_user.id, completed=True))
        await cache.invalidate(TODOS_COMPLETED_CACHE_KEY.format(user_id=current_user.id, completed=False))

        return TodoRead.model_validate(todo)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: int,
    todo_update: TodoUpdate = Body(...),
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        todo = await session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        if todo.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this todo")

        update_data = todo_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(todo, key, value)

        await session.commit()
        await session.refresh(todo)

        # Invalidate caches
        await cache.invalidate(TODOS_CACHE_KEY.format(user_id=current_user.id))
        await cache.invalidate(TODOS_COMPLETED_CACHE_KEY.format(user_id=current_user.id, completed=True))
        await cache.invalidate(TODOS_COMPLETED_CACHE_KEY.format(user_id=current_user.id, completed=False))
        await cache.invalidate(TODO_CACHE_KEY.format(id=todo_id))

        return TodoRead.model_validate(todo)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    try:
        cache = CacheManager(redis)
        todo = await session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        if todo.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this todo")

        await session.delete(todo)
        await session.commit()

        # Invalidate caches
        await cache.invalidate(TODOS_CACHE_KEY.format(user_id=current_user.id))
        await cache.invalidate(TODOS_COMPLETED_CACHE_KEY.format(user_id=current_user.id, completed=True))
        await cache.invalidate(TODOS_COMPLETED_CACHE_KEY.format(user_id=current_user.id, completed=False))
        await cache.invalidate(TODO_CACHE_KEY.format(id=todo_id))

        return {"success": True, "message": "Todo successfully deleted"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
