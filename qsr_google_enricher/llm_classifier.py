from __future__ import annotations

from typing import Any

from openai import OpenAI
from pydantic import BaseModel, Field

from qsr_google_enricher.classifier import LOCATION_TYPE_DEFINITIONS, LOCATION_TYPES


class LocationTypeDecision(BaseModel):
    location_type: str = Field(description="One of the allowed location types.")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score from 0 to 1.")
    needs_manual_review: bool = Field(description="True if the classification is uncertain or borderline.")
    reason: str = Field(description="Short explanation of why this label was chosen.")


class OpenAILocationClassifier:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def classify(
        self,
        *,
        formatted_address: str | None,
        display_name: str | None,
        place_types: list[str] | None,
        nearby_context: list[dict[str, Any]] | None = None,
    ) -> tuple[str, float, bool, str]:
        place_types = place_types or []
        nearby_context = nearby_context or []

        compact_context = []
        for item in nearby_context[:12]:
            compact_context.append(
                {
                    "name": (item.get("displayName") or {}).get("text"),
                    "primaryType": item.get("primaryType"),
                    "types": item.get("types", []) or [],
                    "formattedAddress": item.get("formattedAddress"),
                }
            )

        definitions_block = "\n".join(
            f"- {name}: {definition}" for name, definition in LOCATION_TYPE_DEFINITIONS.items()
        )

        system_prompt = (
            "You classify QSR outlet locations in Italy into exactly one allowed category. "
            "Be conservative. If the evidence is weak or ambiguous, still choose the best category "
            "but set needs_manual_review=true and lower confidence."
        )

        user_prompt = f"""
Allowed location types:
{definitions_block}

Rules:
- Return exactly one location_type from this list: {LOCATION_TYPES}
- Prefer Shopping Mall only when the outlet is inside a mall/large commercial center otherwise prefer Commercial Area.
- Prefer Transport Hub only when inside or immediately next to major transport infrastructure.
- Prefer Service Area only for autogrill-style or highway-roadside service areas.
- Distinguish City Center vs Commercial Area carefully:
  - City Center = historic center, famous central piazzas/duomo/core pedestrian streets, very high-footfall center.
  - Commercial Area = retail corridor, business district, commercial strip, retail park, but not the historic core.
- Residential Area should be used when the outlet seems mainly embedded in neighborhoods and not a major commercial zone.

Outlet to classify:
- Display name: {display_name}
- Formatted address: {formatted_address}
- Google place types: {place_types}
- Nearby context: {compact_context}
""".strip()

        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=LocationTypeDecision,
        )
        parsed = response.output_parsed
        if parsed.location_type not in LOCATION_TYPES:
            raise ValueError(f"Model returned unsupported location type: {parsed.location_type}")
        return parsed.location_type, parsed.confidence, parsed.needs_manual_review, parsed.reason
