"""
demo/run_demo.py — UMKM Autopilot demo mode (no real credentials needed).
Usage: python demo/run_demo.py --mock
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from loguru import logger

MOCK_SALES = [
    {"id": "S001", "product": "Batik Mega Mendung", "revenue": 1_500_000, "qty": 10},
    {"id": "S002", "product": "Batik Parang", "revenue": 2_200_000, "qty": 15},
    {"id": "S003", "product": "Batik Kawung", "revenue": 800_000, "qty": 6},
    {"id": "S004", "product": "Batik Truntum", "revenue": 9_500_000, "qty": 60},  # anomaly
    {"id": "S005", "product": "Batik Sidomukti", "revenue": 1_100_000, "qty": 8},
]


async def run_demo():
    logger.info("=" * 60)
    logger.info("  🤖 UMKM Autopilot — DEMO MODE")
    logger.info("=" * 60)

    # 1. Pantau Agent
    logger.info("\n📡 [1/5] PantauAgent — Marketplace Monitor")
    from agents.pantau_agent import PantauAgent
    pantau = PantauAgent(keywords=["batik", "tenun"])
    result = await pantau.run()
    logger.info(f"  → Scraped {result['total_products']} products")
    logger.info(f"  → Avg price: Rp {result['avg_price']:,}")

    # 2. Analitik Agent
    logger.info("\n📊 [2/5] AnalitikAgent — Sales Analytics")
    from tools.rag_db import RAGDatabase
    from agents.analitik_agent import AnalitikAgent
    rag = RAGDatabase()
    analitik = AnalitikAgent(rag_db=rag)
    analitik_result = await analitik.run(MOCK_SALES)
    logger.info(f"  → Anomalies detected: {len(analitik_result['anomalies'])}")
    for a in analitik_result["anomalies"]:
        logger.warning(f"    ⚠ Anomaly: {a['product']} (z={a.get('z_score', '?')})")

    # 3. Konten Agent
    logger.info("\n✍️  [3/5] KontenAgent — Content Generation")
    from agents.konten_agent import KontenAgent
    konten = KontenAgent()
    schedule = await konten.generate_promo_schedule("Batik Mega Mendung")
    logger.info(f"  → Generated {len(schedule)}-day promo schedule")
    for item in schedule[:2]:
        logger.info(f"    • {item['hari']} | {item['platform']}: {item['caption'][:50]}...")

    # 4. Bayar Agent
    logger.info("\n💳 [4/5] BayarAgent — Payment Reconciliation")
    from agents.bayar_agent import BayarAgent
    bayar = BayarAgent()
    recon = await bayar.reconcile(expected_transactions=[
        {"order_id": "TXN-1000"},
        {"order_id": "TXN-1001"},
    ])
    logger.info(f"  → Expected: {recon['total_expected']}, Actual: {recon['total_actual']}")
    logger.info(f"  → Failed transactions: {len(recon['failed_transactions'])}")

    # 5. Laporan Agent
    logger.info("\n📋 [5/5] LaporanAgent — Daily Report")
    from agents.laporan_agent import LaporanAgent
    laporan = LaporanAgent()
    report = await laporan.run()
    logger.info(f"  → Report date: {report['report_date']}")
    logger.info(f"\n{report['content']}")

    logger.info("\n" + "=" * 60)
    logger.info("  ✅ Demo complete! All 5 agents ran successfully.")
    logger.info("  🔧 Set credentials in .env to enable real data.")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    args = parser.parse_args()

    asyncio.run(run_demo())
