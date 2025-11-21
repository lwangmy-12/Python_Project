import pandas as pd
import sqlite3
import os

folder = os.path.dirname(__file__)
os.chdir(folder)

print("Loading nbi_pa.db ...")
conn = sqlite3.connect("nbi_pa.db")
df = pd.read_sql_query("SELECT * FROM pa_bridges", conn)
conn.close()

print("Original rows:", df.shape)

required_cols = [
    "STATE_CODE_001","COUNTY_CODE_003","STRUCTURE_NUMBER_008",
    "LOCATION_009","FEATURES_DESC_006A","FACILITY_CARRIED_007",
    "LAT_016","LONG_017",
    "YEAR_BUILT_027","STRUCTURE_KIND_043A","STRUCTURE_TYPE_043B",
    "DECK_STRUCTURE_TYPE_107","MAIN_UNIT_SPANS_045",
    "MAX_SPAN_LEN_MT_048","STRUCTURE_LEN_MT_049",
    "ADT_029","YEAR_ADT_030",
    "DECK_COND_058","SUPERSTRUCTURE_COND_059","SUBSTRUCTURE_COND_060",
    "OPERATING_RATING_064","INVENTORY_RATING_066","STRUCTURAL_EVAL_067",
    "DATA_YEAR"
]

df = df[required_cols].copy()


bad_values = ["", " ", "  ", ".", "N", "*", "''", "“”", "''", "`", "'", "\"", "NaN"]
df.replace(bad_values, pd.NA, inplace=True)      

float_cols = ["LAT_016","LONG_017","MAX_SPAN_LEN_MT_048","STRUCTURE_LEN_MT_049"]
int_cols = [
    "STATE_CODE_001","COUNTY_CODE_003","YEAR_BUILT_027",
    "MAIN_UNIT_SPANS_045","ADT_029","YEAR_ADT_030",
    "DECK_COND_058","SUPERSTRUCTURE_COND_059","SUBSTRUCTURE_COND_060",
    "OPERATING_RATING_064","INVENTORY_RATING_066","STRUCTURAL_EVAL_067",
    "DATA_YEAR"
]

df[float_cols] = df[float_cols].apply(pd.to_numeric, errors="coerce")
df[int_cols]   = df[int_cols].apply(pd.to_numeric, errors="coerce")


# Fix coordinates

def dms_to_decimal(x):
    """
    Convert NBI encoded DMS (DDMMSS.SS or DDDMMSS.SS) to decimal degrees.
    x is an integer like 35271855 or 081055065.
    """
    if pd.isna(x):
        return pd.NA
    
    x = int(x)

    sec = (x % 10000) / 100.0
    x //= 10000
    
    minutes = x % 100
    x //= 100

    degrees = x

    return degrees + minutes/60 + sec/3600


# Convert latitude
df["LAT_016"] = df["LAT_016"].apply(dms_to_decimal)

# Convert longitude 
df["LONG_017"] = df["LONG_017"].apply(lambda v: -dms_to_decimal(v))

# FILTERING

before = df.shape[0]
numeric_cols = float_cols + int_cols

df = df.dropna(subset=numeric_cols)
after_numeric = df.shape[0]

print(f"Rows before cleaning: {before}")
print(f"Rows after dropping rows with missing numeric fields: {after_numeric}")
print(f"Removed by numeric filtering: {before - after_numeric} rows")

# GROUP FILTER

valid_mask = pd.Series(True, index=df.groupby(["DATA_YEAR", "STRUCTURE_NUMBER_008"]).groups.keys())

grouped = df.groupby(["DATA_YEAR", "STRUCTURE_NUMBER_008"])

df = df.dropna(subset=required_cols)


print(f"Rows after strict row-level filtering: {df.shape[0]}")

#save database 
conn2 = sqlite3.connect("pa_bridges_clean.db")
df.to_sql("pa_bridges_clean", conn2, if_exists="replace", index=False)

conn2.execute("CREATE INDEX IF NOT EXISTS idx_struct ON pa_bridges_clean(STRUCTURE_NUMBER_008)")
conn2.execute("CREATE INDEX IF NOT EXISTS idx_year ON pa_bridges_clean(DATA_YEAR)")

conn2.commit()
conn2.close()

print("Clean database created: pa_bridges_clean.db")
print(df.head())
