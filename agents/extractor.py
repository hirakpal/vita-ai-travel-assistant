"""Extracts structured trip/preference fields from the conversation so far."""
import json
import re
from datetime import date

from services.llm_client import LLMClient

EXTRACTION_PROMPT = """\
Today's date is {today}. From the conversation below, extract any of these \
fields the traveler has stated so far. Respond with ONLY a compact JSON \
object (no prose, no code fences). Omit any field that is still unknown - \
never guess, invent, or default a value (including years for dates; if the \
traveler didn't state a year, infer the nearest future occurrence of that \
date relative to today).

Fields:
- destination, departure_city, start_date, end_date, budget, \
travelers_count (integer), purpose, interests (list of strings), \
travel_style, accommodation_preference, transportation_preference, \
food_preference, accessibility_requirements, special_requests
- selected_hotel (string): a specific hotel name the traveler has confirmed \
they will book/stay at, if any.
- confirmed_transport_leg (object with mode, from, to, fare_estimate, \
rationale): a specific point-to-point journey and transport mode the \
traveler has confirmed/chosen, if any.
- itinerary_days (list of strings): one entry per day the traveler has \
agreed to a day-by-day plan for, each summarizing that day's plan.

Conversation:
{conversation}
"""


def _to_transcript(messages: list[dict]) -> str:
    return "\n".join(f"{m['role']}: {m['content']}" for m in messages)


def extract_trip_fields(messages: list[dict], llm: LLMClient) -> dict:
    prompt = EXTRACTION_PROMPT.format(today=date.today().isoformat(), conversation=_to_transcript(messages))
    raw = llm.chat(
        system_prompt="You are a precise data-extraction assistant. Output valid JSON only.",
        messages=[{"role": "user", "content": prompt}],
    )
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return {}
