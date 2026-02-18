import os
from typing import List
import pandas as pd


def save_to_excel(data_list: List[dict], output_path: str):
    if not data_list:
        print("No data to save.")
        return

    try:
        # Compute ordered columns: keep Filename/Status/Error first if present
        first = data_list[0]
        cols = []
        for k in ("Filename", "Status", "Error"):
            if k in first:
                cols.append(k)

        # add remaining keys in order of first dict
        for k in first.keys():
            if k not in cols:
                cols.append(k)

        df = pd.DataFrame(data_list)

        # Some PDFs might have slightly different keys; ensure all columns exist
        for c in cols:
            if c not in df.columns:
                df[c] = ""

        # Ensure directory exists
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

        # Save with openpyxl engine
        df.to_excel(output_path, index=False, engine="openpyxl")
        print(f"Saved {len(df)} records to {output_path}")

    except Exception as e:
        print(f"Error saving to Excel: {e}")
