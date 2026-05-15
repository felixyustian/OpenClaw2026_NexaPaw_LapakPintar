"""
skills/pantau_skill.py — QwenPaw skill wrapper for PantauAgent.
Install with: qwenpaw install skills/pantau_skill.py
"""

from agents.pantau_agent import PantauAgent


async def pantau_skill(keywords: list[str]) -> dict:
    """
    Monitor competitor prices and trends on Tokopedia & Shopee.

    Args:
        keywords: List of product keywords to monitor.

    Returns:
        Summary dict with avg/min/max prices and product snapshots.
    """
    agent = PantauAgent(keywords=keywords)
    return await agent.run()
