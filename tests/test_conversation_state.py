from agents.conversation_state import ConversationStage, ConversationStateMachine
from models.trip import Itinerary, TripInfo


def test_greeting_advances_to_intent_discovery():
    state = ConversationStateMachine()
    trip_info, itinerary = TripInfo(), Itinerary()
    state.advance(trip_info, itinerary)
    assert state.stage == ConversationStage.INTENT_DISCOVERY


def test_mandatory_info_blocks_until_complete():
    state = ConversationStateMachine(ConversationStage.MANDATORY_INFO)
    trip_info, itinerary = TripInfo(destination="Kyoto"), Itinerary()
    state.advance(trip_info, itinerary)
    assert state.stage == ConversationStage.MANDATORY_INFO

    trip_info.update(
        departure_city="Delhi",
        start_date="2026-10-01",
        end_date="2026-10-10",
        budget="$3000",
        travelers_count=2,
        purpose="honeymoon",
    )
    state.advance(trip_info, itinerary)
    assert state.stage == ConversationStage.PREFERENCE_DISCOVERY
