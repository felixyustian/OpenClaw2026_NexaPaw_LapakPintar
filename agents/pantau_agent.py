"""
Pantau Agent — Real-time competitor price & trend monitor
Scrapes Tokopedia & Shopee for the target UMKM product category.
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from loguru import logger

from tools.scraper import MarketplaceScraper


@dataclass
class ProductSnapshot:
    platform: str
    product_name: str
    price: int
    seller: str
    rating: float
    sold_count: int
    scraped_at: datetime = field(default_factory=datetime.utcnow)


class PantauAgent:
    """Monitors competitor prices and trends across Tokopedia & Shopee."""

    name = "pantau_agent"

    def __init__(self, keywords: list[str], redis_client=None):
        self.keywords = keywords
        self.redis = redis_client
        self.scraper = MarketplaceScraper()

    async def run(self) -> dict[str, Any]:
        logger.info(f"[PantauAgent] Starting price monitoring for: {self.keywords}")
        results: list[ProductSnapshot] = []

        for keyword in self.keywords:
            tokopedia = await self.scraper.scrape_tokopedia(keyword)
            shopee = await self.scraper.scrape_shopee(keyword)
            results.extend(tokopedia + shopee)

        summary = self._summarize(results)
        await self._store(summary)
        logger.info(f"[PantauAgent] Scraped {len(results)} products.")
        return summary

    def _summarize(self, snapshots: list[ProductSnapshot]) -> dict[str, Any]:
        if not snapshots:
            return {"status": "no_data", "snapshots": []}

        prices = [s.price for s in snapshots]
        return {
            "status": "ok",
            "total_products": len(snapshots),
            "avg_price": sum(prices) // len(prices),
            "min_price": min(prices),
            "max_price": max(prices),
            "timestamp": datetime.utcnow().isoformat(),
            "snapshots": [vars(s) for s in snapshots],
        }

    async def _store(self, summary: dict[str, Any]) -> None:
        if self.redis:
            import json
            self.redis.set("pantau:latest", json.dumps(summary, default=str))
            logger.debug("[PantauAgent] Stored summary to Redis.")
