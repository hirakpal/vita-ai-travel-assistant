"""Core orchestrator: ties together guardrails, state machine, memory, RAG,
and the LLM to produce each assistant turn."""
from agents.conversation_state import ConversationStage, ConversationStateMachine
from agents.extractor import extract_trip_fields
from guardrails.conversation_flow import get_stage_instruction
from guardrails.persona import build_system_prompt
from guardrails.transportation import TransportContext, recommend_transport
from models.trip import Itinerary, TripInfo
from services.budget_estimator import estimate_budget
from services.llm_client import LLMClient
from services.maps_service import get_distance_km
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
        selected_hotel = extracted.pop("selected_hotel", None)
        confirmed_leg = extracted.pop("confirmed_transport_leg", None)
        itinerary_days = extracted.pop("itinerary_days", None)
        trip_info.update(**extracted)

        # Opportunistically fold confirmed details into the live itinerary as
        # soon as the traveler states them, regardless of conversation stage.
        if selected_hotel and selected_hotel not in itinerary.hotels:
            itinerary.hotels.append(selected_hotel)
        if isinstance(confirmed_leg, dict) and confirmed_leg.get("mode"):
            if confirmed_leg not in itinerary.transportation:
                itinerary.transportation.append(confirmed_leg)
        if isinstance(itinerary_days, list):
            for day in itinerary_days:
                if day and day not in itinerary.daily_plans:
                    itinerary.daily_plans.append(day)

        # 2. Advance the conversation stage if the current stage's gate is met.
        state.advance(trip_info, itinerary)

        # 3. Retrieve grounding knowledge when the stage benefits from it.
        context = ""
        if state.stage in RETRIEVAL_STAGES:
            query = f"{trip_info.destination or ''} {trip_info.interests} {trip_info.transportation_preference or ''}"
            context = retrieve_context(query)

        # 4. Apply the transportation guardrail as a baseline suggestion once
        # we reach that stage, if the traveler hasn't already confirmed a leg.
        if state.stage == ConversationStage.TRANSPORTATION_PLANNING and not itinerary.transportation:
            distance_km = get_distance_km(trip_info.departure_city, trip_info.destination)
            suggestion = recommend_transport(
                TransportContext(
                    distance_km=distance_km if distance_km is not None else 800,
                    group_size=trip_info.travelers_count or 1,
                )
            )
            itinerary.transportation.append(suggestion)

        # 5. Recompute the budget estimate every turn so it tracks whatever
        # has been confirmed in the itinerary so far (or the traveler's own
        # stated budget). Computed before the LLM call so the assistant can
        # reference the real running total instead of inventing its own.
        if trip_info.destination:
            itinerary.estimated_budget = estimate_budget(trip_info, itinerary)

        # 6. Build the system prompt from the persona + stage guardrails.
        system_prompt = build_system_prompt(context)
        stage_instruction = get_stage_instruction(state.stage, trip_info)
        system_prompt += f"\n\nCurrent conversation stage: {state.stage.value}\nInstruction: {stage_instruction}"
        if itinerary.estimated_budget and state.stage in (
            ConversationStage.ITINERARY_BUILDING,
            ConversationStage.SUMMARY,
            ConversationStage.COMPLETED,
        ):
            b = itinerary.estimated_budget
            system_prompt += (
                f"\n\nCurrent running budget estimate: {b['currency']} {b['total']:,} total "
                f"(accommodation {b['currency']} {b['accommodation']:,}, "
                f"transportation {b['currency']} {b['transportation']:,}, "
                f"food {b['currency']} {b['food']:,}, activities {b['currency']} {b['activities']:,}). "
                "Reference these figures rather than inventing your own."
            )

        # 7. Generate the assistant reply.
        reply = self.llm.chat(system_prompt=system_prompt, messages=messages)

        # 8. Update the live itinerary once we are in the building/summary stages.
        if state.stage in (ConversationStage.ITINERARY_BUILDING, ConversationStage.SUMMARY, ConversationStage.COMPLETED):
            if trip_info.destination and not itinerary.trip_summary:
                itinerary.trip_summary = (
                    f"{trip_info.travelers_count or 'Traveler(s)'} heading to "
                    f"{trip_info.destination} from {trip_info.departure_city or 'TBD'}, "
                    f"{trip_info.start_date or 'TBD'} to {trip_info.end_date or 'TBD'}."
                )

        return reply
