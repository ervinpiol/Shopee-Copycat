from fastapi import Depends, HTTPException, status
from app.models.users import User
from app.routes.users import current_active_user

def admin_required(
    user: User = Depends(current_active_user),
) -> User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


def seller_required(
    user: User = Depends(current_active_user),
) -> User:
    if user.role != "seller":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User role must be seller",
        )
    return user
