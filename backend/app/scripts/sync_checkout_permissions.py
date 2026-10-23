from sqlalchemy import select

from app.core.default_permissions import DEFAULT_PERMISSIONS
from app.db import SessionLocal
from app.models.permissions import Permission
from app.models.roles import Role

CHECKOUT_CODES = {
    "checkout:read",
    "checkout:create",
}

ROLE_PERMISSIONS = {
    "ADMIN": CHECKOUT_CODES,
    "MANAGER": CHECKOUT_CODES,
    "RECEPTIONIST": CHECKOUT_CODES,
}


def main():
    descriptions = {
        code: description
        for code, description in DEFAULT_PERMISSIONS
        if code in CHECKOUT_CODES
    }

    with SessionLocal() as db:
        permissions = {}

        for code, description in descriptions.items():
            permission = db.scalar(
                select(Permission).where(Permission.code == code)
            )

            if permission is None:
                permission = Permission(code=code, description=description)
                db.add(permission)
                db.flush()

            permissions[code] = permission

        for role_name, codes in ROLE_PERMISSIONS.items():
            role = db.scalar(select(Role).where(Role.name == role_name))

            if role is None:
                print(f"Skipping missing role: {role_name}")
                continue

            for code in codes:
                permission = permissions[code]
                if permission not in role.permissions:
                    role.permissions.append(permission)

            print(f"checkout permissions synchronized for {role_name}.")

        db.commit()


if __name__ == "__main__":
    main()
