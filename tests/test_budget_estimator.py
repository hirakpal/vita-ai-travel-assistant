from models.trip import Itinerary, TripInfo
from services.budget_estimator import estimate_budget, format_budget_string


def test_estimate_uses_stated_nightly_rate():
    trip = TripInfo(destination="Pune, India", start_date="2026-07-25", end_date="2026-07-30", budget="2000 INR per night", travelers_count=1)
    result = estimate_budget(trip, Itinerary())
    assert result["currency"] == "INR"
    assert result["nights"] == 5
    assert result["accommodation"] == 2000 * 5 * 1


def test_estimate_falls_back_to_defaults_without_stated_budget():
    trip = TripInfo(destination="Pune, India", start_date="2026-07-25", end_date="2026-07-27", travelers_count=2)
    result = estimate_budget(trip, Itinerary())
    assert result["nights"] == 2
    assert result["accommodation"] > 0
    assert result["total"] == result["accommodation"] + result["transportation"] + result["food"] + result["activities"]


def test_estimate_includes_confirmed_transport_fare():
    trip = TripInfo(destination="Pune, India", start_date="2026-07-25", end_date="2026-07-26", travelers_count=1)
    itinerary = Itinerary(transportation=[{"mode": "taxi", "fare_estimate": "INR 150-250", "rationale": "confirmed"}])
    result = estimate_budget(trip, itinerary)
    assert result["transportation"] == 200


def test_format_budget_string_produces_readable_total():
    estimate = {"currency": "INR", "total": 45000}
    assert format_budget_string(estimate) == "~INR 45,000 (auto-estimated by VITA)"


def test_estimate_handles_non_string_budget_without_crashing():
    # Regression: an LLM extraction can return budget as a bare number (JSON
    # int) rather than a string; the estimator must not crash on it.
    trip = TripInfo(destination="Pune, India", start_date="2026-07-25", end_date="2026-07-27", travelers_count=1, budget=5000)
    result = estimate_budget(trip, Itinerary())
    assert result["currency"] == "INR"
    assert result["total"] > 0
