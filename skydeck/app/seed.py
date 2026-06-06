"""
Seed script for SkyDeck development database.

Usage:
    python -m app.seed
"""

import hashlib
import uuid
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import text

from app.db.session import SessionLocal
from app.models.audit_log import AuditLog
from app.models.enums import SubmissionStatus, UserRole
from app.models.form_template import FormTemplate
from app.models.form_version import FormVersion
from app.models.manual import Manual
from app.models.org import Org
from app.models.submission import Submission
from app.models.submission_attachment import SubmissionAttachment
from app.models.user import User


def _hash_password(plain: str) -> str:
    """Hash the shared demo password before inserting seed users."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def _hash_id() -> str:
    """Generate a stable-looking public id for seeded submissions."""
    return hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:32]


def seed() -> None:
    """Populate an empty development database with demo aviation data."""
    db = SessionLocal()

    try:
        # ── guard: skip if already seeded ──────────────────
        existing = db.execute(text("SELECT count(*) FROM orgs")).scalar()
        if existing and existing > 0:
            print("[seed] Database already contains data — skipping.")
            return

        now = datetime.now(timezone.utc)

        # ────────────────────────────────────────────────────
        # 1. Organisation
        # ────────────────────────────────────────────────────
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

        # ────────────────────────────────────────────────────
        # 2. Users (1 admin + 1 chief_pilot + 3 pilots)
        # ────────────────────────────────────────────────────
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
        for u in users_data:
            user = User(
                org_id=org.id,
                name=u["name"],
                email=u["email"],
                password_hash=password_hash,
                role=u["role"],
            )
            db.add(user)
            users.append(user)

        db.flush()
        for u in users:
            print(f"[seed] Created user: {u.name} ({u.role.value}) id={u.id}")

        admin, chief_pilot, pilot_1, pilot_2, pilot_3 = users

        # ────────────────────────────────────────────────────
        # 3. Manuals (4 documents)
        # ────────────────────────────────────────────────────
        manuals_data = [
            {
                "title": "Standard Operating Procedures (SOP) – CRJ-700",
                "storage_path": "/docs/manuals/sop-crj700-v3.pdf",
                "original_filename": "SOP_CRJ700_Rev3.pdf",
                "mime_type": "application/pdf",
                "file_size": 4_521_984,
                "sha256": hashlib.sha256(b"sop-crj700-v3").hexdigest(),
                "version_number": 3,
                "uploaded_by": admin.id,
            },
            {
                "title": "Emergency & Abnormal Checklist – ERJ-175",
                "storage_path": "/docs/manuals/emergency-erj175-v2.pdf",
                "original_filename": "Emergency_Checklist_ERJ175_Rev2.pdf",
                "mime_type": "application/pdf",
                "file_size": 1_835_008,
                "sha256": hashlib.sha256(b"emergency-erj175-v2").hexdigest(),
                "version_number": 2,
                "uploaded_by": chief_pilot.id,
            },
            {
                "title": "Minimum Equipment List (MEL) – CRJ-200",
                "storage_path": "/docs/manuals/mel-crj200-v5.pdf",
                "original_filename": "MEL_CRJ200_Rev5.pdf",
                "mime_type": "application/pdf",
                "file_size": 2_097_152,
                "sha256": hashlib.sha256(b"mel-crj200-v5").hexdigest(),
                "version_number": 5,
                "uploaded_by": admin.id,
            },
            {
                "title": "Weight & Balance Manual – Fleet Wide",
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
        for m in manuals_data:
            manual = Manual(org_id=org.id, **m)
            db.add(manual)
            manuals.append(manual)

        db.flush()
        for m in manuals:
            print(f"[seed] Created manual: {m.title} (id={m.id})")

        # ────────────────────────────────────────────────────
        # 4. Form Templates (2) + Versions
        # ────────────────────────────────────────────────────
        tpl_preflight = FormTemplate(org_id=org.id, name="Pre-Flight Inspection Report")
        tpl_safety = FormTemplate(org_id=org.id, name="Safety Occurrence Report")
        db.add_all([tpl_preflight, tpl_safety])
        db.flush()
        print(f"[seed] Created form template: {tpl_preflight.name} (id={tpl_preflight.id})")
        print(f"[seed] Created form template: {tpl_safety.name} (id={tpl_safety.id})")

        # Pre-Flight v1
        fv_preflight_v1 = FormVersion(
            template_id=tpl_preflight.id,
            version_number=1,
            schema_json={
                "title": "Pre-Flight Inspection Report v1",
                "fields": [
                    {"name": "aircraft_registration", "type": "text", "required": True},
                    {
                        "name": "aircraft_type",
                        "type": "select",
                        "options": ["CRJ-200", "CRJ-700", "ERJ-175"],
                        "required": True,
                    },
                    {"name": "flight_number", "type": "text", "required": True},
                    {"name": "departure_airport", "type": "text", "required": True},
                    {"name": "arrival_airport", "type": "text", "required": True},
                    {
                        "name": "exterior_walkaround",
                        "type": "checklist",
                        "items": [
                            "Fuselage condition",
                            "Wing surfaces",
                            "Landing gear",
                            "Engine inlets",
                            "Pitot tubes",
                            "Navigation lights",
                        ],
                        "required": True,
                    },
                    {
                        "name": "cockpit_check",
                        "type": "checklist",
                        "items": [
                            "Flight instruments",
                            "Avionics power",
                            "Fuel quantity",
                            "Hydraulic pressure",
                            "Fire detection",
                            "Oxygen supply",
                        ],
                        "required": True,
                    },
                    {"name": "remarks", "type": "textarea", "required": False},
                    {"name": "pilot_signature", "type": "signature", "required": True},
                ],
            },
        )

        # Pre-Flight v2
        fv_preflight_v2 = FormVersion(
            template_id=tpl_preflight.id,
            version_number=2,
            schema_json={
                "title": "Pre-Flight Inspection Report v2",
                "fields": [
                    {"name": "aircraft_registration", "type": "text", "required": True},
                    {
                        "name": "aircraft_type",
                        "type": "select",
                        "options": ["CRJ-200", "CRJ-700", "ERJ-175"],
                        "required": True,
                    },
                    {"name": "flight_number", "type": "text", "required": True},
                    {"name": "departure_airport", "type": "text", "required": True},
                    {"name": "arrival_airport", "type": "text", "required": True},
                    {"name": "scheduled_departure", "type": "datetime", "required": True},
                    {
                        "name": "exterior_walkaround",
                        "type": "checklist",
                        "items": [
                            "Fuselage condition",
                            "Wing surfaces",
                            "Landing gear",
                            "Engine inlets",
                            "Pitot tubes",
                            "Navigation lights",
                            "De-icing status",
                        ],
                        "required": True,
                    },
                    {
                        "name": "cockpit_check",
                        "type": "checklist",
                        "items": [
                            "Flight instruments",
                            "Avionics power",
                            "Fuel quantity",
                            "Hydraulic pressure",
                            "Fire detection",
                            "Oxygen supply",
                            "TCAS operational",
                            "Weather radar",
                        ],
                        "required": True,
                    },
                    {"name": "fuel_quantity_lbs", "type": "number", "required": True},
                    {"name": "remarks", "type": "textarea", "required": False},
                    {"name": "pilot_signature", "type": "signature", "required": True},
                ],
            },
        )

        # Safety Occurrence v1
        fv_safety_v1 = FormVersion(
            template_id=tpl_safety.id,
            version_number=1,
            schema_json={
                "title": "Safety Occurrence Report v1",
                "fields": [
                    {"name": "occurrence_date", "type": "date", "required": True},
                    {"name": "occurrence_time_utc", "type": "time", "required": True},
                    {
                        "name": "flight_phase",
                        "type": "select",
                        "options": [
                            "Taxi",
                            "Takeoff",
                            "Climb",
                            "Cruise",
                            "Descent",
                            "Approach",
                            "Landing",
                            "Ground",
                        ],
                        "required": True,
                    },
                    {
                        "name": "occurrence_type",
                        "type": "select",
                        "options": [
                            "Bird strike",
                            "Turbulence",
                            "Go-around",
                            "TCAS RA",
                            "Equipment malfunction",
                            "Runway incursion",
                            "Near miss",
                            "Other",
                        ],
                        "required": True,
                    },
                    {
                        "name": "severity",
                        "type": "select",
                        "options": ["Low", "Medium", "High", "Critical"],
                        "required": True,
                    },
                    {"name": "aircraft_registration", "type": "text", "required": True},
                    {"name": "location", "type": "text", "required": True},
                    {"name": "description", "type": "textarea", "required": True},
                    {"name": "immediate_action_taken", "type": "textarea", "required": False},
                    {"name": "attachments", "type": "file", "multiple": True, "required": False},
                ],
            },
        )

        db.add_all([fv_preflight_v1, fv_preflight_v2, fv_safety_v1])
        db.flush()
        print(
            f"[seed] Created form versions: Pre-Flight v1 (id={fv_preflight_v1.id}), "
            f"Pre-Flight v2 (id={fv_preflight_v2.id}), Safety v1 (id={fv_safety_v1.id})"
        )

        # ────────────────────────────────────────────────────
        # 5. Submissions (3 sample)
        # ────────────────────────────────────────────────────
        sub_1 = Submission(
            org_id=org.id,
            user_id=pilot_1.id,
            form_version_id=fv_preflight_v2.id,
            data_json={
                "aircraft_registration": "N728SK",
                "aircraft_type": "CRJ-700",
                "flight_number": "SKW5421",
                "departure_airport": "KSLC",
                "arrival_airport": "KDEN",
                "scheduled_departure": "2026-02-22T06:30:00Z",
                "exterior_walkaround": {
                    "Fuselage condition": True,
                    "Wing surfaces": True,
                    "Landing gear": True,
                    "Engine inlets": True,
                    "Pitot tubes": True,
                    "Navigation lights": True,
                    "De-icing status": True,
                },
                "cockpit_check": {
                    "Flight instruments": True,
                    "Avionics power": True,
                    "Fuel quantity": True,
                    "Hydraulic pressure": True,
                    "Fire detection": True,
                    "Oxygen supply": True,
                    "TCAS operational": True,
                    "Weather radar": True,
                },
                "fuel_quantity_lbs": 12400,
                "remarks": "Light frost on wings, de-icing completed at 05:45Z.",
                "pilot_signature": "achen_sig_202602220630",
            },
            status=SubmissionStatus.submitted,
            hash_id=_hash_id(),
            ip="10.0.1.42",
            device_info_json={"platform": "iPad", "app_version": "1.2.0"},
            submitted_at=now,
        )

        sub_2 = Submission(
            org_id=org.id,
            user_id=pilot_3.id,
            form_version_id=fv_preflight_v2.id,
            data_json={
                "aircraft_registration": "N614SK",
                "aircraft_type": "ERJ-175",
                "flight_number": "SKW3287",
                "departure_airport": "KORD",
                "arrival_airport": "KMSP",
                "scheduled_departure": "2026-02-22T14:15:00Z",
                "exterior_walkaround": {
                    "Fuselage condition": True,
                    "Wing surfaces": True,
                    "Landing gear": True,
                    "Engine inlets": True,
                    "Pitot tubes": True,
                    "Navigation lights": True,
                    "De-icing status": False,
                },
                "cockpit_check": {
                    "Flight instruments": True,
                    "Avionics power": True,
                    "Fuel quantity": True,
                    "Hydraulic pressure": True,
                    "Fire detection": True,
                    "Oxygen supply": True,
                    "TCAS operational": True,
                    "Weather radar": True,
                },
                "fuel_quantity_lbs": 9800,
                "remarks": "De-icing not required — clear conditions at KORD.",
                "pilot_signature": "nokonkwo_sig_202602221415",
            },
            status=SubmissionStatus.pending,
            hash_id=_hash_id(),
            ip="10.0.2.18",
            device_info_json={"platform": "iPad", "app_version": "1.2.0"},
        )

        sub_3 = Submission(
            org_id=org.id,
            user_id=pilot_2.id,
            form_version_id=fv_safety_v1.id,
            data_json={
                "occurrence_date": "2026-02-21",
                "occurrence_time_utc": "17:42",
                "flight_phase": "Approach",
                "occurrence_type": "Bird strike",
                "severity": "Medium",
                "aircraft_registration": "N523SK",
                "location": "KSLC RWY 34L, 500ft AGL",
                "description": (
                    "Bird strike on left engine during final approach to RWY 34L. "
                    "Single bird impact, engine parameters remained normal. "
                    "Aircraft landed safely. Post-flight inspection revealed "
                    "minor dent on engine cowling, no FOD ingestion."
                ),
                "immediate_action_taken": (
                    "Continued approach and landed normally. Notified ATC of bird strike. "
                    "Reported to maintenance for engine borescope inspection."
                ),
            },
            status=SubmissionStatus.submitted,
            hash_id=_hash_id(),
            ip="10.0.1.55",
            device_info_json={"platform": "Android", "app_version": "1.1.9"},
            submitted_at=now,
        )

        db.add_all([sub_1, sub_2, sub_3])
        db.flush()
        print(f"[seed] Created 3 submissions (ids={sub_1.id}, {sub_2.id}, {sub_3.id})")

        # Attachment on the safety occurrence report
        attachment = SubmissionAttachment(
            submission_id=sub_3.id,
            storage_path="/uploads/submissions/bird-strike-evidence-n523sk.jpg",
            original_filename="engine_cowling_dent_N523SK.jpg",
            mime_type="image/jpeg",
            file_size=2_458_624,
            sha256=hashlib.sha256(b"bird-strike-photo-n523sk").hexdigest(),
            attachment_type="photo_evidence",
        )
        db.add(attachment)
        db.flush()
        print(f"[seed] Created attachment on submission {sub_3.id}")

        # ────────────────────────────────────────────────────
        # 6. Audit log entry for seeding
        # ────────────────────────────────────────────────────
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
