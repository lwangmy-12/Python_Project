PA Bridge Analysis — README

Project overview
----------------
This project ingests National Bridge Inventory (NBI) records for Pennsylvania, cleans and normalizes the data, stores a cleaned table in SQLite, exposes a small REST API (FastAPI) for queries, and provides a lightweight Leaflet-based frontend for visual exploration.

Repository layout
-----------------
- data/
  - clean_pa_bridges.py      # Data cleaning script (reads raw `nbi_pa.db` and writes `pa_bridges_clean.db`)
  - txt_process.py           # Downloader/parser that fetches NBI delimited text files and builds `nbi_pa.db`
  - nbi_pa.db                # (raw) original NBI SQLite database (produced by the txt script)
  - pa_bridges_clean.db      # (produced) cleaned SQLite database
- backend/
  - api_app/
    - main.py                # FastAPI app and router mounting
    - db.py                  # helper to open pa_bridges_clean.db (path resolved relative to module)
    - routers/
      - bridge.py            # bridge endpoints (get by id/year, list by year, nearby)
      - stats.py             # stats endpoints (condition aggregations)
    - models/                # pydantic models (basic)
- frontend/
  - index.html               # frontend UI (Leaflet map + controls)
  - style.css                # styles for frontend
  - script.js                # frontend behavior and API calls
  - map.html                 # (generated) full map page (can be produced by `analysis/map_generate.py`)
- utilities and misc (top-level)
  - add_legacy_route.py      # small helper used during development to add compatibility routes
  - update_main.py           # helper script used to modify `main.py` (development)
  - testapi.py               # quick local TestClient-based checks
  - scripts/                 # any auxiliary scripts (data helpers, analysis tools)
  - analysis/                # notebooks or analysis artifacts

Note: some development helper scripts and generated files may be present in the repository root. The key
production files are `data/clean_pa_bridges.py`, `data/pa_bridges_clean.db`, `backend/api_app/*`, and the
`frontend/` static site.

Requirements
------------
- Python 3.10+ (3.11/3.13 tested in this environment)
- The following Python packages (install via pip):
  - pandas
  - fastapi
  - uvicorn[standard]
  - httpx (optional - for TestClient, tests)

Install dependencies (PowerShell):

```powershell
python -m pip install --upgrade pip
pip install pandas fastapi uvicorn[standard] httpx
```

Data acquisition & cleaning
---------------------------
This project separates data acquisition (downloading/parsing delimited NBI files) from cleaning.

1) Data acquisition — `data/txt_process.py`

- The downloader/parser `data/txt_process.py` fetches FHWA NBI delimited text files (e.g. `PA19.txt`...`PA25.txt`) and builds a raw SQLite database `data/nbi_pa.db` with the `pa_bridges` table.
- By default the script in this repository downloads years 2019–2025; adjust the `years` variable in the script to change the range.
- Network access is required; if FHWA is unreachable the script will skip that year and continue.
- To run the downloader (from project root):

```powershell
python data/txt_process.py
```

After running this script you should have `data/nbi_pa.db` containing the raw `pa_bridges` table.

2) Data cleaning — `data/clean_pa_bridges.py`

The cleaning script is `data/clean_pa_bridges.py`. It performs these tasks:
- Loads raw table `pa_bridges` from `nbi_pa.db` (expects `nbi_pa.db` to be present in the `data/` folder).
- Replaces common "bad" markers with missing values and coerces numeric columns.
- Parses NBI-style encoded coordinates (formats like `DDMMSSss` or `DDDMMSSss`) into decimal degrees.
- Drops rows with missing numeric fields.
- Performs a group-level completeness check per `(DATA_YEAR, STRUCTURE_NUMBER_008)` and keeps only groups where required attributes exist.
- Saves cleaned table to `data/pa_bridges_clean.db` and creates indexes on `STRUCTURE_NUMBER_008` and `DATA_YEAR`.

To run the cleaner (from project root):

```powershell
python data/clean_pa_bridges.py
```

This will create/update `data/pa_bridges_clean.db`.

Backend (API)
-------------
The backend lives at `backend/api_app`. It uses FastAPI and reads from the cleaned SQLite DB.

Important: `backend/api_app/db.py` resolves the DB path relative to the module so the API can be started from any working directory. The DB file expected is `data/pa_bridges_clean.db` in the project root.

Start the API with uvicorn (PowerShell):

```powershell
uvicorn backend.api_app.main:app --reload
```

API endpoints (examples)
------------------------
- Get bridge by id (latest or specific year):
  - Latest: `GET /api/bridges/{id}`
    - Example (PowerShell):
      ```powershell
      Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/bridges/000000000000957'
      ```
  - Specific year: `GET /api/bridges/{id}?year=2019`
    - Example:
      ```powershell
      Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/bridges/000000000000957?year=2019'
      ```

- List bridges by year: `GET /api/bridges/year/{year}`
  - Example:
    ```powershell
    Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/bridges/year/2019'
    ```

- Nearby search (naive bounding box): `GET /api/bridges/nearby?lat={lat}&lon={lon}&radius_km={r}`
  - Example:
    ```powershell
    Invoke-RestMethod -Uri '"http://127.0.0.1:8000/api/bridges/nearby?lat=40.5&lon=-79.9&radius_km=5"'
    ```

- Condition stats by year: `GET /api/stats/condition/year/{year}`
  - Example:
    ```powershell
    Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/stats/condition/year/2019'
    ```

Interactive docs
----------------
With the server running visit:
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Redoc: `http://127.0.0.1:8000/redoc`

Frontend
--------
The frontend is a simple static UI that calls the API. You can open `frontend/index.html` directly in a browser (some browsers restrict `file://` + AJAX; if that occurs serve the folder with a simple static server).

Serve the frontend directory quickly (PowerShell):

```powershell
# Python 3 builtin http.server, from project frontend folder
cd frontend
python -m http.server 5500
# Then open http://127.0.0.1:5500/index.html
```

Alternatively, a full interactive map page `frontend/map.html` can be generated from the cleaned database using the analysis helper:

```powershell
python analysis/map_generate.py
```

This script reads `data/pa_bridges_clean.db` (default year=2025 in the script), produces an interactive Folium map and saves it to `frontend/map.html`.

Testing and debugging
---------------------
- FastAPI TestClient is useful for in-process testing. If you run tests that import `TestClient`, ensure `httpx` is installed.
- If you see 500 errors on API calls, check uvicorn stdout for full traceback and verify the DB file exists at `data/pa_bridges_clean.db`.
- If endpoints return 404 for `/api/bridge/{id}`, note that the project supports `/api/bridges/{id}` (plural). A legacy alias is also provided by the app for backward compatibility.

Development notes
-----------------
- Coordinate parsing: the cleaner decodes NBI DMS-like integers into decimal degrees (e.g., `35271855` -> 35.45515). If you have GPS decimal columns instead, the parser preserves decimal values.
- Database access: `backend/api_app/db.py` constructs an absolute path to `data/pa_bridges_clean.db` relative to the module file to avoid working-directory issues.
- To avoid heavy reprocessing during development, you can reuse the existing `pa_bridges_clean.db` produced earlier and skip rerunning the cleaner.

Possible improvements
---------------------
- Replace naive bounding-box proximity search with haversine distance or use a spatial index (R-tree or PostGIS) for accurate and fast nearest-neighbor queries.
- Add OpenAPI `response_model` annotations and Pydantic models for clearer documentation and consistent responses.
- Add unit tests for the cleaning pipeline and API endpoints.
- Containerize with Docker for reproducible deployment.

Contact / Author
----------------
Mingyu Wang

License
-------
This project is intended for academic use only. 
