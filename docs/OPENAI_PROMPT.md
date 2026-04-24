# OpenAI Prompt Notes

The project uses OpenAI for the custom `location_type` classification step. Google Places does not directly provide the exact research categories used for the internship, so the prompt converts place metadata and nearby context into one allowed label.

## System Prompt

```text
You classify QSR outlet locations in Italy into exactly one allowed category. Be conservative. If the evidence is weak or ambiguous, still choose the best category but set needs_manual_review=true and lower confidence.
```

## User Prompt Structure

The runtime prompt includes:

- allowed location types and definitions
- classification rules for edge cases
- matched outlet display name
- matched formatted address
- Google place types
- nearby context from Google Places

The model must return a structured object with:

- `location_type`
- `confidence`
- `needs_manual_review`
- `reason`

## Important Portfolio Note

The internship workflow should be described as OpenAI prompt-based classification. The rules-based classifier remains in the codebase as a fallback and testable baseline, but it was not the main method used for the research workflow.

