import pandas as pd
import re

# File paths
cleaned_items_path = "CTB_cleaned_items.xlsx"             # File with ITEM and STORAGE
analysis_path = "_CTB_par_analysis_output.xlsx"            # Full analysis file
output_path = "ctb_filtered_analysis_output.xlsx"         # Output file

# Load files
cleaned_df = pd.read_excel(cleaned_items_path)
analysis_df = pd.read_excel(analysis_path)

# Normalize column names

def strip_count_unit(item_name: str) -> str:
    """
    Removes a count unit at the end of an item name string.
    Example: "Item Name 1ct" -> "Item Name"
             "Example Item 2ea" -> "Example Item"
    """
    if pd.isna(item_name):
        return item_name
    return re.sub(r'\s+\d+\s*[a-zA-Z]{1,3}$', '', item_name).strip()

cleaned_df.columns = cleaned_df.columns.str.strip().str.upper()
analysis_df.columns = analysis_df.columns.str.strip().str.upper()

# Ensure consistent item formatting
cleaned_df["ITEM"] = cleaned_df["ITEM"].str.strip().apply(strip_count_unit)
analysis_df["ITEM_BASE"] = analysis_df["ITEM_BASE"].str.strip()

# Merge STORAGE info into analysis based on ITEM name
filtered_df = analysis_df.merge(
    cleaned_df[["ITEM", "STORAGE"]],
    how="inner",
    left_on="ITEM_BASE",
    right_on="ITEM"
)

# Drop the duplicate key column from merge
filtered_df.drop(columns=["ITEM"], inplace=True)

# Reorder if desired (optional)
column_order = ["ITEM_BASE", "STORAGE"] + [col for col in filtered_df.columns if col not in ["ITEM_BASE", "STORAGE"]]
filtered_df = filtered_df[column_order]

# Save to Excel
filtered_df.to_excel(output_path, index=False)
print(f"✅ Filtered analysis with storage info saved as '{output_path}'")
