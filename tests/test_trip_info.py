from models.trip import Itinerary, TripInfo


def test_missing_mandatory_fields_initially_all_missing():
    trip = TripInfo()
    assert set(trip.missing_mandatory_fields()) == set(TripInfo.MANDATORY_FIELDS)
    assert not trip.is_mandatory_complete()


def test_update_fills_mandatory_fields():
    trip = TripInfo()
    trip.update(
        destination="Kyoto",
        departure_city="Delhi",
        start_date="2026-10-01",
        end_date="2026-10-10",
        budget="$3000",
        travelers_count=2,
        purpose="honeymoon",
    )
    assert trip.is_mandatory_complete()


def test_update_ignores_none_and_empty():
    trip = TripInfo(destination="Kyoto")
    trip.update(destination=None, departure_city="")
    assert trip.destination == "Kyoto"
    assert trip.departure_city is None


def test_itinerary_is_empty_by_default():
    assert Itinerary().is_empty()


def test_update_rejects_placeholder_values():
    trip = TripInfo(departure_city="Delhi")
    trip.update(departure_city="unknown", start_date="TBD", budget="n/a")
    assert trip.departure_city == "Delhi"
    assert trip.start_date is None
    assert trip.budget is None
