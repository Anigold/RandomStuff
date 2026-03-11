import pandas as pd
from datetime import datetime

# ------------------------
# Configuration
# ------------------------
AUDIT_DAYS = 28
BUFFER_PERCENT = 0.20
PURCHASE_LOG_PATH = "./PurchaseLogs/Collegetown Bagels - College Ave - Foodager - Purchase Log 2025-06-26 2025-06-26.xlsx"

# ------------------------
# Load Audit File
# ------------------------
audit_path = "./Audits/Collegetown Bagels - College Ave - Foodager - Audit 2025-07-17.xlsx"
audit_df = pd.read_excel(audit_path, sheet_name="4. Summary By Item", skiprows=6)
audit_df.dropna(how='all', inplace=True)
audit_df.columns = audit_df.columns.str.strip().str.upper()
audit_df["ITEM_BASE"] = audit_df["ITEM"].str.strip()

audit_trimmed = audit_df[["ITEM_BASE", "COUNT UNIT", "TOTAL"]].copy()
audit_trimmed.rename(columns={"COUNT UNIT": "COUNT_UNIT"}, inplace=True)

# ------------------------
# Load Pars File
# ------------------------
pars_path = "./ItemPars/Collegetown Bagels - College Ave - Foodager - Item Par List.xlsx"
pars_df = pd.read_excel(pars_path, skiprows=4)
pars_df.dropna(how='all', inplace=True)
pars_df.columns = pars_df.columns.str.strip().str.upper()

pars_df["ITEM"] = pars_df["ITEM"].str.strip()
pars_df["ITEM_BASE"] = pars_df["ITEM"].str.rsplit(" ", n=1).str[0]
pars_df["PAR"] = pd.to_numeric(pars_df["PAR"], errors="coerce")

pars_trimmed = pars_df[["ITEM_BASE", "PAR"]].copy()
pars_trimmed.dropna(subset=["ITEM_BASE", "PAR"], inplace=True)

# ------------------------
# Load Consumption Details
# ------------------------
consumption_path = "./ConsumptionDetails/Collegetown Bagels - College Ave - Foodager - Consumption Details 2025-06-12 2025-06-25.xlsx"
consumption_df = pd.read_excel(consumption_path, skiprows=7)
consumption_df.dropna(how='all', inplace=True)
consumption_df.columns = consumption_df.columns.str.strip().str.upper()

if "ITEM" in consumption_df.columns:
    consumption_df["ITEM"] = consumption_df["ITEM"].str.strip()
    consumption_df["ITEM_BASE"] = consumption_df["ITEM"].str.rsplit(" ", n=1).str[0]

if "CONSUMED" in consumption_df.columns:
    consumption_df["CONSUMED"] = pd.to_numeric(consumption_df["CONSUMED"], errors="coerce")

consumption_trimmed = consumption_df[["ITEM_BASE", "CONSUMED"]].copy()

# ------------------------
# Load Purchase Log
# ------------------------
purchase_df = pd.read_excel(PURCHASE_LOG_PATH, skiprows=5)
purchase_df.dropna(how='all', inplace=True)
purchase_df.columns = purchase_df.columns.str.strip().str.upper()

if "ITEM" in purchase_df.columns and "RECEIVED DATE" in purchase_df.columns:
    purchase_df["ITEM"] = purchase_df["ITEM"].str.strip()
    purchase_df["ITEM_BASE"] = purchase_df["ITEM"].str.rsplit(" ", n=1).str[0]
    purchase_df["RECEIVED DATE"] = pd.to_datetime(purchase_df["RECEIVED DATE"], errors="coerce")

# Calculate deliveries per item
purchase_freq = (
    purchase_df.dropna(subset=["RECEIVED DATE"])
    .groupby("ITEM_BASE")["RECEIVED DATE"]
    .nunique()
    .reset_index()
)

# Estimate delivery frequency in days
start_date = purchase_df["RECEIVED DATE"].min()
end_date = purchase_df["RECEIVED DATE"].max()
cycle_days = (end_date - start_date).days

purchase_freq["DELIVERIES_PER_WEEK"] = (purchase_freq["RECEIVED DATE"] / cycle_days) * 7
purchase_freq.drop(columns="RECEIVED DATE", inplace=True)

# ------------------------
# Merge All Data
# ------------------------
merged = pd.merge(consumption_trimmed, pars_trimmed, on="ITEM_BASE", how="outer")
merged = pd.merge(merged, audit_trimmed, on="ITEM_BASE", how="outer")
merged = pd.merge(merged, purchase_freq, on="ITEM_BASE", how="left")

# ------------------------
# Analysis Calculations
# ------------------------
merged["WEEKLY_USAGE"] = merged["CONSUMED"] / AUDIT_DAYS * 7

# Default to 1 delivery/week if unknown
# merged["DELIVERIES_PER_WEEK"].fillna(1, inplace=True)

# # Adjusted PAR based on delivery frequency
# merged["IDEAL_PAR"] = merged.apply(
#     lambda row: (row["WEEKLY_USAGE"] / row["DELIVERIES_PER_WEEK"]) * (1 + BUFFER_PERCENT)
#     if row["DELIVERIES_PER_WEEK"] > 0 else row["WEEKLY_USAGE"] * (1 + BUFFER_PERCENT),
#     axis=1
# )

# Set ideal par to 2 weeks of usage
merged["IDEAL_PAR"] = merged["WEEKLY_USAGE"] * 2


def round_to_half(x):
    if pd.isna(x):
        return None
    return round(x * 2) / 2

merged["RECOMMENDED_PAR"] = merged["IDEAL_PAR"].apply(round_to_half)

# How many days PAR would cover
merged["PAR_DAYS_ON_HAND"] = merged.apply(
    lambda row: (row["PAR"] / row["WEEKLY_USAGE"]) * 7 if row["WEEKLY_USAGE"] and not pd.isna(row["PAR"]) else None,
    axis=1
)

# Par adjustment recommendation
merged["PAR_DEVIATION"] = merged["PAR"] - merged["IDEAL_PAR"]
merged["PAR_RECOMMENDATION"] = merged.apply(
    lambda row: "Unknown" if pd.isna(row["PAR"]) or pd.isna(row["RECOMMENDED_PAR"])
    else "Lower Par" if row["PAR"] > row["RECOMMENDED_PAR"]
    else "Raise Par" if row["PAR"] < row["RECOMMENDED_PAR"]
    else "Keep Par",
    axis=1
)

# Risk Assessment
def assess_risk(row):
    if pd.isna(row["TOTAL"]):
        return "Unknown"
    elif row["TOTAL"] < (row["WEEKLY_USAGE"] or 0) * 0.5:
        return "Stockout Risk"
    elif row["TOTAL"] > (row["IDEAL_PAR"] or 0) * 2:
        return "Overstocked"
    return "OK"

merged["RISK"] = merged.apply(assess_risk, axis=1)

# ------------------------
# Output Final Analysis
# ------------------------
final_columns = [
    "ITEM_BASE", "COUNT_UNIT", "WEEKLY_USAGE", "PAR", "PAR_DAYS_ON_HAND",
    "IDEAL_PAR", "RECOMMENDED_PAR", "PAR_RECOMMENDATION", "PAR_DEVIATION",
    "DELIVERIES_PER_WEEK", "TOTAL", "RISK"
]

analysis_df = merged[final_columns].sort_values(by="ITEM_BASE")
analysis_df.to_excel("_CTB_par_analysis_output.xlsx", index=False)

print(analysis_df.head())
print("✅ Analysis complete. Saved as 'par_analysis_output.xlsx'")
