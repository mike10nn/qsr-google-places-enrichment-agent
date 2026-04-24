from __future__ import annotations

from pathlib import Path

import pandas as pd

from qsr_google_enricher.models import InputRow, OutletRecord


def read_input_csv(path: str | Path) -> list[InputRow]:
    df = pd.read_csv(path)
    return [InputRow.from_dict(row) for row in df.to_dict(orient="records")]


def records_to_dataframe(records: list[OutletRecord]) -> pd.DataFrame:
    return pd.DataFrame([record.to_dict() for record in records])
