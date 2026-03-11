import sys
import os
import pandas as pd
import re

def strip_count_unit(item_name: str) -> str:
    """
    Removes trailing unit identifiers (e.g., '12ct', '100ea') from item names.
    """
    if pd.isna(item_name):
        return item_name
    return re.sub(r'\s+\d+\s*[a-zA-Z]{1,4}$', '', item_name).strip()

def process_file(filename):
    if not os.path.exists(filename):
        print(f"❌ File not found: {filename}")
        sys.exit(1)

    try:
        df = pd.read_excel(filename)
    except Exception as e:
        print(f"❌ Failed to read Excel file: {e}")
        sys.exit(1)

    # Find ITEM column (case-insensitive)
    item_col = next((col for col in df.columns if col.strip().upper() == "ITEM"), None)
    if not item_col:
        print("❌ No 'ITEM' column found in the file.")
        sys.exit(1)

    df["ITEM"] = df[item_col].apply(strip_count_unit)

    output_path = filename.replace(".xlsx", ".cleaned.xlsx")
    df.to_excel(output_path, index=False)
    print(f"✅ Cleaned file saved as: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python strip_count_unit.py [filename.xlsx]")
        sys.exit(1)

    filename = sys.argv[1]
    process_file(filename)
