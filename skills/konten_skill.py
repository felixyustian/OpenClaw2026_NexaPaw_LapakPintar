"""skills/konten_skill.py — QwenPaw skill wrapper for KontenAgent."""
from agents.konten_agent import KontenAgent

async def konten_skill(product_name: str, category: str = "", price: int = 0, features: list = []) -> str:
    """Generate product description and promo schedule."""
    agent = KontenAgent()
    return await agent.generate_description(product_name, category, price, features)
