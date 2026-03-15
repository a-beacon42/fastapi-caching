[x] app/config.py — Settings class (DB path, Azure OpenAI endpoint/key. Use pydantic-settings so everything comes from env vars.

[x] app/models.py — Pydantic models matching the DB schema. Note, Summary, and whatever you want the API to return.

[x] app/services/db.py — Async DB layer. Two key queries: (a) get notes by company_id, (b) get/upsert summaries. This is the cache check logic.

[x] app/services/llm.py — Azure OpenAI wrapper. generate_summary(docs, stream=False) → calls chat completions, returns the summary text.

[x] app/routers/summary.py — The endpoint. Wire together DB queries + staleness check + LLM call + save. This is the core agent flow.

[x] app/main.py — FastAPI app, lifespan, router includes.

[ ] Tests — Hit each branch: fresh, stale, no summary, unknown company.
