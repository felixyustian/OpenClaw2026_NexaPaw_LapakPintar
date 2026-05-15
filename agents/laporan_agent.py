"""
Laporan Agent — Synthesises cross-agent insights into a daily business report.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from loguru import logger


LAPORAN_PROMPT = """
Kamu adalah asisten bisnis UMKM Indonesia. Buat laporan harian bisnis berdasarkan data berikut:

Data Pantau (harga kompetitor):
{pantau_summary}

Data Analitik (tren penjualan):
{analitik_summary}

Data Bayar (rekonsiliasi):
{bayar_summary}

Format laporan:
1. Ringkasan Eksekutif (2 kalimat)
2. Highlight Penting (max 3 poin)
3. Rekomendasi Aksi untuk besok (max 3 poin)
4. Peringatan (jika ada anomali)

Bahasa Indonesia, to the point, mudah dipahami pemilik UMKM.
"""


class LaporanAgent:
    """Synthesises daily business insights from all agents and sends report."""

    name = "laporan_agent"

    def __init__(self, llm_client=None, redis_client=None, notifier=None):
        self.llm = llm_client
        self.redis = redis_client
        self.notifier = notifier  # e.g. WhatsApp / email notifier

    async def run(self) -> dict[str, Any]:
        logger.info("[LaporanAgent] Generating daily report.")

        pantau = self._load_from_redis("pantau:latest")
        analitik = self._load_from_redis("analitik:latest")
        bayar = self._load_from_redis("bayar:latest")

        report_text = await self._synthesise(pantau, analitik, bayar)

        report = {
            "report_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "generated_at": datetime.utcnow().isoformat(),
            "content": report_text,
            "sources": {
                "pantau": bool(pantau),
                "analitik": bool(analitik),
                "bayar": bool(bayar),
            },
        }

        # Store report
        if self.redis:
            self.redis.lpush("laporan:history", json.dumps(report, ensure_ascii=False))
            self.redis.ltrim("laporan:history", 0, 29)  # Keep last 30 reports

        # Notify owner
        if self.notifier:
            await self.notifier.send(report_text)

        logger.info("[LaporanAgent] Daily report generated and stored.")
        return report

    def _load_from_redis(self, key: str) -> dict:
        if not self.redis:
            return {}
        raw = self.redis.get(key)
        return json.loads(raw) if raw else {}

    async def _synthesise(
        self, pantau: dict, analitik: dict, bayar: dict
    ) -> str:
        if not self.llm:
            return self._mock_report()

        prompt = LAPORAN_PROMPT.format(
            pantau_summary=json.dumps(pantau, ensure_ascii=False)[:500],
            analitik_summary=json.dumps(analitik, ensure_ascii=False)[:500],
            bayar_summary=json.dumps(bayar, ensure_ascii=False)[:500],
        )
        return await self.llm.achat(prompt)

    def _mock_report(self) -> str:
        return (
            "📊 *Laporan Harian UMKM Autopilot*\n\n"
            "1️⃣ Ringkasan: Bisnis berjalan normal, tidak ada anomali signifikan hari ini.\n"
            "2️⃣ Highlight: Harga rata-rata kompetitor stabil di kisaran yang kompetitif.\n"
            "3️⃣ Rekomendasi: Pertahankan harga saat ini dan tingkatkan konten promosi.\n\n"
            "_[DEMO MODE — hubungkan LLM & Redis untuk laporan nyata]_"
        )
