import json
import os

import redis
from fastapi import APIRouter

router = APIRouter()

_redis = None
try:
    _redis = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True,
    )
    _redis.ping()
except Exception:
    _redis = None


@router.get("/summary")
async def get_summary():
    """Return latest data from all agents."""
    summary = {}

    if _redis:
        for key in ["pantau:latest", "analitik:latest", "bayar:latest"]:
            raw = _redis.get(key)
            if raw:
                summary[key.split(":")[0]] = json.loads(raw)

        reports = _redis.lrange("laporan:history", 0, 0)
        if reports:
            summary["laporan"] = json.loads(reports[0])
    else:
        summary["warning"] = "Redis not connected — running in stateless mode."

    return summary


@router.get("/reports")
async def get_reports(limit: int = 10):
    """Return last N daily reports."""
    if not _redis:
        return {"reports": [], "warning": "Redis not connected."}
    raw_reports = _redis.lrange("laporan:history", 0, limit - 1)
    return {"reports": [json.loads(r) for r in raw_reports]}
