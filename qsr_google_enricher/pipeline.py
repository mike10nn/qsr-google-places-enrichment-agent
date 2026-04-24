from __future__ import annotations

from typing import Any

from qsr_google_enricher.classifier import classify_location_type_rules
from qsr_google_enricher.config import Settings
from qsr_google_enricher.google_places import GooglePlacesClient
from qsr_google_enricher.llm_classifier import OpenAILocationClassifier
from qsr_google_enricher.models import InputRow, OutletRecord


ITALIAN_REGION_BY_CODE = {
    "ABR": "Abruzzo",
    "BAS": "Basilicata",
    "CAL": "Calabria",
    "CAM": "Campania",
    "EMR": "Emilia-Romagna",
    "FVG": "Friuli-Venezia Giulia",
    "LAZ": "Lazio",
    "LIG": "Liguria",
    "LOM": "Lombardia",
    "MAR": "Marche",
    "MOL": "Molise",
    "PMN": "Piemonte",
    "PUG": "Puglia",
    "SAR": "Sardegna",
    "SIC": "Sicilia",
    "TOS": "Toscana",
    "TAA": "Trentino-Alto Adige/Südtirol",
    "UMB": "Umbria",
    "VDA": "Valle d'Aosta/Vallée d'Aoste",
    "VEN": "Veneto",
}


def _component_lookup(details: dict[str, Any]) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    for component in details.get("addressComponents", []) or []:
        for item_type in component.get("types", []) or []:
            lookup[item_type] = component
    return lookup


def _component_text(component: dict[str, Any] | None) -> str | None:
    if not component:
        return None
    return component.get("longText") or component.get("shortText")


def _extract_region(component_lookup_map: dict[str, dict[str, Any]]) -> str | None:
    region_component = component_lookup_map.get("administrative_area_level_1")
    if not region_component:
        return None
    long_text = region_component.get("longText")
    short_text = region_component.get("shortText")
    if long_text:
        return long_text
    if short_text and short_text in ITALIAN_REGION_BY_CODE:
        return ITALIAN_REGION_BY_CODE[short_text]
    return short_text


def _price_range_to_string(details: dict[str, Any]) -> str | None:
    price_range = details.get("priceRange")
    if isinstance(price_range, dict):
        start = price_range.get("startPrice", {})
        end = price_range.get("endPrice", {})
        start_u = start.get("units")
        end_u = end.get("units")
        currency = start.get("currencyCode") or end.get("currencyCode")
        if start_u is not None and end_u is not None:
            return f"{currency or ''} {start_u}-{end_u}".strip()

    price_level = details.get("priceLevel")
    if price_level:
        return str(price_level)
    return None


def _classify_location(
    *,
    settings: Settings,
    llm_classifier: OpenAILocationClassifier | None,
    matched_address: str | None,
    matched_name: str | None,
    types: list[str],
    nearby_context: list[dict[str, Any]],
) -> tuple[str, float, bool, str, str]:
    if settings.location_classifier_mode == "openai":
        if not llm_classifier:
            raise ValueError(
                "OpenAI location classification requested, but OPENAI_API_KEY or OPENAI_MODEL is missing."
            )
        location_type, lt_conf, manual_review, reason = llm_classifier.classify(
            formatted_address=matched_address,
            display_name=matched_name,
            place_types=types,
            nearby_context=nearby_context,
        )
        return location_type, lt_conf, manual_review, reason, "OpenAI"

    location_type, lt_conf, manual_review, reason = classify_location_type_rules(
        formatted_address=matched_address,
        display_name=matched_name,
        place_types=types,
        nearby_context=nearby_context,
    )
    return location_type, lt_conf, manual_review, reason, "rules"


