"""Summary endpoint — RAG retrieval → cache check → LLM stream."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.models import SummaryResponse
from app.services.llm import build_prompt, stream_completion
from app.services.retrieval import RetrievalService
from app.services.summary_db import SummaryDBService

router = APIRouter(prefix="/api/v1")


# ── Dependency factories ─────────────────────────────────────────────────────
def get_retrieval_service() -> RetrievalService:
    return RetrievalService()


def get_summary_db_service() -> SummaryDBService:
    return SummaryDBService()


# ── Route ─────────────────────────────────────────────────────────────────────
@router.get("/summary/{company_id}")
async def get_summary(
    company_id: str,
    retrieval: RetrievalService = Depends(get_retrieval_service),
    summary_db: SummaryDBService = Depends(get_summary_db_service),
):
    """Return a streamed or cached executive summary for *company_id*.

    Flow:
    1. Look up notes from the retrieval service.
    2. If no notes exist → 404.
    3. Compare the latest note date against the cached_at timestamp.
    4. If the cache is fresh → return the stored summary immediately.
    5. Otherwise → build a prompt, stream the LLM response, persist it.
    """

    # Step 1 – Retrieve matching notes
    notes = retrieval.search(company_id)
    if not notes:
        raise HTTPException(status_code=404, detail="No notes found for this ID.")

    # Step 2 – Determine the latest data point
    latest_date = retrieval.latest_record_date(company_id)

    # Step 3 – Check the cache
    cached_at = await summary_db.get_cached_at(company_id)

    if cached_at and latest_date and cached_at >= latest_date:
        # Cache hit — serve the stored summary directly
        stored = await summary_db.get_summary(company_id)
        return SummaryResponse(id=company_id, summary=stored, cached=True)  # type: ignore

    # Step 4 – Cache miss or stale — generate a new summary via LLM
    prompt = build_prompt(notes)

    # We accumulate the streamed tokens so we can persist the full text after
    # streaming completes.
    collected_chunks: list[str] = []

    async def _generate():
        async for token in stream_completion(prompt):
            collected_chunks.append(token)
            yield token

        # Step 5 – Persist the completed summary
        full_text = "".join(collected_chunks)
        await summary_db.save(company_id, full_text, latest_date)  # type: ignore

    return StreamingResponse(_generate(), media_type="text/event-stream")
