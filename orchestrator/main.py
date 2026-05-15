"""
UMKM Autopilot — QwenPaw Orchestrator
Coordinates all agents via APScheduler event bus.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime

import redis
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from loguru import logger

from agents import (
    AnalitikAgent,
    BayarAgent,
    KontenAgent,
    LaporanAgent,
    PantauAgent,
)
from tools.rag_db import RAGDatabase

load_dotenv()

# ── Redis connection ─────────────────────────────────────────────────────────
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True,
)

# ── RAG DB ───────────────────────────────────────────────────────────────────
rag_db = RAGDatabase(
    host=os.getenv("CHROMA_HOST", "localhost"),
    port=int(os.getenv("CHROMA_PORT", 8001)),
)

# ── LLM client (Qwen3 via DashScope) ─────────────────────────────────────────
llm_client = None
if os.getenv("QWEN_API_KEY"):
    try:
        from tools.llm_client import QwenClient
        llm_client = QwenClient(api_key=os.getenv("QWEN_API_KEY"))
        logger.info("Qwen3 LLM client initialised.")
    except Exception as e:
        logger.warning(f"Could not initialise LLM client: {e}")

# ── Agent instances ──────────────────────────────────────────────────────────
KEYWORDS = os.getenv("MONITOR_KEYWORDS", "baju batik,tas kulit").split(",")

pantau_agent = PantauAgent(keywords=KEYWORDS, redis_client=redis_client)
analitik_agent = AnalitikAgent(rag_db=rag_db, llm_client=llm_client)
konten_agent = KontenAgent(llm_client=llm_client)
bayar_agent = BayarAgent()
laporan_agent = LaporanAgent(
    llm_client=llm_client,
    redis_client=redis_client,
)


async def job_pantau():
    logger.info("⏰ Scheduler: Running PantauAgent...")
    try:
        await pantau_agent.run()
    except Exception as e:
        logger.error(f"[Orchestrator] PantauAgent error: {e}")


async def job_laporan():
    logger.info("⏰ Scheduler: Running LaporanAgent...")
    try:
        await laporan_agent.run()
    except Exception as e:
        logger.error(f"[Orchestrator] LaporanAgent error: {e}")


def main():
    logger.info("🚀 UMKM Autopilot Orchestrator starting...")

    scheduler = AsyncIOScheduler()

    # Pantau: every N minutes
    interval = int(os.getenv("PANTAU_INTERVAL_MINUTES", 30))
    scheduler.add_job(job_pantau, "interval", minutes=interval, id="pantau")

    # Laporan: daily at configured hour
    laporan_hour = int(os.getenv("LAPORAN_HOUR", 23))
    laporan_min = int(os.getenv("LAPORAN_MINUTE", 0))
    scheduler.add_job(
        job_laporan, "cron", hour=laporan_hour, minute=laporan_min, id="laporan"
    )

    scheduler.start()
    logger.info(
        f"Scheduler active — Pantau every {interval}m, Laporan at {laporan_hour:02d}:{laporan_min:02d}"
    )

    loop = asyncio.get_event_loop()
    # Run pantau once on startup
    loop.run_until_complete(job_pantau())

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Orchestrator stopped.")
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    main()
