"""Conversation state machine driving the consultation workflow."""
from enum import Enum


class ConversationStage(str, Enum):
    GREETING = "greeting"
    INTENT_DISCOVERY = "intent_discovery"
    MANDATORY_INFO = "mandatory_info"
    PREFERENCE_DISCOVERY = "preference_discovery"
    CONSTRAINT_DISCOVERY = "constraint_discovery"
    RECOMMENDATION = "recommendation"
    TRANSPORTATION_PLANNING = "transportation_planning"
    ITINERARY_BUILDING = "itinerary_building"
    SUMMARY = "summary"
    COMPLETED = "completed"


STAGE_ORDER = [
    ConversationStage.GREETING,
    ConversationStage.INTENT_DISCOVERY,
    ConversationStage.MANDATORY_INFO,
    ConversationStage.PREFERENCE_DISCOVERY,
    ConversationStage.CONSTRAINT_DISCOVERY,
    ConversationStage.RECOMMENDATION,
    ConversationStage.TRANSPORTATION_PLANNING,
    ConversationStage.ITINERARY_BUILDING,
    ConversationStage.SUMMARY,
    ConversationStage.COMPLETED,
]


class ConversationStateMachine:
    """Tracks the current stage and enforces forward-only, gated transitions."""

    def __init__(self, stage: ConversationStage = ConversationStage.GREETING):
        self.stage = stage

    def can_advance(self, trip_info, itinerary) -> bool:
        if self.stage == ConversationStage.GREETING:
            return True
        if self.stage == ConversationStage.INTENT_DISCOVERY:
            return bool(trip_info.destination or trip_info.purpose)
        if self.stage == ConversationStage.MANDATORY_INFO:
            return trip_info.is_mandatory_complete()
        if self.stage == ConversationStage.PREFERENCE_DISCOVERY:
            return bool(trip_info.interests or trip_info.travel_style)
        if self.stage == ConversationStage.CONSTRAINT_DISCOVERY:
            return True
        if self.stage == ConversationStage.RECOMMENDATION:
            return True
        if self.stage == ConversationStage.TRANSPORTATION_PLANNING:
            return bool(itinerary.transportation)
        if self.stage == ConversationStage.ITINERARY_BUILDING:
            return not itinerary.is_empty()
        if self.stage == ConversationStage.SUMMARY:
            return True
        return False

    def advance(self, trip_info, itinerary) -> ConversationStage:
        if not self.can_advance(trip_info, itinerary):
            return self.stage
        idx = STAGE_ORDER.index(self.stage)
        if idx + 1 < len(STAGE_ORDER):
            self.stage = STAGE_ORDER[idx + 1]
        return self.stage

    def to_dict(self) -> dict:
        return {"stage": self.stage.value}

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationStateMachine":
        return cls(ConversationStage(data.get("stage", ConversationStage.GREETING.value)))
