"""Data models for trip information and itinerary state."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TripInfo:
    """Mandatory and optional traveler-provided trip details."""

    destination: Optional[str] = None
    departure_city: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[str] = None
    travelers_count: Optional[int] = None
    purpose: Optional[str] = None

    interests: list[str] = field(default_factory=list)
    travel_style: Optional[str] = None
    accommodation_preference: Optional[str] = None
    transportation_preference: Optional[str] = None
    food_preference: Optional[str] = None
    accessibility_requirements: Optional[str] = None
    special_requests: Optional[str] = None
    budget_deferred: bool = False

    MANDATORY_FIELDS = (
        "destination",
        "departure_city",
        "start_date",
        "end_date",
        "budget",
        "travelers_count",
        "purpose",
    )

    def missing_mandatory_fields(self) -> list[str]:
        return [f for f in self.MANDATORY_FIELDS if getattr(self, f) in (None, "", [])]

    def is_mandatory_complete(self) -> bool:
        return not self.missing_mandatory_fields()

    _PLACEHOLDER_VALUES = {
        "unknown", "n/a", "na", "tbd", "none", "null",
        "not specified", "not sure", "not provided", "?",
    }

    _STRING_FIELDS = (
        "destination", "departure_city", "start_date", "end_date", "budget",
        "purpose", "travel_style", "accommodation_preference",
        "transportation_preference", "food_preference",
        "accessibility_requirements", "special_requests",
    )

    def _is_valid(self, value) -> bool:
        if value in (None, "", []):
            return False
        if isinstance(value, str) and value.strip().lower() in self._PLACEHOLDER_VALUES:
            return False
        return True

    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if not hasattr(self, key) or not self._is_valid(value):
                continue
            if key in self._STRING_FIELDS and not isinstance(value, str):
                value = str(value)
            setattr(self, key, value)


@dataclass
class Itinerary:
    """Live itinerary that is progressively built during the conversation."""

    trip_summary: str = ""
    transportation: list[dict] = field(default_factory=list)
    hotels: list[dict] = field(default_factory=list)
    daily_plans: list[dict] = field(default_factory=list)
    activities: list[dict] = field(default_factory=list)
    estimated_budget: dict = field(default_factory=dict)
    checklist: list[str] = field(default_factory=list)
    packing_suggestions: list[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not any(
            [
                self.trip_summary,
                self.transportation,
                self.hotels,
                self.daily_plans,
                self.activities,
                self.estimated_budget,
                self.checklist,
                self.packing_suggestions,
            ]
        )
