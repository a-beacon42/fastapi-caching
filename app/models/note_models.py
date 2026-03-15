from pydantic import BaseModel
import uuid


class Note(BaseModel):
    id: uuid.UUID
    company_id: str
    company_name: str
    notes: str
    created_on: str
    updated_on: str
