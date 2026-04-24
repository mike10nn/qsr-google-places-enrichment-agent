# Methodology

## Research Problem

The internship task required a structured dataset of QSR outlet locations. Manually collected addresses needed to be enriched with geographic and business metadata so they could be analyzed by region, province, city, rating, review volume, price range, and location context.

## Data Pipeline

1. Start with a CSV of outlet addresses.
2. Query Google Places Text Search using the address and optional brand.
3. Score returned candidates using address/name similarity.
4. Fetch details for the best match.
5. Optionally collect nearby context such as malls, stations, airports, and gas stations.
6. Send the matched outlet and context into an OpenAI prompt for `location_type` classification.
7. Export a CSV and formatted Excel workbook.
8. Review low-confidence or ambiguous rows manually.

## Location Type Categories

- City Center
- Shopping Mall
- Commercial Area
- Transport Hub
- Residential Area
- Highway / Service Area

## OpenAI Classification

The primary internship workflow used an OpenAI prompt to classify the custom `location_type` field. The classifier receives:

- matched Google place name
- formatted Google address
- Google place types
- nearby context from Google Places
- allowed location-type definitions

The model returns:

- one allowed `location_type`
- confidence score
- manual-review flag
- short reasoning text

## Data Quality Controls

The output includes both enrichment fields and audit fields. This makes the workflow useful for analysis while preserving enough traceability to check questionable rows.

Important checks:

- verify low match-confidence rows
- inspect rows where Google found no match
- check borderline location classifications
- compare a sample of results against Google Maps manually

## Limitations

- Google Places coverage and business metadata can vary by brand/location.
- `price_range` is only available when Google returns pricing information.
- Location type is a custom research classification, not a native Google field.
- OpenAI classification should be reviewed for high-stakes or ambiguous rows.
- API usage may create costs depending on volume and requested fields.

