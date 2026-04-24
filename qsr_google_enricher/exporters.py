from __future__ import annotations

from pathlib import Path

import pandas as pd


FINAL_COLUMN_ORDER = [
    "input_address",
    "brand",
    "matched_name",
    "matched_address",
    "region",
    "province",
    "city",
    "price_range",
    "customer_rating",
    "review_count",
    "latitude",
    "longitude",
    "location_type",
    "location_type_confidence",
    "needs_manual_review",
    "match_confidence",
    "google_place_id",
    "google_maps_uri",
    "primary_type",
    "place_types",
    "business_status",
    "notes",
    "source",
    "error",
]


def export_outputs(df: pd.DataFrame, output_base_path: str | Path) -> tuple[Path, Path]:
    output_base_path = Path(output_base_path)
    output_base_path.parent.mkdir(parents=True, exist_ok=True)

    missing = [column for column in FINAL_COLUMN_ORDER if column not in df.columns]
    if missing:
        raise ValueError(f"Dataframe is missing expected columns: {missing}")

    df = df[FINAL_COLUMN_ORDER].copy()

    csv_path = output_base_path.with_suffix(".csv")
    xlsx_path = output_base_path.with_suffix(".xlsx")

    df.to_csv(csv_path, index=False)

    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="QSR_Enriched", index=False)
        workbook = writer.book
        worksheet = writer.sheets["QSR_Enriched"]

        header_fill = "1F4E78"
        header_font = "FFFFFF"

        for cell in worksheet[1]:
            cell.fill = __import__("openpyxl").styles.PatternFill(
                fill_type="solid",
                fgColor=header_fill,
            )
            cell.font = __import__("openpyxl").styles.Font(bold=True, color=header_font)

        widths = {
            "A": 40, "B": 18, "C": 26, "D": 48, "E": 18, "F": 18, "G": 18,
            "H": 20, "I": 18, "J": 18, "K": 14, "L": 14, "M": 24, "N": 20,
            "O": 18, "P": 18, "Q": 24, "R": 40, "S": 20, "T": 42, "U": 18,
            "V": 22, "W": 38, "X": 30,
        }
        for col, width in widths.items():
            worksheet.column_dimensions[col].width = width

        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        for row in worksheet.iter_rows(min_row=2, min_col=9, max_col=18):
            for cell in row:
                if cell.column in {9, 11, 12, 14, 16}:  # rating, lat/lng, confidences
                    cell.number_format = "0.00"
                elif cell.column == 10:  # review_count
                    cell.number_format = "0"

    return csv_path, xlsx_path
