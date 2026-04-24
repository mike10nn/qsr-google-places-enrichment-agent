from __future__ import annotations

from typing import Any


LOCATION_TYPES = [
    "City Center",
    "Shopping Mall",
    "Commercial Area",
    "Transport Hub",
    "Residential Area",
    "Highway / Service Area",
]

LOCATION_TYPE_DEFINITIONS = {
    "City Center": "Historic center, main street, high foot traffic, e.g. central Rome or Milan Duomo.",
    "Shopping Mall": "Inside malls or commercial centers.",
    "Commercial Area": "High street but not historic center; retail parks, business districts, or commercial corridors.",
    "Transport Hub": "Located inside or immediately next to major transport infrastructure.",
    "Residential Area": "Located within neighborhoods and not in a major commercial zone.",
    "Highway / Service Area": "Autogrill-style locations near highways or major roads.",
}

SHOPPING_KEYWORDS = {
    "centro commerciale",
    "shopping mall",
    "shopping center",
    "shopping centre",
    "mall",
    "galleria",
    "outlet village",
    "retail park",
    "parco commerciale",
}
TRANSPORT_KEYWORDS = {
    "stazione",
    "aeroporto",
    "airport",
    "metro",
    "bus station",
    "train station",
    "terminal",
    "porto",
    "port",
}
HIGHWAY_KEYWORDS = {
    "autogrill",
    "area di servizio",
    "service area",
    "autostrada",
    "tangenziale",
    "raccordo",
    "ss ",
    "a1",
    "a4",
    "a14",
}
CITY_CENTER_KEYWORDS = {
    "centro storico",
    "duomo",
    "piazza",
    "corso",
    "via roma",
    "centro",
    "historic center",
    "historic centre",
    "main street",
}
COMMERCIAL_KEYWORDS = {
    "zona industriale",
    "viale industria",
    "business park",
    "district",
    "retail",
    "commerciale",
    "area commerciale",
}


def _normalize(text: str | None) -> str:
    return " ".join((text or "").lower().replace(",", " ").replace(".", " ").split())


def _contains_any(text: str, keywords: set[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def classify_location_type_rules(
    *,
    formatted_address: str | None,
    display_name: str | None,
    place_types: list[str] | None,
    nearby_context: list[dict[str, Any]] | None = None,
) -> tuple[str, float, bool, str]:
    place_types = place_types or []
    nearby_context = nearby_context or []

    text = " | ".join([_normalize(formatted_address), _normalize(display_name)])
    all_context_types: set[str] = set(place_types)
    for item in nearby_context:
        all_context_types.update(item.get("types", []) or [])
        primary = item.get("primaryType")
        if primary:
            all_context_types.add(primary)
        display = (item.get("displayName") or {}).get("text")
        text += " | " + _normalize(display)

    if "shopping_mall" in all_context_types or _contains_any(text, SHOPPING_KEYWORDS):
        return "Shopping Mall", 0.95, False, "mall keyword/type detected"

    if all_context_types.intersection(
        {"airport", "train_station", "subway_station", "transit_station", "bus_station"}
    ) or _contains_any(text, TRANSPORT_KEYWORDS):
        return "Transport Hub", 0.92, False, "transport keyword/type detected"

    if "gas_station" in all_context_types or _contains_any(text, HIGHWAY_KEYWORDS):
        return "Highway / Service Area", 0.9, False, "highway/service keyword detected"

    if _contains_any(text, CITY_CENTER_KEYWORDS):
        return "City Center", 0.65, True, "city-center keyword detected; manual check advised"

    if _contains_any(text, COMMERCIAL_KEYWORDS):
        return "Commercial Area", 0.72, True, "commercial-area keyword detected"

    if "restaurant" in all_context_types or "fast_food_restaurant" in all_context_types:
        return "Residential Area", 0.45, True, "fallback classification; manual check advised"

    return "Residential Area", 0.35, True, "low-confidence fallback"


# Backward-compatible name used by the first version of the project.
def classify_location_type(
    *,
    formatted_address: str | None,
    display_name: str | None,
    place_types: list[str] | None,
    nearby_context: list[dict[str, Any]] | None = None,
) -> tuple[str, float, bool, str]:
    return classify_location_type_rules(
        formatted_address=formatted_address,
        display_name=display_name,
        place_types=place_types,
        nearby_context=nearby_context,
    )
