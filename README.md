# QSR Google Places Enrichment Agent

Python workflow for enriching quick-service restaurant (QSR) outlet address lists with Google Places data and an OpenAI-assisted location-type classification step.

This project was created to support internship research by turning manually collected QSR outlet addresses into an analysis-ready dataset with geographic fields, Google ratings, review counts, price indicators, coordinates, match quality fields, and a custom `location_type` category.

## What This Project Demonstrates

- Data collection and enrichment workflow design
- API integration with Google Places API and OpenAI
- Prompt-based classification for ambiguous business/location context
- CSV-to-Excel data delivery for research and stakeholder review
- Manual-review flags for data quality control
- Reproducible project documentation for a data/business analyst portfolio

## Workflow

```text
Input CSV of outlet addresses
        |
        v
Google Places Text Search
        |
        v
Best candidate match + Place Details
        |
        v
Optional nearby context search
        |
        v
OpenAI prompt classifies location_type
        |
        v
CSV and Excel outputs for analysis/manual review
```

## Enriched Fields

Core research fields:

- `region`
- `province`
- `city`
- `price_range`
- `customer_rating`
- `review_count`
- `latitude`
- `longitude`
- `location_type`

Audit and data-quality fields:

- `input_address`
- `brand`
- `matched_name`
- `matched_address`
- `match_confidence`
- `google_place_id`
- `google_maps_uri`
- `primary_type`
- `place_types`
- `business_status`
- `location_type_confidence`
- `needs_manual_review`
- `source`
- `error`

## Project Structure

```text
.
|-- main.py
|-- requirements.txt
|-- requirements-dev.txt
|-- .env.example
|-- qsr_google_enricher/
|   |-- classifier.py
|   |-- config.py
|   |-- exporters.py
|   |-- google_places.py
|   |-- io_utils.py
|   |-- llm_classifier.py
|   |-- models.py
|   `-- pipeline.py
|-- data/
|   |-- samples/
|   |   |-- sample_input.csv
|   |   `-- sample_output.csv
|   `-- raw/              # ignored by git; local internship data only
|-- docs/
|   |-- MANUAL.md
|   |-- METHODOLOGY.md
|   |-- DATA_DICTIONARY.md
|   |-- OPENAI_PROMPT.md
|   `-- CV_ENTRY.md
|-- scripts/
|   `-- merge_notes_address.py
|-- templates/
|   `-- QSR_template_and_output_schema.xlsx
`-- tests/
    |-- conftest.py
    `-- test_classifier.py
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

For local testing:

```bash
pip install -r requirements-dev.txt
```

Create a local environment file:

```bash
copy .env.example .env
```

Fill in your real keys in `.env`:

```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

Do not commit `.env`. It is ignored by `.gitignore`.

## Input Format

Use a CSV with at least one address column. Optional columns are `brand` and `notes`.

```csv
address,brand,notes
"Corso Buenos Aires 12, Milano, Italy","Example Burger","synthetic portfolio sample"
"Stazione Centrale, Piazza Duca d'Aosta, Milano, Italy","Example Coffee","synthetic portfolio sample"
```

See `data/samples/sample_input.csv` for a safe sample file.

## Run

Recommended OpenAI-assisted run:

```bash
python main.py --input data/samples/sample_input.csv --output outputs/qsr_results --enable-context-search --context-radius 250 --location-classifier openai
```

The command creates:

- `outputs/qsr_results.csv`
- `outputs/qsr_results.xlsx`

The project also includes a rules-based classifier as a fallback for testing and comparison:

```bash
python main.py --input data/samples/sample_input.csv --output outputs/qsr_results_rules --enable-context-search --context-radius 250
```

For the internship workflow, the documented primary method is the OpenAI prompt-based classifier.

## Data Privacy

The public repository intentionally includes only synthetic sample files. Real internship CSVs, generated outputs, PDFs, and local working spreadsheets are stored under ignored folders such as `data/raw/` and `outputs/`.

Before publishing or sharing:

- Keep `.env` private.
- Do not commit real API keys.
- Do not publish client, employer, internship, or manually collected proprietary data unless you have permission.
- Use sample or anonymized files for portfolio demonstration.

## Quality Checks

Run tests:

```bash
python -m pytest
```

Rows should be manually reviewed when:

- `needs_manual_review` is `True`
- `match_confidence` is low
- `location_type_confidence` is low
- `error` is not empty

## Portfolio Summary

This project can be described on a CV as:

> Built a Python-based data enrichment workflow using Google Places API and OpenAI to convert QSR outlet address lists into analysis-ready datasets with ratings, review counts, geographic fields, coordinates, and location-type classification. Added manual-review flags and Excel exports to support internship market research.
