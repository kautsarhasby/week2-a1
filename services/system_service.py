import httpx
from fastapi import Response, status
from config import database


def get_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


def check_health(response: Response):
    db_status = "ok"
    supabase_status = "ok"

    try:
        with database.get_db() as conn:
            conn.execute("SELECT 1").fetchone()
    except Exception as e:
        db_status = f"error: {str(e)}"

    try:
        res = httpx.get(
            f"{database.SUPABASE_URL}/auth/v1/health",
            headers={"apikey": database.SUPABASE_KEY},
            timeout=5.0,
        )
        res.raise_for_status()
    except Exception as e:
        supabase_status = f"error: {str(e)}"

    if db_status != "ok" or supabase_status != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {
            "status": "error",
            "db": db_status,
            "supabase_auth": supabase_status,
        }

    return {
        "status": "ok",
        "db": "ok",
        "supabase_auth": "ok",
    }