"""skills/analitik_skill.py — QwenPaw skill wrapper for AnalitikAgent."""
from agents.analitik_agent import AnalitikAgent
from tools.rag_db import RAGDatabase

async def analitik_skill(sales_data: list[dict]) -> dict:
    """Analyse sales patterns and predict demand."""
    agent = AnalitikAgent(rag_db=RAGDatabase())
    return await agent.run(sales_data)
