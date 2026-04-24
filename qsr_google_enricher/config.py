from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(slots=True)
class Settings:
    api_key: str
    country_code: str = "IT"
    language_code: str = "it"
    search_max_results: int = 5
    request_timeout_seconds: int = 30
    pause_between_requests_seconds: float = 0.15
    enable_context_search: bool = False
    context_radius_meters: int = 250
    location_classifier_mode: str = "rules"
    openai_api_key: str | None = None
    openai_model: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
        if not api_key:
            raise ValueError(
                "Missing GOOGLE_MAPS_API_KEY. Create a .env file from .env.example "
                "and paste your Google Maps Platform API key."
            )
        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip() or None
        openai_model = os.getenv("OPENAI_MODEL", "").strip() or None
        return cls(api_key=api_key, openai_api_key=openai_api_key, openai_model=openai_model)
