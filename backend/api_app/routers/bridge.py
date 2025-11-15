import math
from fastapi import APIRouter
from ..db import get_db

router = APIRouter()
router = APIRouter()


@router.get("/year/{year}")
def bridges_by_year(year: int):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM pa_bridges_clean WHERE DATA_YEAR = ?", (year,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]



@router.get("/nearby")
def nearby(lat: float, lon: float, radius_km: float = 5):
    conn = get_db()

    # BBOX (approx)
    lat_min = lat - 0.1
    lat_max = lat + 0.1
    lon_min = lon - 0.1
    lon_max = lon + 0.1

    rows = conn.execute(
        """
        SELECT * FROM pa_bridges_clean
        WHERE LAT_016 BETWEEN ? AND ?
          AND LONG_017 BETWEEN ? AND ?
        """,
        (lat_min, lat_max, lon_min, lon_max)
    ).fetchall()

    conn.close()

    # Haversine distance
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return 2 * R * math.asin(math.sqrt(a))

    nearby_bridges = []
    for r in rows:
        # ensure lat/lon present and numeric
        try:
            rlat = float(r["LAT_016"])
            rlon = float(r["LONG_017"])
        except Exception:
            continue
        d = haversine(lat, lon, rlat, rlon)
        if d <= radius_km:
            item = dict(r)
            item["distance_km"] = round(d, 3)
            nearby_bridges.append(item)


    nearby_bridges.sort(key=lambda x: x["distance_km"])

    return nearby_bridges



@router.get("/{id}")
def get_bridge(id: str, year: int = None):
    conn = get_db()

    # If caller passed a short numeric id like '1', pad to 15 digits
    if id.isdigit() and len(id) < 15:
        id = id.zfill(15)

    if year:
        row = conn.execute(
            """
            SELECT * FROM pa_bridges_clean
            WHERE STRUCTURE_NUMBER_008 = ? AND DATA_YEAR = ?
            """,
            (id, year)
        ).fetchone()
    else:
        row = conn.execute(
            """
            SELECT * FROM pa_bridges_clean
            WHERE STRUCTURE_NUMBER_008 = ?
            ORDER BY DATA_YEAR DESC
            LIMIT 1
            """,
            (id,)
        ).fetchone()

    conn.close()

    if not row:
        return {"error": "bridge not found"}

    return dict(row)