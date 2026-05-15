"""
Bayar Agent — Transaction reconciliation & disbursement via DOKU REST API v2.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from loguru import logger

from tools.doku_client import DOKUClient


class BayarAgent:
    """Handles payment reconciliation and auto-disbursement via DOKU API."""

    name = "bayar_agent"

    def __init__(self, doku_client: DOKUClient | None = None):
        self.doku = doku_client or DOKUClient(
            client_id=os.getenv("DOKU_CLIENT_ID", ""),
            secret_key=os.getenv("DOKU_SECRET_KEY", ""),
        )

    async def reconcile(self, expected_transactions: list[dict]) -> dict[str, Any]:
        """Compare expected vs actual transactions and flag discrepancies."""
        logger.info(f"[BayarAgent] Reconciling {len(expected_transactions)} transactions.")

        actual = await self.doku.get_transactions()
        expected_ids = {t["order_id"] for t in expected_transactions}
        actual_ids = {t["order_id"] for t in actual}

        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids

        failed = [t for t in actual if t.get("status") == "FAILED"]

        result = {
            "status": "ok",
            "total_expected": len(expected_transactions),
            "total_actual": len(actual),
            "missing_transactions": list(missing),
            "unexpected_transactions": list(extra),
            "failed_transactions": failed,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if failed:
            logger.warning(f"[BayarAgent] {len(failed)} failed transactions detected!")

        return result

    async def disburse(
        self, recipient_account: str, amount: int, notes: str = ""
    ) -> dict[str, Any]:
        """Auto-disburse funds to supplier."""
        logger.info(f"[BayarAgent] Disbursing Rp {amount:,} to {recipient_account}")
        return await self.doku.transfer(
            to_account=recipient_account,
            amount=amount,
            notes=notes or "Auto-disbursement by UMKM Autopilot",
        )

    async def detect_anomalies(self, transactions: list[dict]) -> list[dict]:
        """Flag transactions outside normal value range."""
        if not transactions:
            return []

        amounts = [t.get("amount", 0) for t in transactions]
        mean = sum(amounts) / len(amounts)
        std = (sum((a - mean) ** 2 for a in amounts) / len(amounts)) ** 0.5

        anomalies = []
        for txn in transactions:
            amt = txn.get("amount", 0)
            if std > 0 and abs(amt - mean) / std > 3.0:
                anomalies.append({**txn, "anomaly_reason": "value_outlier"})

        return anomalies
