from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class PantauRequest(BaseModel):
    keywords: list[str]


class KontenRequest(BaseModel):
    product_name: str
    category: str = "Umum"
    price: int = 100000
    features: list[str] = []


@router.post("/pantau/run")
async def run_pantau(req: PantauRequest):
    """Trigger a Pantau Agent scrape manually."""
    from tools.scraper import MarketplaceScraper
    scraper = MarketplaceScraper()
    results = []
    for kw in req.keywords[:3]:  # Limit to 3 keywords per manual call
        results.extend(await scraper.scrape_tokopedia(kw))
    return {"status": "ok", "results_count": len(results)}


@router.post("/konten/description")
async def generate_description(req: KontenRequest):
    """Generate product description via Konten Agent."""
    from agents.konten_agent import KontenAgent
    agent = KontenAgent()
    desc = await agent.generate_description(
        product_name=req.product_name,
        category=req.category,
        price=req.price,
        features=req.features,
    )
    return {"description": desc}


@router.post("/konten/schedule")
async def generate_schedule(req: KontenRequest):
    """Generate promo content schedule."""
    from agents.konten_agent import KontenAgent
    agent = KontenAgent()
    schedule = await agent.generate_promo_schedule(req.product_name)
    return {"schedule": schedule}
