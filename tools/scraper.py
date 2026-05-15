"""
tools/scraper.py — Playwright-based marketplace scraper (Tokopedia & Shopee).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

from loguru import logger

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


@dataclass
class ProductSnapshot:
    platform: str
    product_name: str
    price: int
    seller: str
    rating: float
    sold_count: int


class MarketplaceScraper:
    """Scrapes product listings from Indonesian marketplaces."""

    async def scrape_tokopedia(self, keyword: str) -> list[ProductSnapshot]:
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not installed — returning mock data.")
            return self._mock_data("Tokopedia", keyword)

        results: list[ProductSnapshot] = []
        url = f"https://www.tokopedia.com/search?q={keyword.replace(' ', '+')}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(url, timeout=30_000)
                await page.wait_for_load_state("networkidle", timeout=15_000)

                cards = await page.query_selector_all("[data-testid='master-product-card']")
                for card in cards[:10]:
                    try:
                        name_el = await card.query_selector("[data-testid='linkProductName']")
                        price_el = await card.query_selector("[data-testid='linkProductPrice']")
                        if name_el and price_el:
                            name = await name_el.inner_text()
                            price_raw = await price_el.inner_text()
                            price = int("".join(filter(str.isdigit, price_raw)) or "0")
                            results.append(
                                ProductSnapshot(
                                    platform="Tokopedia",
                                    product_name=name.strip(),
                                    price=price,
                                    seller="",
                                    rating=0.0,
                                    sold_count=0,
                                )
                            )
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"[Scraper] Tokopedia scrape failed: {e}")
            finally:
                await browser.close()

        return results or self._mock_data("Tokopedia", keyword)

    async def scrape_shopee(self, keyword: str) -> list[ProductSnapshot]:
        # Shopee uses heavy JS — return mock until headless bypass implemented
        logger.info(f"[Scraper] Shopee scrape for: {keyword} (mock mode)")
        return self._mock_data("Shopee", keyword)

    def _mock_data(self, platform: str, keyword: str) -> list[ProductSnapshot]:
        import random
        return [
            ProductSnapshot(
                platform=platform,
                product_name=f"{keyword.title()} Produk {i+1}",
                price=random.randint(50_000, 500_000),
                seller=f"Toko{random.randint(1, 999)}",
                rating=round(random.uniform(4.0, 5.0), 1),
                sold_count=random.randint(10, 1000),
            )
            for i in range(5)
        ]