def build_record_from_details(
    row: InputRow,
    details: dict[str, Any],
    match_confidence: float,
    nearby_context: list[dict[str, Any]],
    settings: Settings,
    llm_classifier: OpenAILocationClassifier | None,
) -> OutletRecord:
    lookup = _component_lookup(details)
    location = details.get("location") or {}
    matched_name = (details.get("displayName") or {}).get("text")
    matched_address = details.get("formattedAddress")
    types = details.get("types", []) or []

    location_type, lt_conf, manual_review, reason, method = _classify_location(
        settings=settings,
        llm_classifier=llm_classifier,
        matched_address=matched_address,
        matched_name=matched_name,
        types=types,
        nearby_context=nearby_context,
    )

    return OutletRecord(
        input_address=row.input_address,
        brand=row.brand,
        matched_name=matched_name,
        matched_address=matched_address,
        region=_extract_region(lookup),
        province=_component_text(lookup.get("administrative_area_level_2")),
        city=(
            _component_text(lookup.get("locality"))
            or _component_text(lookup.get("postal_town"))
            or _component_text(lookup.get("administrative_area_level_3"))
        ),
        price_range=_price_range_to_string(details),
        customer_rating=details.get("rating"),
        review_count=details.get("userRatingCount"),
        latitude=location.get("latitude"),
        longitude=location.get("longitude"),
        location_type=location_type,
        location_type_confidence=lt_conf,
        location_type_reason=reason,
        location_type_method=method,
        needs_manual_review=manual_review,
        match_confidence=match_confidence,
        google_place_id=details.get("id"),
        google_maps_uri=details.get("googleMapsUri"),
        primary_type=details.get("primaryType"),
        place_types=" | ".join(types) if types else None,
        business_status=details.get("businessStatus"),
        notes=row.notes,
        source=(
            "Google Places API + OpenAI location classifier"
            if method == "OpenAI"
            else "Google Places API + rules-based classifier"
        ),
    )


def run_pipeline(
    rows: list[InputRow],
    client: GooglePlacesClient,
    settings: Settings,
) -> list[OutletRecord]:
    output: list[OutletRecord] = []
    llm_classifier = None
    if settings.location_classifier_mode == "openai":
        if not settings.openai_api_key or not settings.openai_model:
            raise ValueError(
                "When --location-classifier openai is used, set OPENAI_API_KEY and OPENAI_MODEL in .env "
                "or pass --openai-model."
            )
        llm_classifier = OpenAILocationClassifier(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    for row in rows:
        try:
            candidates = client.search_place_candidates(row)
            if not candidates:
                output.append(
                    OutletRecord(
                        input_address=row.input_address,
                        brand=row.brand,
                        matched_name=None,
                        matched_address=None,
                        region=None,
                        province=None,
                        city=None,
                        price_range=None,
                        customer_rating=None,
                        review_count=None,
                        latitude=None,
                        longitude=None,
                        location_type=None,
                        location_type_confidence=None,
                        location_type_reason=None,
                        location_type_method=settings.location_classifier_mode,
                        needs_manual_review=True,
                        match_confidence=None,
                        google_place_id=None,
                        google_maps_uri=None,
                        primary_type=None,
                        place_types=None,
                        business_status=None,
                        notes=row.notes,
                        error="No Google Places match found.",
                    )
                )
                continue

            best = candidates[0]
            details = client.get_place_details(best.place_id)
            nearby_context = []
            lat = (details.get("location") or {}).get("latitude")
            lng = (details.get("location") or {}).get("longitude")
            if lat is not None and lng is not None:
                nearby_context = client.find_nearby_context(lat, lng)

            output.append(
                build_record_from_details(
                    row=row,
                    details=details,
                    match_confidence=best.match_score,
                    nearby_context=nearby_context,
                    settings=settings,
                    llm_classifier=llm_classifier,
                )
            )

        except Exception as exc:
            output.append(
                OutletRecord(
                    input_address=row.input_address,
                    brand=row.brand,
                    matched_name=None,
                    matched_address=None,
                    region=None,
                    province=None,
                    city=None,
                    price_range=None,
                    customer_rating=None,
                    review_count=None,
                    latitude=None,
                    longitude=None,
                    location_type=None,
                    location_type_confidence=None,
                    location_type_reason=None,
                    location_type_method=settings.location_classifier_mode,
                    needs_manual_review=True,
                    match_confidence=None,
                    google_place_id=None,
                    google_maps_uri=None,
                    primary_type=None,
                    place_types=None,
                    business_status=None,
                    notes=row.notes,
                    error=str(exc),
                )
            )

    return output
