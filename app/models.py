from pydantic import BaseModel


class CompanyNote(BaseModel):
    """A single record from the retrieval database."""

    id: str
    company_name: str
    notes: str
    created_on: str  # ISO-8601
    updated_on: str  # ISO-8601


class CachedSummaryRef(BaseModel):
    """Lightweight cache entry — just enough to decide if the summary is stale."""

    id: str
    cached_at: str  # ISO-8601 — latest retrieval-record date when summary was built


class SummaryResponse(BaseModel):
    """Returned when the summary is already cached and served directly."""

    id: str
    summary: str
    cached: bool
