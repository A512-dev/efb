"""
Seed script for SkyDeck development database.

Usage:
    python -m app.seed
"""

import hashlib
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import text

from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from app.models.manual import Manual
from app.models.org import Org
from app.models.user import User


def _hash_password(plain: str) -> str:
    """Hash the shared demo password before inserting seed users."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _add_years(value: datetime, years: int) -> datetime:
    """Add whole years while keeping leap-day dates valid."""
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(month=2, day=28, year=value.year + years)


def _default_position(name: str, role: UserRole) -> str:
    """Infer a display position for seeded demo users."""
    if role == UserRole.admin:
        return "Admin"
    if role == UserRole.chief_pilot:
        return "Chief Pilot"
    if role == UserRole.pilot and name.strip().lower().startswith("captain"):
        return "Captain"
    if role == UserRole.pilot:
        return "P2"
    return role.value.replace("_", " ").title()


def seed() -> None:
    """Populate an empty development database with demo aviation data."""
    db = SessionLocal()

    try:
        existing = db.execute(text("SELECT count(*) FROM orgs")).scalar()
        if existing and existing > 0:
            print("[seed] Database already contains data - skipping.")
            return

        now = datetime.now(timezone.utc)

        org = Org(
            name="SkyWest Regional Airlines",
            settings_json={
                "timezone": "America/Denver",
                "base_airport": "KSLC",
                "fleet_type": ["CRJ-200", "CRJ-700", "ERJ-175"],
                "regulatory_authority": "FAA",
            },
        )
        db.add(org)
        db.flush()
        print(f"[seed] Created org: {org.name} (id={org.id})")

        password_hash = _hash_password("SkyDeck@2026!")
        users_data = [
            {
                "name": "Sarah Mitchell",
                "email": "s.mitchell@skywest-air.com",
                "role": UserRole.admin,
            },
            {
                "name": "Captain James Thornton",
                "email": "j.thornton@skywest-air.com",
                "role": UserRole.chief_pilot,
            },
            {
                "name": "First Officer Ava Chen",
                "email": "a.chen@skywest-air.com",
                "role": UserRole.pilot,
            },
            {
                "name": "First Officer Marcus Rivera",
                "email": "m.rivera@skywest-air.com",
                "role": UserRole.pilot,
            },
            {
                "name": "Captain Nadia Okonkwo",
                "email": "n.okonkwo@skywest-air.com",
                "role": UserRole.pilot,
            },
        ]

        users: list[User] = []
        for user_data in users_data:
            user = User(
                org_id=org.id,
                name=user_data["name"],
                email=user_data["email"],
                password_hash=password_hash,
                role=user_data["role"],
                employee_no="pending",
                position=_default_position(user_data["name"], user_data["role"]),
                aircraft_type=(
                    "A310" if user_data["role"] in {UserRole.pilot, UserRole.chief_pilot} else "N/A"
                ),
                medical_expires_at=_add_years(now, 1),
                passport_expires_at=_add_years(now, 5),
                license_expires_at=_add_years(now, 1),
            )
            db.add(user)
            users.append(user)

        db.flush()
        for user in users:
            user.employee_no = str(user.id)
        db.flush()
        for user in users:
            print(f"[seed] Created user: {user.name} ({user.role.value}) id={user.id}")

        admin, chief_pilot = users[0], users[1]

        manuals_data = [
            {
                "title": "Standard Operating Procedures (SOP) - CRJ-700",
                "storage_path": "/docs/manuals/sop-crj700-v3.pdf",
                "original_filename": "SOP_CRJ700_Rev3.pdf",
                "mime_type": "application/pdf",
                "file_size": 4_521_984,
                "sha256": hashlib.sha256(b"sop-crj700-v3").hexdigest(),
                "version_number": 3,
                "uploaded_by": admin.id,
            },
            {
                "title": "Emergency & Abnormal Checklist - ERJ-175",
                "storage_path": "/docs/manuals/emergency-erj175-v2.pdf",
                "original_filename": "Emergency_Checklist_ERJ175_Rev2.pdf",
                "mime_type": "application/pdf",
                "file_size": 1_835_008,
                "sha256": hashlib.sha256(b"emergency-erj175-v2").hexdigest(),
                "version_number": 2,
                "uploaded_by": chief_pilot.id,
            },
            {
                "title": "Minimum Equipment List (MEL) - CRJ-200",
                "storage_path": "/docs/manuals/mel-crj200-v5.pdf",
                "original_filename": "MEL_CRJ200_Rev5.pdf",
                "mime_type": "application/pdf",
                "file_size": 2_097_152,
                "sha256": hashlib.sha256(b"mel-crj200-v5").hexdigest(),
                "version_number": 5,
                "uploaded_by": admin.id,
            },
            {
                "title": "Weight & Balance Manual - Fleet Wide",
                "storage_path": "/docs/manuals/weight-balance-fleet-v1.pdf",
                "original_filename": "Weight_Balance_Fleet_Rev1.pdf",
                "mime_type": "application/pdf",
                "file_size": 3_145_728,
                "sha256": hashlib.sha256(b"weight-balance-fleet-v1").hexdigest(),
                "version_number": 1,
                "uploaded_by": chief_pilot.id,
            },
        ]

        manuals: list[Manual] = []
        for manual_data in manuals_data:
            manual = Manual(org_id=org.id, **manual_data)
            db.add(manual)
            manuals.append(manual)

        db.flush()
        for manual in manuals:
            print(f"[seed] Created manual: {manual.title} (id={manual.id})")

        audit = AuditLog(
            org_id=org.id,
            user_id=admin.id,
            action="seed",
            target_type="database",
            target_id="initial",
            metadata_json={"seeded_at": now.isoformat(), "script": "app.seed"},
        )
        db.add(audit)

        db.commit()
        print("\n[seed] Database seeded successfully.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
