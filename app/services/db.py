import aiosqlite

from app.config import Settings
from app.models.note_models import Note
from app.models.summary_models import Summary


def _map_db_row_to_Note(row: aiosqlite.Row) -> Note:
    return Note(
        id=row["id"],
        company_id=row["company_id"],
        company_name=row["company_name"],
        notes=row["notes"],
        created_on=row["created_on"],
        updated_on=row["updated_on"],
    )


def _map_db_row_to_Summary(row: aiosqlite.Row) -> Summary:
    return Summary(
        id=row["id"],
        company_id=row["company_id"],
        summary=row["summary"],
        citations=row["citations"],
        prompt_version=row["prompt_version"],
        created_on=row["created_on"],
    )


class DbService:
    def __init__(self, settings: Settings):
        self.db_path = settings.db_path

    async def get_notes_by_company(self, company_id: str) -> list[Note] | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            q = "SELECT * FROM notes WHERE company_id = ?"
            async with db.execute(q, (company_id,)) as cursor:
                db_results = await cursor.fetchall()
                notes: list[Note] = [_map_db_row_to_Note(row) for row in db_results]
        return notes if notes else None

    async def get_summary_by_company(self, company_id: str) -> Summary | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            q = "SELECT * FROM summaries WHERE company_id = ? ORDER BY created_on DESC"
            async with db.execute(q, (company_id,)) as cursor:
                db_result = await cursor.fetchone()
                return _map_db_row_to_Summary(db_result) if db_result else None

    async def get_latest_note_date(self, company_id: str) -> str | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            q = "SELECT updated_on FROM notes WHERE company_id = ? ORDER BY updated_on DESC LIMIT 1"
            async with db.execute(q, (company_id,)) as cursor:
                db_result = await cursor.fetchone()
                return db_result["updated_on"] if db_result else None

    async def save_summary(self, summary: Summary) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT INTO summaries (id, company_id, summary, citations, prompt_version, created_on)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id) DO UPDATE SET
                    summary = excluded.summary,
                    citations = excluded.citations,
                    prompt_version = excluded.prompt_version,
                    created_on = excluded.created_on
                """,
                (
                    str(summary.id),
                    summary.company_id,
                    summary.summary,
                    summary.citations,
                    summary.prompt_version,
                    summary.created_on,
                ),
            )
            await db.commit()
