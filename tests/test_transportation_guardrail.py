from guardrails.transportation import TransportContext, recommend_transport


def test_short_distance_recommends_walking():
    result = recommend_transport(TransportContext(distance_km=2))
    assert result["mode"] == "walking"


def test_long_distance_recommends_flight():
    result = recommend_transport(TransportContext(distance_km=2000))
    assert result["mode"] == "flight"


def test_heavy_luggage_overrides_walking():
    result = recommend_transport(TransportContext(distance_km=2, has_heavy_luggage=True))
    assert result["mode"] == "taxi"


def test_accessibility_overrides_metro():
    result = recommend_transport(TransportContext(distance_km=20, accessibility_needs=True))
    assert result["mode"] == "taxi"
