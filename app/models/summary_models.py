from pydantic import BaseModel
import uuid

from app.models.note_models import Note


class Summary(BaseModel):
    id: uuid.UUID
    company_id: str
    summary: str
    citations: str
    prompt_version: str
    created_on: str


# internal call
# agent.retrieve_docs(id) -> agent.generate_summary(docs) -> SummaryResponse
class SummaryRequest(BaseModel):
    source_docs: list[Note]


class SummaryResponse(BaseModel):
    company_id: str
    citations: list[str]
    summary: str
    created_on: str
    cached: bool
