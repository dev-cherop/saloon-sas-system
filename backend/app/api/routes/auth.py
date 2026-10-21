from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload

from app.core.security import create_access_token, verify_password
from app.db import get_db
from app.models.users import User
from app.schemas.auth import LoginRequest, TokenResponse, UserRead,AuthContextRead,BusinessContextRead

from app.core.auth import get_current_user

from app.models.membership import BusinessMembership
from app.models.roles import Role
from app.models.system_permissions import SystemRole

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

@router.get("/me", response_model=AuthContextRead)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = (
        select(BusinessMembership)
        .where(
            BusinessMembership.user_id == current_user.id
        )
        .options(
            selectinload(BusinessMembership.business),
            selectinload(
                BusinessMembership.role
            ).selectinload(Role.permissions),
        )
    )

    memberships = db.scalars(statement).all()

    system_statement = (
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.system_roles).selectinload(
                SystemRole.permissions
            )
        )
    )
    user_with_system_roles = db.scalar(system_statement)
    system_permissions = sorted({
        permission.code
        for role in user_with_system_roles.system_roles
        for permission in role.permissions
    }) if user_with_system_roles else []

    businesses = [
        BusinessContextRead(
            id=membership.business.id,
            name=membership.business.name,
            role=membership.role.name,
            permissions=sorted(
                permission.code
                for permission in membership.role.permissions
            ),
        )
        for membership in memberships
        if membership.business.is_active
    ]

    return AuthContextRead(
        user=UserRead.model_validate(current_user),
        businesses=businesses,
        system_permissions=system_permissions,
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