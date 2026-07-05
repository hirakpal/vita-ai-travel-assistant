from services import maps_service


def test_returns_none_without_api_key(monkeypatch):
    monkeypatch.setattr(maps_service, "settings", type("S", (), {"google_maps_api_key": ""})())
    assert maps_service.get_distance_km("Delhi", "Kyoto") is None


def test_returns_none_for_missing_place_names(monkeypatch):
    monkeypatch.setattr(maps_service, "settings", type("S", (), {"google_maps_api_key": "fake-key"})())
    assert maps_service.get_distance_km("", "Kyoto") is None
    assert maps_service.get_distance_km("Delhi", "") is None
