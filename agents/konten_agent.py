"""
Konten Agent — Auto-generate product descriptions & promotional content schedule.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from typing import Any

from loguru import logger


PROMO_SCHEDULE_TEMPLATE = """
Buatkan jadwal konten promosi untuk toko UMKM selama 7 hari ke depan.
Produk: {product_name}
Target audiens: pembeli Indonesia usia 20-45
Tone: friendly, lokal, menarik
Format output: JSON array dengan field [hari, platform, caption, hashtags]
Balas HANYA dengan JSON tanpa markdown.
"""

DESKRIPSI_TEMPLATE = """
Tulis deskripsi produk marketplace yang menarik untuk:
Nama: {product_name}
Kategori: {category}
Harga: Rp {price:,}
Fitur utama: {features}

Deskripsi harus SEO-friendly untuk Tokopedia/Shopee, 150-200 kata, bahasa Indonesia.
"""


class KontenAgent:
    """Generates product descriptions and promotional content schedules via Qwen3."""

    name = "konten_agent"

    def __init__(self, llm_client=None):
        self.llm = llm_client

    async def generate_description(
        self,
        product_name: str,
        category: str,
        price: int,
        features: list[str],
    ) -> str:
        if not self.llm:
            return f"[DEMO] Deskripsi otomatis untuk {product_name} — LLM tidak dikonfigurasi."

        prompt = DESKRIPSI_TEMPLATE.format(
            product_name=product_name,
            category=category,
            price=price,
            features=", ".join(features),
        )
        logger.info(f"[KontenAgent] Generating description for: {product_name}")
        return await self.llm.achat(prompt)

    async def generate_promo_schedule(self, product_name: str) -> list[dict]:
        if not self.llm:
            return self._mock_schedule(product_name)

        prompt = PROMO_SCHEDULE_TEMPLATE.format(product_name=product_name)
        logger.info(f"[KontenAgent] Generating promo schedule for: {product_name}")
        raw = await self.llm.achat(prompt)

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("[KontenAgent] Failed to parse JSON schedule.")
            return []

    def _mock_schedule(self, product_name: str) -> list[dict]:
        platforms = ["Instagram", "TikTok", "WhatsApp Story"]
        schedule = []
        for i in range(7):
            day = (datetime.today() + timedelta(days=i)).strftime("%A, %d %b")
            schedule.append({
                "hari": day,
                "platform": platforms[i % len(platforms)],
                "caption": f"✨ Promo hari ke-{i+1} untuk {product_name}! Jangan sampai kehabisan!",
                "hashtags": ["#UMKM", "#ProdukLokal", f"#{product_name.replace(' ', '')}"],
            })
        return schedule
