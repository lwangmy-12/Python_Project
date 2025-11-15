import pandas as pd
import sqlite3
import requests
import csv
from io import StringIO

# Years to download
years = list(range(2019, 2025 + 1))
all_dfs = []

for year in years:
    short_year = str(year)[-2:]
    url = f"https://www.fhwa.dot.gov/bridge/nbi/{year}/delimited/PA{short_year}.txt"

    print(f"Downloading PA {year} data from: {url}")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to download: {url}")
        continue

    text = response.text

    fixed_rows = []
    reader = csv.reader(StringIO(text))

    for row in reader:
        if len(row) > 123:
            row = row[:122] + [",".join(row[122:])]

        if len(row) < 123:
            row = row + [""] * (123 - len(row))

        fixed_rows.append(row)

    # First row is header
    header = fixed_rows[0]
    data = fixed_rows[1:]

    df = pd.DataFrame(data, columns=header)
    df["DATA_YEAR"] = year

    all_dfs.append(df)

print("Merging all PA data from 2019 to 2025...")
full_df = pd.concat(all_dfs, ignore_index=True)
print("Total records:", full_df.shape)

#to SQLite database
print("Creating SQLite database nbi_pa.db ...")
conn = sqlite3.connect("nbi_pa.db")

full_df.to_sql("pa_bridges", conn, if_exists="replace", index=False)

print("Creating indexes ...")
conn.execute("CREATE INDEX IF NOT EXISTS idx_structure ON pa_bridges(STRUCTURE_NUMBER_008)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_year ON pa_bridges(DATA_YEAR)")

conn.commit()
conn.close()

print("Done. SQLite database 'nbi_pa.db' has been created.")
