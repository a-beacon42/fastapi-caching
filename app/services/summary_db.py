"""SQLite-backed service for persisting AI-generated summaries and cache refs."""

import aiosqlite

DB_PATH = "summaries.db"


async def init_db() -> None:
    """Create tables if they don't exist yet."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS cache_refs (
                id         TEXT PRIMARY KEY,
                cached_at  TEXT NOT NULL       -- latest retrieval created_on when summary was built
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS summaries (
                id       TEXT PRIMARY KEY,
                content  TEXT NOT NULL
            )
            """
        )
        await db.commit()


class SummaryDBService:
    """Async interface to the summaries SQLite database."""

    async def get_cached_at(self, company_id: str) -> str | None:
        """Return the cached_at timestamp for *company_id*, or None."""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT cached_at FROM cache_refs WHERE id = ?",
                (company_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row else None

    async def get_summary(self, company_id: str) -> str | None:
        """Return the stored summary text, or None."""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT content FROM summaries WHERE id = ?",
                (company_id,),
            )
            row = await cursor.fetchone()
            return row[0] if row else None

    async def save(self, company_id: str, content: str, cached_at: str) -> None:
        """Upsert both the summary content and the cache reference."""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO cache_refs (id, cached_at) VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET cached_at = excluded.cached_at
                """,
                (company_id, cached_at),
            )
            await db.execute(
                """
                INSERT INTO summaries (id, content) VALUES (?, ?)
                ON CONFLICT(id) DO UPDATE SET content = excluded.content
                """,
                (company_id, content),
            )
            await db.commit()
