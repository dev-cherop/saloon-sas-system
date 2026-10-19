from sqlalchemy import select

from app.core.default_permissions import DEFAULT_PERMISSIONS
from app.db import SessionLocal
from app.models.permissions import Permission
from app.models.roles import Role

LOYALTY_CODES = {
    "loyalty:read",
    "loyalty:earn",
    "loyalty:redeem",
    "loyalty:manage",
}


def main():
    descriptions = {
        code: description
        for code, description in DEFAULT_PERMISSIONS
        if code in LOYALTY_CODES
    }

    with SessionLocal() as db:
        admin_role = db.scalar(
            select(Role).where(Role.name == "ADMIN")
        )

        if admin_role is None:
            raise RuntimeError("ADMIN role was not found.")

        for code, description in descriptions.items():
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

        print("Loyalty permissions synchronized for ADMIN:")
        for permission in sorted(
            admin_role.permissions,
            key=lambda item: item.code,
        ):
            if permission.code in LOYALTY_CODES:
                print(f"  {permission.code}")


if __name__ == "__main__":
    main()