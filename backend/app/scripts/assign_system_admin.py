import sys

from sqlalchemy import select

from app.db import SessionLocal
from app.models.system_permissions import SystemRole
from app.models.users import User


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python -m app.scripts.assign_system_admin "
            "<user-email>"
        )
        raise SystemExit(1)

    email = sys.argv[1].strip().lower()

    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(User.email == email)
        )

        if user is None:
            print(f"No user found with email: {email}")
            raise SystemExit(1)

        if not user.is_active:
            print("Cannot assign system admin to an inactive user.")
            raise SystemExit(1)

        role = db.scalar(
            select(SystemRole).where(
                SystemRole.name == "System Administrator"
            )
        )

        if role is None:
            print("System Administrator role not found.")
            raise SystemExit(1)

        if role not in user.system_roles:
            user.system_roles.append(role)
            db.commit()
            print(f"System Administrator assigned to {email}.")
        else:
            print(f"{email} already has the system role.")


if __name__ == "__main__":
    main()
