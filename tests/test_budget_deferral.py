import json

from agents.conversation_state import ConversationStage, ConversationStateMachine
from agents.travel_agent import TravelAgent
from models.trip import Itinerary, TripInfo


class FakeLLM:
    """Stubs the extraction call (returns fixed JSON) and the main reply call
    (returns a fixed string), distinguished by which system prompt is used."""

    def chat(self, system_prompt, messages):
        if "data-extraction" in system_prompt:
            return json.dumps({"budget_deferred": True})
        return "Sure, let's figure out a good budget together."


def test_deferred_budget_unblocks_mandatory_info_stage():
    trip_info = TripInfo(
        destination="Kolkata",
        departure_city="Bangalore",
        start_date="2027-01-29",
        end_date="2027-02-01",
        travelers_count=2,
        purpose="anniversary",
    )
    itinerary = Itinerary()
    state = ConversationStateMachine(ConversationStage.MANDATORY_INFO)
    agent = TravelAgent(llm=FakeLLM())

    assert trip_info.missing_mandatory_fields() == ["budget"]

    agent.process_turn(
        messages=[{"role": "user", "content": "help me decide the budget based on activities"}],
        trip_info=trip_info,
        itinerary=itinerary,
        state=state,
    )

    assert trip_info.budget is not None
    assert trip_info.is_mandatory_complete()
    assert state.stage == ConversationStage.PREFERENCE_DISCOVERY
