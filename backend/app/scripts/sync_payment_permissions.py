from sqlalchemy import select

from app.db import SessionLocal
from app.models.permissions import Permission
from app.models.roles import Role


PAYMENT_PERMISSIONS = [
    ("payments:read", "View payments and collection reports"),
    ("payments:create", "Record customer payments"),
]


def sync_payment_permissions():
    with SessionLocal() as db:
        try:
            permissions = {}

            for code, description in PAYMENT_PERMISSIONS:
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

                permissions[code] = permission

            for role_name in ("ADMIN", "MANAGER"):
                role = db.scalar(
                    select(Role)
                    .where(Role.name == role_name)
                )

                if role is None:
                    print(f"Role {role_name} not found; skipping.")
                    continue

                existing_codes = {
                    permission.code for permission in role.permissions
                }

                for code, permission in permissions.items():
                    if code not in existing_codes:
                        role.permissions.append(permission)

                print(f"Updated permissions for {role_name}")

            db.commit()
            print("Payment permission synchronization completed.")

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    sync_payment_permissions()