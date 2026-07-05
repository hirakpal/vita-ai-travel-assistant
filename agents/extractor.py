"""Extracts structured trip/preference fields from the conversation so far."""
import json
import re

from services.llm_client import LLMClient

EXTRACTION_PROMPT = """\
From the conversation below, extract any of these fields the traveler has \
stated so far. Respond with ONLY a compact JSON object (no prose, no code \
fences). Omit fields that are still unknown - do not guess or invent values.

Fields: destination, departure_city, start_date, end_date, budget, \
travelers_count (integer), purpose, interests (list of strings), \
travel_style, accommodation_preference, transportation_preference, \
food_preference, accessibility_requirements, special_requests

Conversation:
{conversation}
"""


def _to_transcript(messages: list[dict]) -> str:
    return "\n".join(f"{m['role']}: {m['content']}" for m in messages)


def extract_trip_fields(messages: list[dict], llm: LLMClient) -> dict:
    prompt = EXTRACTION_PROMPT.format(conversation=_to_transcript(messages))
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
