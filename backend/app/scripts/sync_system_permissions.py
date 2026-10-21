from sqlalchemy import select

from app.core.default_permissions import (
    DEFAULT_SYSTEM_PERMISSIONS,
)
from app.db import SessionLocal
from app.models.system_permissions import (
    SystemPermission,
    SystemRole,
)


SYSTEM_ROLE_NAME = "System Administrator"


def main():
    with SessionLocal() as db:
        permissions = {}

        for code, description in DEFAULT_SYSTEM_PERMISSIONS:
            permission = db.scalar(
                select(SystemPermission).where(
                    SystemPermission.code == code
                )
            )

            if permission is None:
                permission = SystemPermission(
                    code=code,
                    description=description,
                )
                db.add(permission)
                db.flush()

            permissions[code] = permission

        role = db.scalar(
            select(SystemRole).where(
                SystemRole.name == SYSTEM_ROLE_NAME
            )
        )

        if role is None:
            role = SystemRole(
                name=SYSTEM_ROLE_NAME,
                description=(
                    "Platform-level administration permissions"
                ),
            )
            db.add(role)
            db.flush()

        for permission in permissions.values():
            if permission not in role.permissions:
                role.permissions.append(permission)

        db.commit()

        print("System permissions synchronized.")
        print(f"Role ready: {SYSTEM_ROLE_NAME}")
        print("No users were assigned this role.")


if __name__ == "__main__":
    main()
