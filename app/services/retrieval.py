"""Mock retrieval service — simulates a document / notes database."""

from app.models import CompanyNote

# ── Mock data ────────────────────────────────────────────────────────────────
# Each company_id can have multiple notes (like a CRM activity log).
_MOCK_NOTES: list[dict] = [
    # ── Acme Corp (acme-001) ─────────────────────────────────────────────────
    {
        "id": "acme-001",
        "company_name": "Acme Corp",
        "notes": "Q3 revenue grew 12% YoY driven by expansion in EMEA markets.",
        "created_on": "2025-07-15T10:00:00Z",
        "updated_on": "2025-07-15T10:00:00Z",
    },
    {
        "id": "acme-001",
        "company_name": "Acme Corp",
        "notes": "New CFO appointed — previously VP Finance at GlobalTech.",
        "created_on": "2025-09-01T08:30:00Z",
        "updated_on": "2025-09-01T08:30:00Z",
    },
    {
        "id": "acme-001",
        "company_name": "Acme Corp",
        "notes": "Signed a 3-year cloud infrastructure deal with Azure worth $4.2M.",
        "created_on": "2025-11-20T14:15:00Z",
        "updated_on": "2025-11-20T14:15:00Z",
    },
    # ── Globex Inc (globex-002) ──────────────────────────────────────────────
    {
        "id": "globex-002",
        "company_name": "Globex Inc",
        "notes": "Product recall in Q2 led to a 5% dip in customer satisfaction scores.",
        "created_on": "2025-06-10T09:00:00Z",
        "updated_on": "2025-06-10T09:00:00Z",
    },
    {
        "id": "globex-002",
        "company_name": "Globex Inc",
        "notes": "Launched 'Globex Green' sustainability initiative — targeting net-zero by 2030.",
        "created_on": "2025-08-22T11:45:00Z",
        "updated_on": "2025-08-22T11:45:00Z",
    },
    # ── Initech (initech-003) ────────────────────────────────────────────────
    {
        "id": "initech-003",
        "company_name": "Initech",
        "notes": "Migrating legacy ERP to SAP S/4HANA — expected go-live in Q1 2026.",
        "created_on": "2025-10-05T16:00:00Z",
        "updated_on": "2025-10-05T16:00:00Z",
    },
]


class RetrievalService:
    """Looks up company notes by ID. In production this would query a vector DB
    or search index; here we just filter an in-memory list."""

    def search(self, company_id: str) -> list[CompanyNote]:
        return [CompanyNote(**note) for note in _MOCK_NOTES if note["id"] == company_id]

    def latest_record_date(self, company_id: str) -> str | None:
        """Return the most recent created_on for a given ID, or None."""
        dates = [note["created_on"] for note in _MOCK_NOTES if note["id"] == company_id]
        return max(dates) if dates else None
