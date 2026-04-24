from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge notes and address columns into one address column for quick CSV cleanup."
    )
    parser.add_argument("--input", required=True, help="Path to the source CSV.")
    parser.add_argument("--output", required=True, help="Path for the cleaned CSV.")
    parser.add_argument(
        "--merged-column",
        default="address",
        help="Name of the merged output column.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input)

    required = {"notes", "address"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {sorted(missing)}")

    merged = (
        df["notes"].fillna("").astype(str).str.strip()
        + ", "
        + df["address"].fillna("").astype(str).str.strip()
    ).str.strip(", ")

    df = df.drop(columns=["notes", "address"])
    df.insert(0, args.merged_column, merged)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Wrote cleaned CSV to {output_path}")


if __name__ == "__main__":
    main()

