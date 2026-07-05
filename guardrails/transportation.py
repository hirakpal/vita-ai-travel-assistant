"""Transportation & Mobility Guardrail: rule-of-thumb transport recommendation."""
from dataclasses import dataclass

WALKING_MAX_KM = 5

TRANSPORT_MODES = (
    "walking",
    "bicycle",
    "bus",
    "metro",
    "train",
    "ferry",
    "self_drive",
    "taxi",
    "ride_hailing",
    "flight",
)


@dataclass
class TransportContext:
    distance_km: float
    budget_level: str = "mid"  # low | mid | high
    group_size: int = 1
    has_heavy_luggage: bool = False
    accessibility_needs: bool = False
    is_international: bool = False


def recommend_transport(ctx: TransportContext) -> dict:
    """Return a suggested transport mode plus rationale, as a rule-based baseline
    that the LLM can refine using additional traveler context."""
    if ctx.is_international or ctx.distance_km > 800:
        mode, rationale = "flight", "Long-haul or international distance makes flying the most time-efficient option."
    elif ctx.distance_km > 300:
        mode, rationale = "train", "Medium-to-long domestic distance; train offers comfort without airport overhead."
    elif ctx.distance_km > 50:
        mode, rationale = "self_drive", "Regional distance suits a self-drive or bus for flexibility."
    elif ctx.distance_km > WALKING_MAX_KM:
        mode, rationale = "metro", "Within city range; public transit (metro/bus) is efficient and affordable."
    else:
        mode, rationale = "walking", "Short local distance is comfortably walkable."

    if ctx.has_heavy_luggage and mode in ("walking", "bicycle"):
        mode, rationale = "taxi", "Heavy luggage makes taxi or ride-hailing more practical than walking."
    if ctx.accessibility_needs and mode in ("walking", "bicycle", "metro"):
        mode, rationale = "taxi", "Accessibility needs favor door-to-door taxi or ride-hailing service."
    if ctx.budget_level == "low" and mode in ("taxi", "self_drive") and ctx.distance_km <= 50:
        mode, rationale = "bus", "Lower budget favors public bus over taxi/self-drive for this distance."

    return {"mode": mode, "rationale": rationale, "distance_km": ctx.distance_km}
