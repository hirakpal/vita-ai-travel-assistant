"""Core orchestrator: ties together guardrails, state machine, memory, RAG,
and the LLM to produce each assistant turn."""
from agents.conversation_state import ConversationStage, ConversationStateMachine
from agents.extractor import extract_trip_fields
from guardrails.conversation_flow import get_stage_instruction
from guardrails.persona import build_system_prompt
from guardrails.transportation import TransportContext, recommend_transport
from models.trip import Itinerary, TripInfo
from services.llm_client import LLMClient
from services.retrieval_engine import retrieve_context

RETRIEVAL_STAGES = {
    ConversationStage.RECOMMENDATION,
    ConversationStage.TRANSPORTATION_PLANNING,
    ConversationStage.ITINERARY_BUILDING,
}


class TravelAgent:
    def __init__(self, llm: LLMClient = None):
        self.llm = llm or LLMClient()

    def process_turn(
        self,
        messages: list[dict],
        trip_info: TripInfo,
        itinerary: Itinerary,
        state: ConversationStateMachine,
    ) -> str:
        # 1. Update short-term memory (slot filling) from the conversation so far.
        extracted = extract_trip_fields(messages, self.llm)
        if "interests" in extracted and isinstance(extracted["interests"], str):
            extracted["interests"] = [extracted["interests"]]
        trip_info.update(**extracted)

        # 2. Advance the conversation stage if the current stage's gate is met.
        state.advance(trip_info, itinerary)

        # 3. Retrieve grounding knowledge when the stage benefits from it.
        context = ""
        if state.stage in RETRIEVAL_STAGES:
            query = f"{trip_info.destination or ''} {trip_info.interests} {trip_info.transportation_preference or ''}"
            context = retrieve_context(query)

        # 4. Apply the transportation guardrail once we reach that stage.
        if state.stage == ConversationStage.TRANSPORTATION_PLANNING and not itinerary.transportation:
            suggestion = recommend_transport(TransportContext(distance_km=50))
            itinerary.transportation.append(suggestion)

        # 5. Build the system prompt from the persona + stage guardrails.
        system_prompt = build_system_prompt(context)
        stage_instruction = get_stage_instruction(state.stage, trip_info)
        system_prompt += f"\n\nCurrent conversation stage: {state.stage.value}\nInstruction: {stage_instruction}"

        # 6. Generate the assistant reply.
        reply = self.llm.chat(system_prompt=system_prompt, messages=messages)

        # 7. Update the live itinerary once we are in the building/summary stages.
        if state.stage in (ConversationStage.ITINERARY_BUILDING, ConversationStage.SUMMARY, ConversationStage.COMPLETED):
            if trip_info.destination and not itinerary.trip_summary:
                itinerary.trip_summary = (
                    f"{trip_info.travelers_count or 'Traveler(s)'} heading to "
                    f"{trip_info.destination} from {trip_info.departure_city or 'TBD'}, "
                    f"{trip_info.start_date or 'TBD'} to {trip_info.end_date or 'TBD'}."
                )

        return reply
