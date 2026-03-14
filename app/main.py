"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.summary import router as summary_router
from app.services.summary_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure SQLite tables exist
    await init_db()
    yield


app = FastAPI(
    title="RAG Summary Agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(summary_router)
