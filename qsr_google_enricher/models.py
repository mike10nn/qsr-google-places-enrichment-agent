from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class InputRow:
    input_address: str
    brand: str | None = None
    notes: str | None = None

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "InputRow":
        normalized = {str(k).strip().lower(): v for k, v in row.items()}
        address = str(
            normalized.get("address")
            or normalized.get("street_address")
            or normalized.get("input_address")
            or ""
        ).strip()
        if not address:
            raise ValueError("Each input row must contain an 'address' column.")
        brand = str(normalized.get("brand") or "").strip() or None
        notes = str(normalized.get("notes") or "").strip() or None
        return cls(input_address=address, brand=brand, notes=notes)


@dataclass(slots=True)
class PlaceCandidate:
    place_id: str
    resource_name: str
    display_name: str | None
    formatted_address: str | None
    lat: float | None
    lng: float | None
    types: list[str] = field(default_factory=list)
    primary_type: str | None = None
    match_score: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OutletRecord:
    input_address: str
    brand: str | None
    matched_name: str | None
    matched_address: str | None
    region: str | None
    province: str | None
    city: str | None
    price_range: str | None
    customer_rating: float | None
    review_count: int | None
    latitude: float | None
    longitude: float | None
    location_type: str | None
    location_type_confidence: float | None
    location_type_reason: str | None
    location_type_method: str | None
    needs_manual_review: bool
    match_confidence: float | None
    google_place_id: str | None
    google_maps_uri: str | None
    primary_type: str | None
    place_types: str | None
    business_status: str | None
    notes: str | None = None
    source: str = "Google Places API + rules-based classifier"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
