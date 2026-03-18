from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import StreamingResponse
from uuid import uuid4
from datetime import datetime, timezone
import json
from app.config import get_settings
from app.prompts.summary import PROMPT_VERSION
from app.services.db import DbService
from app.services.llm import LLMService
from app.models.summary_models import Summary

router = APIRouter()


def get_db_service():
    return DbService(get_settings())


def get_llm_service():
    return LLMService(get_settings())


@router.get("/summary/{company_id}")
async def invoke_pipeline(
    company_id: str,
    stream: bool = False,
    db: DbService = Depends(get_db_service),
    llm_svc: LLMService = Depends(get_llm_service),
):
    notes = await db.get_notes_by_company(company_id)
    if not notes:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail=f"No notes found for {company_id}"
        )

    citation_ids = [str(note.id) for note in notes]

    summary = await db.get_summary_by_company(company_id)
    latest_note_date = await db.get_latest_note_date(company_id)

    if summary and latest_note_date and summary.created_on >= latest_note_date:
        return summary

    if stream:
        collected: list[str] = []

        async def _generate():
            async for token in llm_svc.generate_summary_stream(notes):
                collected.append(token)
                yield token

            full_text = "".join(collected)
            streamed_summary = Summary(
                id=uuid4(),
                company_id=notes[0].company_id,
                summary=full_text,
                citations=json.dumps(citation_ids),
                prompt_version=PROMPT_VERSION,
                created_on=datetime.now(tz=timezone.utc).isoformat(),
            )
            await db.save_summary(streamed_summary)

        return StreamingResponse(_generate(), media_type="text/event-stream")

    else:
        try:
            llm_response = await llm_svc.generate_summary(notes)
        except Exception as e:
            raise HTTPException(status.HTTP_502_BAD_GATEWAY, detail=str(e))

    new_summary = Summary(
        id=uuid4(),
        company_id=notes[0].company_id,
        summary=llm_response.summary,
        citations=json.dumps(citation_ids),
        prompt_version=llm_response.prompt_version,
        created_on=datetime.now(timezone.utc).isoformat(),
    )
    await db.save_summary(new_summary)
    return new_summary
