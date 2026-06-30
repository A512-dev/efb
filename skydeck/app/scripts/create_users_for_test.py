# app/scripts/create_users_for_test.py
from datetime import datetime
from getpass import getpass

from sqlalchemy import select, func

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

        # 1. Handle Role selection via numbered list
        roles = list(UserRole)
        print("\nSelect a role:")
        for idx, role in enumerate(roles, 1):
            print(f"{idx}. {role.value}")
        
        choice = int(input("Enter role number: ")) - 1
        selected_role = roles[choice]

        position = input("Position in system: ").strip()

        # 2. Check for existing user
        existing_user = db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()

        if existing_user:
            print("User already exists.")
            return

        # 3. Generate employee_no: ROLE0000X
        # Count existing users with this role to determine the next number
        count = db.execute(
            select(func.count(User.id)).where(User.role == selected_role)
        ).scalar() or 0
        
        employee_no = f"{selected_role.value.upper()}{str(count + 1).zfill(5)}"

        now = datetime.now()

        user = User(
            org_id=1,
            name=name,
            email=email,
            password_hash=hash_password(password),
            role=selected_role,
            employee_no=employee_no,
            position=position,
            aircraft_type="N/A",
            medical_expires_at=now,
            passport_expires_at=now,
            license_expires_at=now,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        print(f"\nUser created successfully!")
        print(f"ID: {user.id}, Email: {user.email}, Employee No: {user.employee_no}")

    except (ValueError, IndexError):
        print("Invalid input selection.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
