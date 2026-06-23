# app/scripts/create_superuser.py
from datetime import datetime, timezone
from getpass import getpass

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.user import User
from app.models.enums import UserRole
from app.core.security import hash_password


def main():
    db = SessionLocal()

    try:
        email = input("Email: ").strip().lower()
        password = getpass("Password: ")
        name = input("Name: ").strip()

        existing_user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing_user:
            print("User already exists.")
            return

        far_future = datetime(2099, 12, 31, tzinfo=timezone.utc)

        user = User(
            org_id=1,  # must exist in orgs table
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.admin,
            employee_no="ADMIN-001",
            position="System Admin",
            aircraft_type="N/A",
            medical_expires_at=far_future,
            passport_expires_at=far_future,
            license_expires_at=far_future,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"Superuser created successfully. id={user.id}, email={user.email}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
