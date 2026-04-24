# Data Dictionary

| Column | Description |
| --- | --- |
| `input_address` | Original address supplied in the input CSV. |
| `brand` | Optional brand name supplied by the user. |
| `matched_name` | Google Places name for the selected match. |
| `matched_address` | Google formatted address for the selected match. |
| `region` | Region parsed from Google address components. |
| `province` | Province parsed from Google address components. |
| `city` | City/locality parsed from Google address components. |
| `price_range` | Google price range or price level when available. |
| `customer_rating` | Google customer rating. |
| `review_count` | Number of Google user ratings/reviews. |
| `latitude` | Latitude of the matched place. |
| `longitude` | Longitude of the matched place. |
| `location_type` | Custom research category assigned by the OpenAI classifier or fallback rules. |
| `location_type_confidence` | Confidence score for the assigned location type. |
| `needs_manual_review` | Boolean flag for uncertain matches or classifications. |
| `match_confidence` | Similarity score for the selected Google candidate. |
| `google_place_id` | Google Places ID for audit/reference. |
| `google_maps_uri` | Google Maps URL for manual review. |
| `primary_type` | Google primary place type. |
| `place_types` | Google place types returned for the match. |
| `business_status` | Google business status, such as operational/closed. |
| `notes` | Optional notes supplied in the input CSV. |
| `source` | Describes whether output came from Google Places plus OpenAI or fallback rules. |
| `error` | Error message if enrichment failed for a row. |

