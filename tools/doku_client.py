"""
tools/doku_client.py — DOKU REST API v2 integration.
Docs: https://docs.doku.com
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from datetime import datetime
from typing import Any

import httpx
from loguru import logger


class DOKUClient:
    """Thin async client for DOKU REST API v2."""

    BASE_URL = "https://api.doku.com"
    SANDBOX_URL = "https://api-sandbox.doku.com"

    def __init__(self, client_id: str, secret_key: str, sandbox: bool = False):
        self.client_id = client_id
        self.secret_key = secret_key
        self.base_url = self.SANDBOX_URL if sandbox else self.BASE_URL

    def _sign(self, method: str, path: str, body: str, timestamp: str) -> str:
        """Generate HMAC-SHA256 signature per DOKU spec."""
        body_hash = hashlib.sha256(body.encode()).hexdigest() if body else ""
        string_to_sign = f"{method}:{path}:{self.client_id}:{timestamp}:{body_hash}"
        return hmac.new(
            self.secret_key.encode(), string_to_sign.encode(), hashlib.sha256
        ).hexdigest()

    def _headers(self, method: str, path: str, body: str = "") -> dict[str, str]:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        signature = self._sign(method, path, body, timestamp)
        return {
            "Client-Id": self.client_id,
            "Request-Id": str(int(time.time() * 1000)),
            "Request-Timestamp": timestamp,
            "Signature": f"HMACSHA256={signature}",
            "Content-Type": "application/json",
        }

    async def get_transactions(
        self, from_date: str = "", to_date: str = ""
    ) -> list[dict]:
        if not self.client_id:
            logger.warning("[DOKU] No credentials — returning mock transactions.")
            return self._mock_transactions()

        path = "/orders/v1/list"
        params = {}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}{path}",
                params=params,
                headers=self._headers("GET", path),
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json().get("data", [])

    async def transfer(
        self, to_account: str, amount: int, notes: str = ""
    ) -> dict[str, Any]:
        if not self.client_id:
            logger.warning("[DOKU] No credentials — mock transfer.")
            return {"status": "MOCK_SUCCESS", "amount": amount, "to": to_account}

        path = "/disbursement/v1/transfer"
        payload = json.dumps({
            "transfer": {"amount": amount, "currency": "IDR", "notes": notes},
            "beneficiary": {"bank_code": "BCA", "account_number": to_account},
        })

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}{path}",
                content=payload,
                headers=self._headers("POST", path, payload),
                timeout=15,
            )
            resp.raise_for_status()
            return resp.json()

    def _mock_transactions(self) -> list[dict]:
        import random
        statuses = ["SUCCESS", "SUCCESS", "SUCCESS", "FAILED", "PENDING"]
        return [
            {
                "order_id": f"TXN-{1000 + i}",
                "amount": random.randint(50_000, 2_000_000),
                "status": random.choice(statuses),
                "created_at": datetime.utcnow().isoformat(),
            }
            for i in range(10)
        ]
