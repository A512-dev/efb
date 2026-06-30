"""Shared enum values persisted by SQLAlchemy and exposed by the API.

Subclassing ``str`` makes enum members serialize naturally in JSON while still
giving Python code a closed, typo-resistant set of values. Changing persisted
values requires a database migration because PostgreSQL stores native enums.
"""

import enum


class UserRole(str, enum.Enum):
    """Roles used for authorization decisions across the API.

    Route dependencies compare these members directly, and SQLAlchemy maps them
    to PostgreSQL's ``user_role`` enum.
    """

    pilot = "pilot"
    admin = "admin"
    safety = "safety"
    planning = "planning"
    technical = "technical"
    chief_pilot = "chief_pilot"


class ManualAction(str, enum.Enum):
    """Audit actions that can be recorded for manual access."""

    view = "view"
    download = "download"


class AircraftType(str, enum.Enum):
    """Aircraft/fleet values stored on user profiles."""

    A330 = "A330"
    A300_A600_A310 = "A300-A600/A310"
    A320 = "A320"
    F100 = "F100"
    ATR72_600 = "ATR72-600"
    UNKNOWN = "N/A"


DEFAULT_FLEET_AIRCRAFT_TYPE = AircraftType.A300_A600_A310
FLEET_AIRCRAFT_TYPES = (
    AircraftType.A330,
    AircraftType.A300_A600_A310,
    AircraftType.A320,
    AircraftType.F100,
    AircraftType.ATR72_600,
)

_AIRCRAFT_TYPE_ALIASES = {
    "A310": AircraftType.A300_A600_A310,
    "A300_600": AircraftType.A300_A600_A310,
    "A300-600/310": AircraftType.A300_A600_A310,
    "A300/600": AircraftType.A300_A600_A310,
    "A300-A600/A310": AircraftType.A300_A600_A310,
    "ATR": AircraftType.ATR72_600,
    "ATR 72-600": AircraftType.ATR72_600,
    "ATR72_600": AircraftType.ATR72_600,
    "ATR72-600": AircraftType.ATR72_600,
}


def normalize_aircraft_type(value: object, *, allow_non_fleet: bool = True) -> str:
    """Return the canonical stored aircraft type or raise ``ValueError``."""
    if isinstance(value, AircraftType):
        aircraft_type = value
    elif isinstance(value, str):
        normalized = value.strip()
        aircraft_type = _AIRCRAFT_TYPE_ALIASES.get(normalized)
        if aircraft_type is None:
            try:
                aircraft_type = AircraftType(normalized)
            except ValueError as exc:
                raise ValueError("Invalid aircraft type") from exc
    else:
        raise ValueError("Invalid aircraft type")

    if not allow_non_fleet and aircraft_type not in FLEET_AIRCRAFT_TYPES:
        raise ValueError("Aircraft type must be a fleet aircraft")
    return aircraft_type.value
