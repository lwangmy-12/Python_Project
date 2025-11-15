from fastapi import APIRouter
from ..db import get_db

router = APIRouter()

@router.get("/{id}")
def get_bridge(id: str, year: int = None):
    conn = get_db()

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

    rows = conn.execute(
        """
        SELECT * FROM pa_bridges_clean
        WHERE LAT_016 BETWEEN ? AND ?
        AND LONG_017 BETWEEN ? AND ?
        """,
        (lat - 0.05, lat + 0.05, lon - 0.05, lon + 0.05)
    ).fetchall()
    conn.close()

    return [dict(r) for r in rows]
