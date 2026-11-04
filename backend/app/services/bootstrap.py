import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.default_permissions import DEFAULT_PERMISSIONS
from app.core.security import hash_password
from app.models.business import Business
from app.models.membership import BusinessMembership
from app.models.permissions import Permission
from app.models.roles import Role
from app.models.users import User


DEFAULT_ROLES = {
    "ADMIN": [
        permission_code
        for permission_code, _ in DEFAULT_PERMISSIONS
    ],
    "MANAGER": [
        "customers:read",
        "customers:create",
        "customers:update",
        "customers:delete",
        "services:read",
        "services:create",
        "services:update",
        "reports:read",
        "expenses:read",
        "expenses:create",
        "expenses:update",
        "payments:read",
        "payments:create",
        "payroll:read",
        "payroll:create",
        "payroll:update",

    ],
    "RECEPTIONIST": [
        "customers:read",
        "customers:create",
        "customers:update",
        "services:read",
        
    ],
}


def bootstrap_system(
    db: Session,
    *,
    business_name: str,
    admin_email: str,
    admin_password: str,
    admin_first_name: str,
    admin_last_name: str,
) -> tuple[Business, User]:

    existing_user = db.scalar(select(User).limit(1))

    if existing_user is not None:
        raise RuntimeError(
            "The system already has a user. "
            "Bootstrap should only be used for the initial setup."
        )

    # ---------------------------------------------------------
    # Business
    # ---------------------------------------------------------

    business = db.scalar(
        select(Business).limit(1)
    )

    if business is None:
        business = Business(
            name=business_name,
            is_active=True,
        )

        db.add(business)
        db.flush()

    # ---------------------------------------------------------
    # Permissions
    # ---------------------------------------------------------

    permissions_by_code: dict[str, Permission] = {}

    for code, description in DEFAULT_PERMISSIONS:
        permission = db.scalar(
            select(Permission).where(
                Permission.code == code
            )
        )

        if permission is None:
            permission = Permission(
                code=code,
                description=description,
            )

            db.add(permission)
            db.flush()

        permissions_by_code[code] = permission

    # ---------------------------------------------------------
    # Roles
    # ---------------------------------------------------------

    roles_by_name: dict[str, Role] = {}

    for role_name, permission_codes in DEFAULT_ROLES.items():
        role = db.scalar(
            select(Role).where(
                Role.name == role_name
            )
        )

        if role is None:
            role = Role(
                name=role_name,
                description=f"Default {role_name.lower()} role",
            )

            db.add(role)
            db.flush()

        role.permissions = [
            permissions_by_code[code]
            for code in permission_codes
        ]

        roles_by_name[role_name] = role

    db.flush()

    # ---------------------------------------------------------
    # Administrator
    # ---------------------------------------------------------

    admin = User(
        email=admin_email.lower().strip(),
        password_hash=hash_password(admin_password),
        first_name=admin_first_name,
        last_name=admin_last_name,
        is_active=True,
    )

    db.add(admin)
    db.flush()

    # ---------------------------------------------------------
    # Business membership
    # ---------------------------------------------------------

    membership = BusinessMembership(
        user_id=admin.id,
        business_id=business.id,
        role_id=roles_by_name["ADMIN"].id,
    )

    db.add(membership)

    # ---------------------------------------------------------
    # Commit everything together
    # ---------------------------------------------------------

    db.commit()

    db.refresh(business)
    db.refresh(admin)

    return business, admin