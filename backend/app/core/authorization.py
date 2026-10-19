import uuid
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.auth import get_current_user
from app.db import get_db
from app.models.membership import BusinessMembership
from app.models.roles import Role
from app.models.users import User


def get_current_membership(
    business_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BusinessMembership:
    statement = (
        select(BusinessMembership)
        .where(
            BusinessMembership.user_id == current_user.id,
            BusinessMembership.business_id == business_id,
        )
        .options(
            selectinload(
                BusinessMembership.role
            ).selectinload(
                Role.permissions
            )
        )
    )

    membership = db.scalar(statement)

    if membership is None:
        # Deliberately don't reveal whether the business exists.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )

    return membership


def require_permission(permission_code: str) -> Callable:
    def dependency(
        membership: BusinessMembership = Depends(
            get_current_membership
        ),
    ) -> BusinessMembership:
        has_permission = any(
            permission.code == permission_code
            for permission in membership.role.permissions
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )

        return membership

    return dependency