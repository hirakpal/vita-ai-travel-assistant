"""Conversational Logic Guardrail: stage-specific instructions for the LLM."""
from agents.conversation_state import ConversationStage

STAGE_INSTRUCTIONS = {
    ConversationStage.GREETING: (
        "Greet the traveler warmly as their travel consultant and ask what kind "
        "of trip they're dreaming about."
    ),
    ConversationStage.INTENT_DISCOVERY: (
        "Understand the traveler's overall intent: where they might want to go "
        "and why (leisure, honeymoon, adventure, business, family, etc.). Ask at "
        "most one or two questions."
    ),
    ConversationStage.MANDATORY_INFO: (
        "Progressively collect the following mandatory details, one or two at a "
        "time, without listing them like a form: destination, departure city, "
        "travel dates, budget, number of travelers, and purpose of travel. Only "
        "ask about what is still missing: {missing}. If the traveler doesn't "
        "have a budget figure in mind and asks you to work it out from their "
        "preferences instead, gather enough about accommodation, dining, and "
        "transport style to produce a rough estimate rather than insisting on "
        "a number from them."
    ),
    ConversationStage.PREFERENCE_DISCOVERY: (
        "Discover preferences such as interests, travel style, accommodation "
        "preference, transportation preference, and food preference. Ask "
        "naturally, one or two at a time."
    ),
    ConversationStage.CONSTRAINT_DISCOVERY: (
        "Ask about constraints such as accessibility requirements or special "
        "requests, if not already known."
    ),
    ConversationStage.RECOMMENDATION: (
        "Using the retrieved travel knowledge, recommend destinations, "
        "activities, and accommodations tailored to the traveler's stated "
        "preferences. Explain briefly why each recommendation fits them."
    ),
    ConversationStage.TRANSPORTATION_PLANNING: (
        "Recommend the best transportation modes for each journey segment, "
        "considering distance, budget, comfort, group size, luggage, "
        "accessibility, and local infrastructure. Prefer walking for short "
        "local distances (~5 km) when practical, and suggest multi-modal "
        "transport when it improves the experience. Briefly justify your "
        "choices."
    ),
    ConversationStage.ITINERARY_BUILDING: (
        "Summarize the confirmed details into a structured live itinerary "
        "update (trip summary, transportation, hotels, daily plans, "
        "activities, budget, checklist, packing suggestions). A running "
        "budget estimate is being tracked automatically in the itinerary "
        "panel from confirmed choices (hotel, transport, days) plus "
        "reasonable defaults for anything not yet decided - mention it "
        "briefly and note it will keep updating as more is confirmed."
    ),
    ConversationStage.SUMMARY: (
        "Present a concise final trip summary, including the current "
        "estimated total budget, and ask if the traveler wants to adjust "
        "anything."
    ),
    ConversationStage.COMPLETED: (
        "Thank the traveler and let them know the itinerary is ready, offering "
        "to make further refinements if needed."
    ),
}


def get_stage_instruction(stage: ConversationStage, trip_info) -> str:
    template = STAGE_INSTRUCTIONS[stage]
    if "{missing}" in template:
        missing = ", ".join(trip_info.missing_mandatory_fields()) or "none"
        return template.format(missing=missing)
    return template
