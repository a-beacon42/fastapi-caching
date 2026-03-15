from pydantic import BaseModel
import uuid


class Summary(BaseModel):
    id: uuid.UUID
    company_id: str
    summary: str
    citations: str  # list of doc IDs
    prompt_version: str
    created_on: str


class SummaryRequest(BaseModel):
    prompt_version: str
    system_message: str
    user_message: str  # concatenated list of input docs


class SummaryResponse(BaseModel):
    summary: str
    prompt_version: str
