from fastapi import FastAPI

from app.routers import summary

app = FastAPI(title="RAG summarizer", version="0.1.0")
app.include_router(summary.router, prefix="/api/v1", tags=["summary"])
