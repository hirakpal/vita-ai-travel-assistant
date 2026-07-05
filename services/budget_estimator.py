"""Budget Planner & Estimator.

If the traveler has stated a budget, it is surfaced as-is alongside a
running cost estimate. If not, the estimate is built entirely from
whatever has been confirmed in the live itinerary so far (hotel/night
rate, chosen transport legs, trip length, traveler count), falling back to
reasonable per-day defaults for anything not yet decided. The estimate is
recomputed every turn, so it evolves as the itinerary evolves.
"""
import math
import re
from datetime import datetime

CURRENCY_SYMBOLS = {"₹": "INR", "$": "USD", "€": "EUR", "£": "GBP"}
CURRENCY_CODES = ("INR", "USD", "EUR", "GBP")

# Per-day/night defaults, used only for whatever hasn't been confirmed yet.
DEFAULT_RATES = {
    "INR": {"accommodation_per_night": 3000, "food_per_day": 800, "activities_per_day": 500},
    "USD": {"accommodation_per_night": 60, "food_per_day": 25, "activities_per_day": 15},
    "EUR": {"accommodation_per_night": 55, "food_per_day": 22, "activities_per_day": 14},
    "GBP": {"accommodation_per_night": 48, "food_per_day": 20, "activities_per_day": 12},
}

# Flat/per-km fallback cost for a guardrail-suggested transport mode that has
# no traveler-confirmed fare yet.
MODE_COST_PER_KM = {
    "walking": 0, "bicycle": 5, "bus": 2, "metro": 3, "train": 3,
    "ferry": 4, "self_drive": 8, "taxi": 15, "ride_hailing": 13, "flight": 6,
}
MODE_FLAT_MINIMUM = {"bus": 30, "metro": 30, "taxi": 100, "ride_hailing": 100, "ferry": 200}


def _detect_currency(*texts) -> str:
    for text in texts:
        if not text:
            continue
        text = str(text)
        for symbol, code in CURRENCY_SYMBOLS.items():
            if symbol in text:
                return code
        for code in CURRENCY_CODES:
            if code in text.upper():
                return code
    return "INR"


def _extract_numbers(text) -> list[float]:
    return [float(n.replace(",", "")) for n in re.findall(r"[\d,]+(?:\.\d+)?", str(text) if text else "")]


def _average(numbers: list[float]) -> float:
    return sum(numbers) / len(numbers) if numbers else 0.0


def _parse_nights(trip_info) -> int:
    try:
        start = datetime.fromisoformat(trip_info.start_date).date()
        end = datetime.fromisoformat(trip_info.end_date).date()
        nights = (end - start).days
        if nights > 0:
            return nights
    except (TypeError, ValueError):
        pass
    return 1


def _accommodation_cost(trip_info, itinerary, nights: int, rooms: int, currency: str, rates: dict) -> tuple[float, str]:
    budget_text = str(trip_info.budget) if trip_info.budget else ""
    numbers = _extract_numbers(budget_text)
    if numbers and "night" in budget_text.lower():
        return _average(numbers) * nights * rooms, "traveler-stated nightly rate"
    if itinerary.hotels:
        return rates["accommodation_per_night"] * nights * rooms, "default rate (hotel chosen, rate not confirmed)"
    return rates["accommodation_per_night"] * nights * rooms, "default rate (hotel not yet chosen)"


def _transportation_cost(itinerary, currency: str) -> tuple[float, str]:
    if not itinerary.transportation:
        return 0.0, "no transport legs planned yet"
    total = 0.0
    confirmed_any = False
    for leg in itinerary.transportation:
        fare_text = leg.get("fare_estimate") or leg.get("fare") or ""
        numbers = _extract_numbers(fare_text)
        if numbers:
            total += _average(numbers)
            confirmed_any = True
            continue
        mode = leg.get("mode", "taxi")
        distance_km = leg.get("distance_km") or 10
        estimate = MODE_COST_PER_KM.get(mode, 10) * distance_km
        total += max(estimate, MODE_FLAT_MINIMUM.get(mode, 0))
    basis = "includes traveler-confirmed fares" if confirmed_any else "estimated from mode/distance defaults"
    return total, basis


def format_budget_string(estimate: dict) -> str:
    """Renders an estimate dict as a short human-readable budget string,
    used to auto-fill TripInfo.budget when the traveler defers the decision."""
    return f"~{estimate['currency']} {estimate['total']:,} (auto-estimated by VITA)"


def estimate_budget(trip_info, itinerary) -> dict:
    currency = _detect_currency(trip_info.budget, trip_info.destination)
    rates = DEFAULT_RATES.get(currency, DEFAULT_RATES["INR"])

    travelers = trip_info.travelers_count or 1
    nights = _parse_nights(trip_info)
    rooms = max(1, math.ceil(travelers / 2))

    accommodation, accommodation_basis = _accommodation_cost(trip_info, itinerary, nights, rooms, currency, rates)
    transportation, transportation_basis = _transportation_cost(itinerary, currency)
    food = rates["food_per_day"] * nights * travelers
    activities = rates["activities_per_day"] * nights * travelers if (trip_info.interests or itinerary.daily_plans) else 0

    total = round(accommodation + transportation + food + activities)

    return {
        "currency": currency,
        "nights": nights,
        "travelers": travelers,
        "accommodation": round(accommodation),
        "transportation": round(transportation),
        "food": round(food),
        "activities": round(activities),
        "total": total,
        "user_stated_budget": trip_info.budget,
        "notes": {
            "accommodation": accommodation_basis,
            "transportation": transportation_basis,
            "food": "default per-day estimate" if food else "not applicable",
            "activities": "default per-day estimate" if activities else "not yet planned",
        },
    }
