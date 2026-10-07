import argparse
import getpass

from app.db import SessionLocal
from app.services.bootstrap import bootstrap_system

def parse_args():
    parser = argparse.ArgumentParser(
        description="Initialize the Salon Management System."
    )

    parser.add_argument(
        "--business-name",
        required=True,
        help="Name of the first salon business.",
    )

    parser.add_argument(
        "--admin-email",
        required=True,
        help="Administrator email address.",
    )

    parser.add_argument(
        "--first-name",
        required=True,
        help="Administrator first name.",
    )

    parser.add_argument(
        "--last-name",
        required=True,
        help="Administrator last name.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    password = getpass.getpass(
        "Admin password: "
    )

    password_confirmation = getpass.getpass(
        "Confirm admin password: "
    )

    if password != password_confirmation:
        raise SystemExit(
            "Passwords do not match."
        )

    if len(password) < 8:
        raise SystemExit(
            "Password must contain at least 8 characters."
        )

    db = SessionLocal()

    try:
        business, admin = bootstrap_system(
            db,
            business_name=args.business_name,
            admin_email=args.admin_email,
            admin_password=password,
            admin_first_name=args.first_name,
            admin_last_name=args.last_name,
        )

        print()
        print("Bootstrap completed successfully.")
        print()
        print(f"Business : {business.name}")
        print(f"Admin    : {admin.email}")
        print()
        print("Default roles created:")
        print("  - ADMIN")
        print("  - MANAGER")
        print("  - RECEPTIONIST")
        print()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()