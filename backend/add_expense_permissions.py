from sqlalchemy import select

from app.db import SessionLocal
from app.models.roles import Role
from app.models.permissions import Permission

EXPENSE_PERMISSIONS = [
    ("expenses:read", "View expenses and expense reports"),
    ("expenses:create", "Record expenses"),
    ("expenses:update", "Update expenses"),
    ("expenses:delete", "Delete expenses"),
]

with SessionLocal() as db:
    admin_role = db.scalar(
        select(Role).where(Role.name == "ADMIN")
    )

    if admin_role is None:
        raise RuntimeError("ADMIN role not found")

    for code, description in EXPENSE_PERMISSIONS:
        permission = db.scalar(
            select(Permission).where(Permission.code == code)
        )

        if permission is None:
            permission = Permission(
                code=code,
                description=description,
            )
            db.add(permission)
            db.flush()

        if permission not in admin_role.permissions:
            admin_role.permissions.append(permission)

    db.commit()
    print("Expenses permissions assigned to ADMIN successfully.")
