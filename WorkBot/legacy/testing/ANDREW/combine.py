import os
import re
import pandas as pd
from datetime import datetime

# === CONFIGURATION ===
AUDIT_DIR = "audits"  # <- change this
PAR_FILE = "Ithaca Bakery - Meadow St - Foodager - Item Par List.xlsx"
CONSUMPTION_FILE = "Ithaca Bakery - Meadow St - Foodager - Consumption Details 2025-06-07 2025-06-26.xlsx"
OUTPUT_FILE = "meadow_par_analysis_output.xlsx"
AUDIT_START_DATE = datetime.strptime("2025-06-06", "%Y-%m-%d").date()
AUDIT_END_DATE = datetime.strptime("2025-06-26", "%Y-%m-%d").date()
AUDIT_DAYS = (AUDIT_END_DATE - AUDIT_START_DATE).days
BUFFER = 0.2

# === UTILS ===
def extract_date(filename):
    match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    return datetime.strptime(match.group(1), "%Y-%m-%d").date() if match else None

# === 1. Load & Combine Audit Files ===
all_audits = []

for fname in os.listdir(AUDIT_DIR):
    if not fname.endswith(".xlsx"):
        continue
    fdate = extract_date(fname)
    if not fdate:
        continue
    path = os.path.join(AUDIT_DIR, fname)
    try:
        df = pd.read_excel(path, sheet_name="4. Summary By Item", skiprows=6)
    except:
        try:
            df = pd.read_excel(path, sheet_name=fdate.strftime("%A"), skiprows=6)
        except:
            continue
    df.columns = df.columns.str.strip().str.upper()
    if not {"ITEM", "COUNT UNIT", "TOTAL"}.issubset(df.columns):
        continue
    df = df[["ITEM", "COUNT UNIT", "TOTAL"]].dropna(how="all")
    df["ITEM_BASE"] = df["ITEM"].str.strip().str.rsplit(" ", n=1).str[0]
    df["TOTAL"] = pd.to_numeric(df["TOTAL"], errors="coerce")
    df["DATE"] = fdate
    all_audits.append(df)

audits_df = pd.concat(all_audits, ignore_index=True)
latest_audit = audits_df[audits_df["DATE"] == AUDIT_END_DATE]
latest_trimmed = latest_audit[["ITEM_BASE", "COUNT UNIT", "TOTAL"]].rename(columns={"COUNT UNIT": "COUNT_UNIT"})

# === 2. Load Pars ===
pars_df = pd.read_excel(PAR_FILE, skiprows=4)
pars_df.columns = pars_df.columns.str.strip().str.upper()
pars_df["ITEM_BASE"] = pars_df["ITEM"].str.strip().str.rsplit(" ", n=1).str[0]
pars_df["PAR"] = pd.to_numeric(pars_df["PAR"], errors="coerce")
pars_trimmed = pars_df[["ITEM_BASE", "PAR"]].dropna()

# === 3. Load Consumption ===
cons_df = pd.read_excel(CONSUMPTION_FILE, skiprows=7)
cons_df.columns = cons_df.columns.str.strip().str.upper()
cons_df["ITEM_BASE"] = cons_df["ITEM"].str.strip().str.rsplit(" ", n=1).str[0]
cons_df["CONSUMED"] = pd.to_numeric(cons_df["CONSUMED"], errors="coerce")
cons_trimmed = cons_df[["ITEM_BASE", "CONSUMED"]]

# === 4. Merge + Compute ===
df = pd.merge(cons_trimmed, pars_trimmed, on="ITEM_BASE", how="outer")
df = pd.merge(df, latest_trimmed, on="ITEM_BASE", how="outer")

df["WEEKLY_USAGE"] = df["CONSUMED"] / AUDIT_DAYS * 7
df["IDEAL_PAR"] = df["WEEKLY_USAGE"] * (1 + BUFFER)

# Round to nearest 0.5
df["RECOMMENDED_PAR"] = df["IDEAL_PAR"].apply(lambda x: round(x * 2) / 2 if pd.notna(x) else None)

df["PAR_DEVIATION"] = df["PAR"] - df["IDEAL_PAR"]
df["PAR_DAYS_ON_HAND"] = df.apply(
    lambda r: (r["PAR"] / r["WEEKLY_USAGE"] * 7) if pd.notna(r["PAR"]) and r["WEEKLY_USAGE"] else None,
    axis=1
)

def par_action(row):
    if pd.isna(row["PAR"]) or pd.isna(row["RECOMMENDED_PAR"]):
        return "Unknown"
    elif row["PAR"] > row["RECOMMENDED_PAR"]:
        return "Lower Par"
    elif row["PAR"] < row["RECOMMENDED_PAR"]:
        return "Raise Par"
    return "Keep Par"

def risk_status(row):
    if pd.isna(row["TOTAL"]):
        return "Unknown"
    elif row["TOTAL"] < (row["WEEKLY_USAGE"] or 0) * 0.5:
        return "Stockout Risk"
    elif row["TOTAL"] > (row["IDEAL_PAR"] or 0) * 2:
        return "Overstocked"
    return "OK"

df["PAR_RECOMMENDATION"] = df.apply(par_action, axis=1)
df["RISK"] = df.apply(risk_status, axis=1)

# === 5. Output ===
final_cols = [
    "ITEM_BASE", "COUNT_UNIT", "WEEKLY_USAGE", "PAR", "PAR_DAYS_ON_HAND",
    "IDEAL_PAR", "RECOMMENDED_PAR", "PAR_RECOMMENDATION", "PAR_DEVIATION",
    "TOTAL", "RISK"
]
df[final_cols].sort_values(by="ITEM_BASE").to_excel(OUTPUT_FILE, index=False)

print(f"✅ Done! Saved to {OUTPUT_FILE}")
