"""Short-term (session) and long-term (persisted) traveler memory."""
import json
import os
from dataclasses import asdict
from typing import Optional

LONG_TERM_STORE_PATH = os.path.join("memory", "long_term_store.json")

LONG_TERM_FIELDS = (
    "accommodation_preference",
    "food_preference",
    "transportation_preference",
    "travel_style",
    "accessibility_requirements",
)


class MemoryManager:
    """Wraps a TripInfo instance (short-term) and a JSON file (long-term)."""

    def __init__(self, user_id: str, store_path: str = LONG_TERM_STORE_PATH):
        self.user_id = user_id
        self.store_path = store_path

    def _read_store(self) -> dict:
        if not os.path.exists(self.store_path):
            return {}
        with open(self.store_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _write_store(self, data: dict) -> None:
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True)
        with open(self.store_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_long_term_preferences(self) -> dict:
        return self._read_store().get(self.user_id, {})

    def apply_long_term_preferences(self, trip_info) -> None:
        prefs = self.load_long_term_preferences()
        if prefs:
            trip_info.update(**prefs)

    def save_long_term_preferences(self, trip_info) -> None:
        store = self._read_store()
        existing = store.get(self.user_id, {})
        trip_dict = asdict(trip_info)
        for field in LONG_TERM_FIELDS:
            value = trip_dict.get(field)
            if value:
                existing[field] = value
        store[self.user_id] = existing
        self._write_store(store)
