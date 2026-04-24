# User Manual

## Purpose

Use this tool to enrich a CSV of QSR outlet addresses with Google Places data and an OpenAI-assisted `location_type` classification.

## Requirements

- Python 3.11 or newer
- Google Maps Platform API key with Places API enabled
- OpenAI API key and model name for the OpenAI classifier

## Installation

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example`:

```bash
copy .env.example .env
```

Add:

```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

## Prepare Input

The input CSV must contain one of these address columns:

- `address`
- `street_address`
- `input_address`

Recommended optional columns:

- `brand`
- `notes`

Example:

```csv
address,brand,notes
"Corso Buenos Aires 12, Milano, Italy","Example Burger","synthetic sample"
```

## Run The Workflow

Recommended command:

```bash
python main.py --input data/samples/sample_input.csv --output outputs/qsr_results --enable-context-search --context-radius 250 --location-classifier openai
```

This creates:

- `outputs/qsr_results.csv`
- `outputs/qsr_results.xlsx`

## Review The Results

Open the Excel file and filter:

- `needs_manual_review = True`
- low `match_confidence`
- low `location_type_confidence`
- rows with a value in `error`

Correct ambiguous rows manually before using the dataset in final analysis.

