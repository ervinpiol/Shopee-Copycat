from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.db import get_async_session
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoRead, TodoUpdate
from typing import Optional
from app.routes.users import fastapi_users
from app.models.users import User

from redis.asyncio import Redis
import json
from app.core.redis import get_redis

router = APIRouter(prefix="/todo", tags=["Todo"])

CACHE_TTL = 300  # 5 minutes
TODOS_CACHE_KEY = "todos:all"
TODO_CACHE_KEY = "todos:{id}"


async def invalidate_todos_cache(redis: Redis, user_id: int) -> None:
    """Invalidate todo list cache for a user"""
    # Invalidate all possible cached lists for the user
    await redis.delete(f"todos:{user_id}:all")
    await redis.delete(f"todos:{user_id}:completed:true")
    await redis.delete(f"todos:{user_id}:completed:false")


@router.get("", response_model=List[TodoRead])
async def get_todos(
    completed: Optional[bool] = None,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user()),
    redis: Redis = Depends(get_redis)
):
    try:
        # Create a cache key that includes user_id and completed filter
        cache_key = f"todos:{current_user.id}:all" if completed is None else f"todos:{current_user.id}:completed:{completed}"

        cached = await redis.get(cache_key)
        if cached:
            return [TodoRead(**t) for t in json.loads(cached)]

        query = select(Todo).where(Todo.owner_id == current_user.id)
        if completed is not None:
            query = query.where(Todo.completed == completed)

        result = await session.execute(query)
        todos = result.scalars().all()

        # 3️⃣ Serialize and store in Redis
        data = [TodoRead.model_validate(t).model_dump() for t in todos]
        await redis.setex(cache_key, CACHE_TTL, json.dumps(data))

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
        cache_key = TODO_CACHE_KEY.format(id=todo_id, user_id=current_user.id)

        # Check cache first
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Fetch from DB
        todo = await session.get(Todo, todo_id)
        if not todo or todo.owner_id != current_user.id:
            raise HTTPException(status_code=404, detail="Todo not found")

        # Serialize and cache
        data = TodoRead.model_validate(todo).model_dump()
        await redis.setex(cache_key, CACHE_TTL, json.dumps(data))

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
        todo = Todo(
            **todo_create.model_dump(exclude_unset=True),
            owner_id=current_user.id
        )

        session.add(todo)
        await session.commit()
        await session.refresh(todo)

        await invalidate_todos_cache(redis, current_user.id)

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
        todo = await session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        # Ownership check
        if todo.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this todo")
        
        update_data = todo_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(todo, key, value)

        await session.commit()
        await session.refresh(todo)

        await invalidate_todos_cache(redis, current_user.id)
        await redis.delete(TODO_CACHE_KEY.format(id=todo_id))

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
        todo = await session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")

        # Ownership check
        if todo.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this todo")
        
        await session.delete(todo)
        await session.commit()

        await invalidate_todos_cache(redis, current_user.id)
        await redis.delete(TODO_CACHE_KEY.format(id=todo_id))

        return {"success": True, "message": "Todo successfully deleted"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
