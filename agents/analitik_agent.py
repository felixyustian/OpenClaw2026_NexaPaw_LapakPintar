"""
Analitik Agent — Sales analytics, anomaly detection, demand prediction.
Uses RAG DB for historical data and Qwen3 for reasoning.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any

from loguru import logger

from tools.rag_db import RAGDatabase


class AnalitikAgent:
    """Analyses sales trends and predicts demand using RAG + Qwen3 reasoning."""

    name = "analitik_agent"

    def __init__(self, rag_db: RAGDatabase, llm_client=None):
        self.rag = rag_db
        self.llm = llm_client

    async def run(self, sales_data: list[dict]) -> dict[str, Any]:
        logger.info(f"[AnalitikAgent] Analysing {len(sales_data)} sales records.")

        # Store new data points
        for record in sales_data:
            self.rag.upsert(record)

        # Retrieve historical context
        history = self.rag.query("sales trend last 30 days", top_k=20)

        # Detect anomalies
        anomalies = self._detect_anomalies(sales_data)

        # Predict demand via LLM reasoning
        prediction = await self._predict_demand(history, sales_data)

        return {
            "status": "ok",
            "anomalies": anomalies,
            "demand_prediction": prediction,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _detect_anomalies(self, records: list[dict]) -> list[dict]:
        """Simple z-score anomaly detection on revenue field."""
        if len(records) < 3:
            return []

        revenues = [r.get("revenue", 0) for r in records]
        mean = sum(revenues) / len(revenues)
        variance = sum((r - mean) ** 2 for r in revenues) / len(revenues)
        std = variance ** 0.5

        anomalies = []
        for rec in records:
            rev = rec.get("revenue", 0)
            if std > 0 and abs(rev - mean) / std > 2.5:
                anomalies.append({**rec, "z_score": round((rev - mean) / std, 2)})

        return anomalies

    async def _predict_demand(
        self, history: list[dict], current: list[dict]
    ) -> str:
        if not self.llm:
            return "LLM not configured — prediction unavailable in demo mode."

        prompt = f"""
Kamu adalah analis bisnis UMKM Indonesia. Berdasarkan data historis berikut:
{json.dumps(history[:5], ensure_ascii=False)}

Dan data terkini:
{json.dumps(current[:5], ensure_ascii=False)}

Prediksi permintaan untuk 7 hari ke depan dan berikan rekomendasi stok dalam 3 kalimat.
"""
        response = await self.llm.achat(prompt)
        return response
