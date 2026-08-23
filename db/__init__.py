"""RoadGuardian Database Package."""
from .footage_store import (
    init,
    list_footage,
    get_footage_by_id,
    save_incident,
    list_saved_incidents,
    get_saved_incident,
    FootageStoreUnavailable
)
from .storage_backend import resolve_storage_key

__all__ = [
    "init",
    "list_footage",
    "get_footage_by_id",
    "save_incident",
    "list_saved_incidents",
    "get_saved_incident",
    "FootageStoreUnavailable",
    "resolve_storage_key"
]
