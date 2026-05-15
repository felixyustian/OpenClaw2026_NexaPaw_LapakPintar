"""skills/laporan_skill.py — QwenPaw skill wrapper for LaporanAgent."""
from agents.laporan_agent import LaporanAgent

async def laporan_skill() -> dict:
    """Generate and store the daily business report."""
    agent = LaporanAgent()
    return await agent.run()
