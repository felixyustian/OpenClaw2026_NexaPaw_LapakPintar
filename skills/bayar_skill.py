"""skills/bayar_skill.py — QwenPaw skill wrapper for BayarAgent."""
from agents.bayar_agent import BayarAgent

async def bayar_skill(expected_transactions: list[dict]) -> dict:
    """Reconcile payments via DOKU API."""
    agent = BayarAgent()
    return await agent.reconcile(expected_transactions)
