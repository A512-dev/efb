"""Manual category visibility based on user aircraft type."""

from __future__ import annotations

from app.models.enums import UserRole
from app.models.manual import Manual
from app.models.manual_category import ManualCategory
from app.models.manual_update_event import ManualUpdateEvent
from app.models.user import User
from app.repositories import manual_category_repo
from app.services.manual_category_service import (
    FLEET_ROOT_SLUG_BY_AIRCRAFT_TYPE,
    GENERAL_MANUAL_CATEGORY_ROOT,
)

_RESTRICTED_ROLES = {UserRole.pilot, UserRole.chief_pilot}


def user_is_fleet_restricted(user: User) -> bool:
    """Return whether manual visibility should follow the user's fleet."""
    return user.role in _RESTRICTED_ROLES


def allowed_root_slugs(user: User) -> set[str] | None:
    """Return allowed root slugs, or ``None`` for unrestricted users."""
    if not user_is_fleet_restricted(user):
        return None

    slugs = {GENERAL_MANUAL_CATEGORY_ROOT["slug"]}
    fleet_slug = FLEET_ROOT_SLUG_BY_AIRCRAFT_TYPE.get(user.aircraft_type)
    if fleet_slug is not None:
        slugs.add(fleet_slug)
    return slugs


def category_root(category: ManualCategory) -> ManualCategory:
    """Return the root category for any category node."""
    return manual_category_repo.get_path(category)[0]


def can_access_category(user: User, category: ManualCategory) -> bool:
    """Return whether a user may browse or select this category."""
    slugs = allowed_root_slugs(user)
    if slugs is None:
        return True
    return category_root(category).slug in slugs


def filter_categories(user: User, categories: list[ManualCategory]) -> list[ManualCategory]:
    """Remove categories outside the caller's visible root set."""
    slugs = allowed_root_slugs(user)
    if slugs is None:
        return categories
    return [category for category in categories if category_root(category).slug in slugs]


def can_access_manual(user: User, manual: Manual) -> bool:
    """Return whether a user may see/read/download this manual."""
    return can_access_category(user, manual.category)


def filter_manuals(user: User, manuals: list[Manual]) -> list[Manual]:
    """Remove manuals outside the caller's visible fleet/general roots."""
    if allowed_root_slugs(user) is None:
        return manuals
    return [manual for manual in manuals if can_access_manual(user, manual)]


def can_access_update_event(user: User, item: ManualUpdateEvent) -> bool:
    """Return whether the update event belongs to a visible manual."""
    if allowed_root_slugs(user) is None:
        return True
    if item.manual is None:
        return False
    return can_access_manual(user, item.manual)


def filter_update_events(user: User, items: list[ManualUpdateEvent]) -> list[ManualUpdateEvent]:
    """Remove manual update events for hidden fleets."""
    if allowed_root_slugs(user) is None:
        return items
    return [item for item in items if can_access_update_event(user, item)]
