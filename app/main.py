"""
app/main.py — FastAPI backend for UMKM Autopilot dashboard & API.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from app.routes import agents_router, dashboard_router, health_router

load_dotenv()

app = FastAPI(
    title="UMKM Autopilot API",
    description="Autonomous Business Operating System untuk UMKM Indonesia",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(agents_router, prefix="/agents", tags=["Agents"])


@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse({
        "name": "UMKM Autopilot",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    })


@app.on_event("startup")
async def startup_event():
    logger.info("🚀 UMKM Autopilot API started.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("UMKM Autopilot API shutting down.")
