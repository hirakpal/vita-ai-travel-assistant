from models.trip import Itinerary, TripInfo
from services.budget_estimator import estimate_budget


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
