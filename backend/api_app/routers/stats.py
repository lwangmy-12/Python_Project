from fastapi import APIRouter
from ..db import get_db

router = APIRouter()

@router.get("/condition/year/{year}")
def condition_stats(year: int):
    conn = get_db()
    rows = conn.execute(
        """
        SELECT
            DECK_COND_058,
            SUPERSTRUCTURE_COND_059,
            SUBSTRUCTURE_COND_060,
            COUNT(*) as count
        FROM pa_bridges_clean
        WHERE DATA_YEAR = ?
        GROUP BY 1,2,3
        """,
        (year,)
    ).fetchall()
    conn.close()

    return [dict(r) for r in rows]
