from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db import get_db
from app.models.users import User
from app.schemas.auth import LoginRequest, TokenResponse, UserRead

from app.core.auth import get_current_user

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

@router.get("/me", response_model=UserRead)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserRead(
        id=str(current_user.id),
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
    )


@router.post("/login", response_model=TokenResponse)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    statement = select(User).where(User.email == data.email)

    user = db.scalar(statement)

    if user is None or not verify_password(
        data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
        user=UserRead(
            id=str(user.id),
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        ),
    )