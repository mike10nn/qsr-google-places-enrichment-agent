from __future__ import annotations

import argparse
from pathlib import Path

from qsr_google_enricher.config import Settings
from qsr_google_enricher.exporters import export_outputs
from qsr_google_enricher.google_places import GooglePlacesClient
from qsr_google_enricher.io_utils import read_input_csv, records_to_dataframe
from qsr_google_enricher.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Enrich a list of QSR addresses with Google Places data and export a spreadsheet."
    )
    parser.add_argument("--input", required=True, help="Path to input CSV with at least an 'address' column.")
    parser.add_argument(
        "--output",
        required=True,
        help="Output base path without extension, e.g. outputs/qsr_results",
    )
    parser.add_argument("--country", default="IT", help="Country code used for Google Places regionCode.")
    parser.add_argument("--language", default="it", help="Language code for Google Places results.")
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="How many Google Text Search candidates to request before picking the best one.",
    )
    parser.add_argument(
        "--enable-context-search",
        action="store_true",
        help="Run a nearby context search to improve location_type classification.",
    )
    parser.add_argument(
        "--context-radius",
        type=int,
        default=250,
        help="Radius in meters for context search when enabled.",
    )
    parser.add_argument(
        "--location-classifier",
        choices=["rules", "openai"],
        default="rules",
        help="How to classify the custom location_type field.",
    )
    parser.add_argument(
        "--openai-model",
        default=None,
        help="OpenAI model name to use when --location-classifier openai is selected.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = Settings.from_env()
    settings.country_code = args.country
    settings.language_code = args.language
    settings.search_max_results = args.max_results
    settings.enable_context_search = args.enable_context_search
    settings.context_radius_meters = args.context_radius
    settings.location_classifier_mode = args.location_classifier
    if args.openai_model:
        settings.openai_model = args.openai_model

    client = GooglePlacesClient(settings)
    rows = read_input_csv(args.input)
    records = run_pipeline(rows, client, settings)
    df = records_to_dataframe(records)
    csv_path, xlsx_path = export_outputs(df, Path(args.output))

    print(f"Done. CSV:  {csv_path}")
    print(f"Done. XLSX: {xlsx_path}")


if __name__ == "__main__":
    main()