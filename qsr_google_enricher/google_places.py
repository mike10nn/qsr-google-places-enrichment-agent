from __future__ import annotations

import difflib
import time
from typing import Any

import requests

from qsr_google_enricher.config import Settings
from qsr_google_enricher.models import InputRow, PlaceCandidate


class GooglePlacesClient:
    BASE_URL = "https://places.googleapis.com/v1"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": settings.api_key,
            }
        )

    def _sleep(self) -> None:
        if self.settings.pause_between_requests_seconds > 0:
            time.sleep(self.settings.pause_between_requests_seconds)

    def _post(self, path: str, json_body: dict[str, Any], field_mask: str) -> dict[str, Any]:
        response = self.session.post(
            f"{self.BASE_URL}{path}",
            json=json_body,
            headers={"X-Goog-FieldMask": field_mask},
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        self._sleep()
        return response.json()

    def _get(self, path: str, field_mask: str) -> dict[str, Any]:
        response = self.session.get(
            f"{self.BASE_URL}{path}",
            headers={"X-Goog-FieldMask": field_mask},
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        self._sleep()
        return response.json()

    def search_place_candidates(self, row: InputRow) -> list[PlaceCandidate]:
        query = row.input_address
        if row.brand:
            query = f"{row.brand} {row.input_address}"

        payload: dict[str, Any] = {
            "textQuery": query,
            "languageCode": self.settings.language_code,
            "regionCode": self.settings.country_code,
            "maxResultCount": self.settings.search_max_results,
        }

        field_mask = (
            "places.id,places.name,places.displayName,places.formattedAddress,"
            "places.location,places.types,places.primaryType"
        )
        data = self._post("/places:searchText", payload, field_mask)

        candidates: list[PlaceCandidate] = []
        for place in data.get("places", []):
            display_name = (place.get("displayName") or {}).get("text")
            formatted_address = place.get("formattedAddress")
            location = place.get("location") or {}
            score = self._score_candidate(row, display_name, formatted_address)
            candidates.append(
                PlaceCandidate(
                    place_id=place.get("id", ""),
                    resource_name=place.get("name", ""),
                    display_name=display_name,
                    formatted_address=formatted_address,
                    lat=location.get("latitude"),
                    lng=location.get("longitude"),
                    types=place.get("types", []) or [],
                    primary_type=place.get("primaryType"),
                    match_score=score,
                    raw=place,
                )
            )

        return sorted(candidates, key=lambda c: c.match_score, reverse=True)

    def get_place_details(self, place_id: str) -> dict[str, Any]:
        field_mask = (
            "id,displayName,formattedAddress,addressComponents,location,types,primaryType,"
            "rating,userRatingCount,priceLevel,priceRange,googleMapsUri,businessStatus"
        )
        return self._get(f"/places/{place_id}", field_mask)

    def find_nearby_context(self, lat: float, lng: float) -> list[dict[str, Any]]:
        if not self.settings.enable_context_search:
            return []

        field_mask = "places.displayName,places.primaryType,places.types,places.location"
        payload = {
            "includedTypes": [
                "shopping_mall",
                "train_station",
                "subway_station",
                "transit_station",
                "bus_station",
                "airport",
                "gas_station",
            ],
            "maxResultCount": 15,
            "languageCode": self.settings.language_code,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": float(self.settings.context_radius_meters),
                }
            },
        }
        data = self._post("/places:searchNearby", payload, field_mask)
        return data.get("places", []) or []

    @staticmethod
    def _normalize_text(text: str | None) -> str:
        return " ".join((text or "").lower().replace(",", " ").split())

    def _score_candidate(
        self,
        row: InputRow,
        display_name: str | None,
        formatted_address: str | None,
    ) -> float:
        address_a = self._normalize_text(row.input_address)
        address_b = self._normalize_text(formatted_address)
        name_b = self._normalize_text(display_name)
        score = 0.0

        if address_a and address_b:
            score += difflib.SequenceMatcher(None, address_a, address_b).ratio() * 0.75

        if row.brand and name_b:
            score += difflib.SequenceMatcher(
                None,
                self._normalize_text(row.brand),
                name_b,
            ).ratio() * 0.25

        return round(min(score, 1.0), 4)
