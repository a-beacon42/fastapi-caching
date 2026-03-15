"""Database seed script — creates tables and inserts mock data.

Usage:
    python -m db.seed            # creates db/notes.db
    python -m db.seed --reset    # drops existing tables first
"""

import argparse
import json
import sqlite3
import uuid
from pathlib import Path

DB_PATH = Path(__file__).parent / "notes.db"

# ── Schema ────────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id           TEXT PRIMARY KEY,
    company_id   TEXT NOT NULL,
    company_name TEXT NOT NULL,
    notes        TEXT NOT NULL,
    created_on   TEXT NOT NULL,
    updated_on   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS summaries (
    id              TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL,
    summary         TEXT NOT NULL,
    citations       TEXT NOT NULL,   -- JSON array of note IDs
    created_on      TEXT NOT NULL,
    prompt_version  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_notes_company ON notes(company_id);
CREATE INDEX IF NOT EXISTS idx_summaries_company ON summaries(company_id);
"""

# ── Company definitions ───────────────────────────────────────────────────────

COMPANIES = [
    ("acme-001", "Acme Corp"),
    ("globex-002", "Globex Industries"),
    ("initech-003", "Initech Solutions"),
    ("umbrella-004", "Umbrella Health"),
    ("stark-005", "Stark Manufacturing"),
    ("wayne-006", "Wayne Logistics"),
    ("oscorp-007", "Oscorp Dynamics"),
    ("cyberdyne-008", "Cyberdyne Analytics"),
]

# ── Notes (100 total) ────────────────────────────────────────────────────────
# Each tuple: (company_id, notes_text, created_on, updated_on)

_NOTES_RAW: list[tuple[str, str, str, str]] = [
    # ── Acme Corp: 18 notes ──────────────────────────────────────────────────
    (
        "acme-001",
        "Q1 revenue came in at $12.3M, up 8% from prior quarter.",
        "2025-01-15T09:00:00Z",
        "2025-01-15T09:00:00Z",
    ),
    (
        "acme-001",
        "Opened new regional office in Frankfurt to support EMEA growth.",
        "2025-02-03T10:30:00Z",
        "2025-02-03T10:30:00Z",
    ),
    (
        "acme-001",
        "Customer churn rate fell to 3.1% — lowest in company history.",
        "2025-02-20T14:00:00Z",
        "2025-02-20T14:00:00Z",
    ),
    (
        "acme-001",
        "Board approved $5M R&D budget increase for AI initiatives.",
        "2025-03-08T11:15:00Z",
        "2025-03-08T11:15:00Z",
    ),
    (
        "acme-001",
        "Hired VP of Engineering from Microsoft Azure team.",
        "2025-03-25T08:45:00Z",
        "2025-03-25T08:45:00Z",
    ),
    (
        "acme-001",
        "Launched Acme Pro tier — premium SaaS offering with 99.99% SLA.",
        "2025-04-10T16:00:00Z",
        "2025-04-10T16:00:00Z",
    ),
    (
        "acme-001",
        "Q2 pipeline value reached $28M across 140 qualified opportunities.",
        "2025-04-28T09:30:00Z",
        "2025-04-28T09:30:00Z",
    ),
    (
        "acme-001",
        "Completed SOC 2 Type II audit with zero findings.",
        "2025-05-12T13:00:00Z",
        "2025-05-12T13:00:00Z",
    ),
    (
        "acme-001",
        "Strategic partnership signed with Salesforce for CRM integration.",
        "2025-06-01T10:00:00Z",
        "2025-06-01T10:00:00Z",
    ),
    (
        "acme-001",
        "Q3 revenue grew 12% YoY driven by expansion in EMEA markets.",
        "2025-07-15T10:00:00Z",
        "2025-07-15T10:00:00Z",
    ),
    (
        "acme-001",
        "Net promoter score improved to 72, up from 65 last quarter.",
        "2025-07-30T11:00:00Z",
        "2025-07-30T11:00:00Z",
    ),
    (
        "acme-001",
        "New CFO appointed — previously VP Finance at GlobalTech.",
        "2025-09-01T08:30:00Z",
        "2025-09-01T08:30:00Z",
    ),
    (
        "acme-001",
        "Migrated 80% of workloads to Azure — targeting 100% by Q1 2026.",
        "2025-09-18T15:30:00Z",
        "2025-09-18T15:30:00Z",
    ),
    (
        "acme-001",
        "Employee headcount crossed 500 — up 40% YoY.",
        "2025-10-05T09:00:00Z",
        "2025-10-05T09:00:00Z",
    ),
    (
        "acme-001",
        "Signed a 3-year cloud infrastructure deal with Azure worth $4.2M.",
        "2025-11-20T14:15:00Z",
        "2025-11-20T14:15:00Z",
    ),
    (
        "acme-001",
        "Annual customer conference drew 2,000 attendees — 3x prior year.",
        "2025-11-30T10:00:00Z",
        "2025-11-30T10:00:00Z",
    ),
    (
        "acme-001",
        "Closed fiscal year at $52M ARR, beating guidance by 6%.",
        "2025-12-15T16:00:00Z",
        "2025-12-15T16:00:00Z",
    ),
    (
        "acme-001",
        "Published 2026 strategic plan focused on AI-first product roadmap.",
        "2026-01-10T09:00:00Z",
        "2026-01-10T09:00:00Z",
    ),
    # ── Globex Industries: 15 notes ──────────────────────────────────────────
    (
        "globex-002",
        "Q1 shipment volumes up 5% despite supply chain disruptions.",
        "2025-01-20T08:00:00Z",
        "2025-01-20T08:00:00Z",
    ),
    (
        "globex-002",
        "Opened a second distribution center in Memphis, TN.",
        "2025-02-14T12:00:00Z",
        "2025-02-14T12:00:00Z",
    ),
    (
        "globex-002",
        "Key supplier Tanaka Steel renewed contract at favorable terms.",
        "2025-03-05T10:00:00Z",
        "2025-03-05T10:00:00Z",
    ),
    (
        "globex-002",
        "Product recall in Q2 led to a 5% dip in customer satisfaction.",
        "2025-06-10T09:00:00Z",
        "2025-06-10T09:00:00Z",
    ),
    (
        "globex-002",
        "Hired new Head of Quality from automotive industry.",
        "2025-06-25T14:30:00Z",
        "2025-06-25T14:30:00Z",
    ),
    (
        "globex-002",
        "Implemented real-time inventory tracking across all warehouses.",
        "2025-07-08T11:00:00Z",
        "2025-07-08T11:00:00Z",
    ),
    (
        "globex-002",
        "Launched Globex Green sustainability initiative — net-zero by 2030.",
        "2025-08-22T11:45:00Z",
        "2025-08-22T11:45:00Z",
    ),
    (
        "globex-002",
        "Q3 gross margin improved to 34% from 31% after recall costs absorbed.",
        "2025-09-15T09:00:00Z",
        "2025-09-15T09:00:00Z",
    ),
    (
        "globex-002",
        "Expanded into Latin American market with Brazil office.",
        "2025-10-01T10:00:00Z",
        "2025-10-01T10:00:00Z",
    ),
    (
        "globex-002",
        "Won 'Best Logistics Partner' award from National Retail Federation.",
        "2025-10-20T08:30:00Z",
        "2025-10-20T08:30:00Z",
    ),
    (
        "globex-002",
        "Signed $8M multi-year contract with HomeDepot for B2B fulfillment.",
        "2025-11-05T15:00:00Z",
        "2025-11-05T15:00:00Z",
    ),
    (
        "globex-002",
        "Annual revenue reached $180M — 11% growth YoY.",
        "2025-12-10T09:00:00Z",
        "2025-12-10T09:00:00Z",
    ),
    # --- These 3 notes are AFTER the summary's created_on (makes globex stale) ---
    (
        "globex-002",
        "New VP of Operations started — bringing Toyota Production System expertise.",
        "2026-02-01T09:00:00Z",
        "2026-02-01T09:00:00Z",
    ),
    (
        "globex-002",
        "Pilot program for drone-based warehouse inventory counts launched.",
        "2026-02-18T14:00:00Z",
        "2026-02-18T14:00:00Z",
    ),
    (
        "globex-002",
        "Q1 2026 bookings up 22% — strongest quarter in company history.",
        "2026-03-10T10:00:00Z",
        "2026-03-10T10:00:00Z",
    ),
    # ── Initech Solutions: 14 notes ──────────────────────────────────────────
    (
        "initech-003",
        "Kicked off SAP S/4HANA migration project — 18-month timeline.",
        "2025-01-08T09:00:00Z",
        "2025-01-08T09:00:00Z",
    ),
    (
        "initech-003",
        "Hired 12 SAP consultants to support migration.",
        "2025-02-15T10:00:00Z",
        "2025-02-15T10:00:00Z",
    ),
    (
        "initech-003",
        "Data cleansing phase completed — 2.1M records validated.",
        "2025-03-20T11:30:00Z",
        "2025-03-20T11:30:00Z",
    ),
    (
        "initech-003",
        "Legacy ERP downtime reduced to 4 hours/month during transition.",
        "2025-04-12T14:00:00Z",
        "2025-04-12T14:00:00Z",
    ),
    (
        "initech-003",
        "Finance module go-live successful — AP/AR fully migrated.",
        "2025-05-28T09:00:00Z",
        "2025-05-28T09:00:00Z",
    ),
    (
        "initech-003",
        "Mid-year review: migration 45% complete, on budget.",
        "2025-06-30T16:00:00Z",
        "2025-06-30T16:00:00Z",
    ),
    (
        "initech-003",
        "Procurement module testing revealed 23 integration defects — all P2/P3.",
        "2025-07-18T10:30:00Z",
        "2025-07-18T10:30:00Z",
    ),
    (
        "initech-003",
        "Resolved all integration defects — procurement go-live on track.",
        "2025-08-10T09:00:00Z",
        "2025-08-10T09:00:00Z",
    ),
    (
        "initech-003",
        "Employee training program launched — 500 users across 3 regions.",
        "2025-09-05T11:00:00Z",
        "2025-09-05T11:00:00Z",
    ),
    (
        "initech-003",
        "Manufacturing module entered UAT phase.",
        "2025-10-05T16:00:00Z",
        "2025-10-05T16:00:00Z",
    ),
    (
        "initech-003",
        "UAT completed with 96% test pass rate — 4% deferred to post-go-live.",
        "2025-11-01T09:00:00Z",
        "2025-11-01T09:00:00Z",
    ),
    (
        "initech-003",
        "Full go-live achieved on schedule — all modules operational.",
        "2025-12-01T08:00:00Z",
        "2025-12-01T08:00:00Z",
    ),
    (
        "initech-003",
        "Post-go-live defect rate at 0.3% — well below 2% threshold.",
        "2025-12-20T14:00:00Z",
        "2025-12-20T14:00:00Z",
    ),
    (
        "initech-003",
        "CIO presented migration success at industry conference — cited 30% efficiency gain.",
        "2026-01-15T10:00:00Z",
        "2026-01-15T10:00:00Z",
    ),
    # ── Umbrella Health: 13 notes ────────────────────────────────────────────
    (
        "umbrella-004",
        "Received FDA clearance for new portable diagnostic device.",
        "2025-01-22T09:00:00Z",
        "2025-01-22T09:00:00Z",
    ),
    (
        "umbrella-004",
        "Series C funding round closed at $45M — led by Sequoia.",
        "2025-02-10T11:00:00Z",
        "2025-02-10T11:00:00Z",
    ),
    (
        "umbrella-004",
        "Clinical trial for rapid COVID/flu combo test enrolled 1,200 patients.",
        "2025-03-18T10:00:00Z",
        "2025-03-18T10:00:00Z",
    ),
    (
        "umbrella-004",
        "Hired Chief Medical Officer from Johns Hopkins.",
        "2025-04-05T09:30:00Z",
        "2025-04-05T09:30:00Z",
    ),
    (
        "umbrella-004",
        "Launched telemedicine integration — devices now stream to provider dashboards.",
        "2025-05-14T14:00:00Z",
        "2025-05-14T14:00:00Z",
    ),
    (
        "umbrella-004",
        "Q2 device sales reached 15,000 units — 3x Q1.",
        "2025-07-01T10:00:00Z",
        "2025-07-01T10:00:00Z",
    ),
    (
        "umbrella-004",
        "Partnership with CVS Health for in-store diagnostic kiosks.",
        "2025-08-12T08:45:00Z",
        "2025-08-12T08:45:00Z",
    ),
    (
        "umbrella-004",
        "ISO 13485 certification renewed with zero non-conformances.",
        "2025-09-20T09:00:00Z",
        "2025-09-20T09:00:00Z",
    ),
    (
        "umbrella-004",
        "Annual revenue forecast raised to $38M from $30M.",
        "2025-10-15T16:00:00Z",
        "2025-10-15T16:00:00Z",
    ),
    (
        "umbrella-004",
        "Submitted 510(k) application for next-gen respiratory panel.",
        "2025-11-08T10:00:00Z",
        "2025-11-08T10:00:00Z",
    ),
    # --- These 3 notes are AFTER the summary's created_on (makes umbrella stale) ---
    (
        "umbrella-004",
        "Received breakthrough device designation from FDA for cardiac monitor.",
        "2026-01-25T09:00:00Z",
        "2026-01-25T09:00:00Z",
    ),
    (
        "umbrella-004",
        "Expanded manufacturing capacity — new cleanroom facility in San Diego.",
        "2026-02-14T11:00:00Z",
        "2026-02-14T11:00:00Z",
    ),
    (
        "umbrella-004",
        "Q1 2026 pipeline includes $22M in pending hospital contracts.",
        "2026-03-05T10:00:00Z",
        "2026-03-05T10:00:00Z",
    ),
    # ── Stark Manufacturing: 12 notes ────────────────────────────────────────
    (
        "stark-005",
        "Retooled production line A for electric vehicle components.",
        "2025-01-10T08:00:00Z",
        "2025-01-10T08:00:00Z",
    ),
    (
        "stark-005",
        "Landed first EV contract with Rivian — $6M over 2 years.",
        "2025-02-22T14:00:00Z",
        "2025-02-22T14:00:00Z",
    ),
    (
        "stark-005",
        "Installed robotic welding cells — throughput up 25%.",
        "2025-03-15T10:00:00Z",
        "2025-03-15T10:00:00Z",
    ),
    (
        "stark-005",
        "Workforce training program for CNC operators graduated first cohort.",
        "2025-04-20T09:00:00Z",
        "2025-04-20T09:00:00Z",
    ),
    (
        "stark-005",
        "Quality defect rate fell to 0.8% — industry average is 2.3%.",
        "2025-05-30T11:00:00Z",
        "2025-05-30T11:00:00Z",
    ),
    (
        "stark-005",
        "Won supplier excellence award from Tesla.",
        "2025-07-10T15:00:00Z",
        "2025-07-10T15:00:00Z",
    ),
    (
        "stark-005",
        "Expanded facility by 40,000 sq ft to accommodate new contracts.",
        "2025-08-18T08:30:00Z",
        "2025-08-18T08:30:00Z",
    ),
    (
        "stark-005",
        "Implemented predictive maintenance — unplanned downtime cut by 60%.",
        "2025-09-25T10:00:00Z",
        "2025-09-25T10:00:00Z",
    ),
    (
        "stark-005",
        "Q3 revenue hit $22M — best quarter in 5 years.",
        "2025-10-12T16:00:00Z",
        "2025-10-12T16:00:00Z",
    ),
    (
        "stark-005",
        "Exploring aerospace components as new vertical.",
        "2025-11-15T09:00:00Z",
        "2025-11-15T09:00:00Z",
    ),
    (
        "stark-005",
        "Passed AS9100 aerospace quality audit on first attempt.",
        "2025-12-08T14:00:00Z",
        "2025-12-08T14:00:00Z",
    ),
    (
        "stark-005",
        "Signed LOI with Boeing for landing gear sub-assemblies.",
        "2026-01-20T10:00:00Z",
        "2026-01-20T10:00:00Z",
    ),
    # ── Wayne Logistics: 11 notes ────────────────────────────────────────────
    (
        "wayne-006",
        "Fleet expanded to 1,200 trucks — largest in the Midwest.",
        "2025-01-28T09:00:00Z",
        "2025-01-28T09:00:00Z",
    ),
    (
        "wayne-006",
        "Implemented route optimization AI — fuel costs down 14%.",
        "2025-03-10T11:00:00Z",
        "2025-03-10T11:00:00Z",
    ),
    (
        "wayne-006",
        "Opened cross-dock facility in Indianapolis.",
        "2025-04-15T10:00:00Z",
        "2025-04-15T10:00:00Z",
    ),
    (
        "wayne-006",
        "Driver retention program reduced turnover from 45% to 28%.",
        "2025-05-22T14:00:00Z",
        "2025-05-22T14:00:00Z",
    ),
    (
        "wayne-006",
        "Won dedicated fleet contract with Whole Foods — 3 year term.",
        "2025-06-18T09:30:00Z",
        "2025-06-18T09:30:00Z",
    ),
    (
        "wayne-006",
        "Deployed ELD-compliant telematics across entire fleet.",
        "2025-07-25T08:00:00Z",
        "2025-07-25T08:00:00Z",
    ),
    (
        "wayne-006",
        "Q3 on-time delivery rate reached 98.2% — company record.",
        "2025-09-10T10:00:00Z",
        "2025-09-10T10:00:00Z",
    ),
    (
        "wayne-006",
        "Piloting electric trucks on short-haul routes in Ohio.",
        "2025-10-08T11:30:00Z",
        "2025-10-08T11:30:00Z",
    ),
    (
        "wayne-006",
        "Insurance costs reduced 18% after safety record improvements.",
        "2025-11-12T09:00:00Z",
        "2025-11-12T09:00:00Z",
    ),
    (
        "wayne-006",
        "Annual revenue crossed $200M for the first time.",
        "2025-12-20T16:00:00Z",
        "2025-12-20T16:00:00Z",
    ),
    (
        "wayne-006",
        "Exploring last-mile delivery partnerships with Amazon.",
        "2026-01-30T10:00:00Z",
        "2026-01-30T10:00:00Z",
    ),
    # ── Oscorp Dynamics: 10 notes ────────────────────────────────────────────
    (
        "oscorp-007",
        "Filed 8 new patents in advanced materials science.",
        "2025-02-05T09:00:00Z",
        "2025-02-05T09:00:00Z",
    ),
    (
        "oscorp-007",
        "Government R&D grant of $3.2M awarded for nano-coating research.",
        "2025-03-12T11:00:00Z",
        "2025-03-12T11:00:00Z",
    ),
    (
        "oscorp-007",
        "Lab partnership with MIT established for polymer research.",
        "2025-04-22T10:00:00Z",
        "2025-04-22T10:00:00Z",
    ),
    (
        "oscorp-007",
        "Prototype self-healing polymer passed 10,000-cycle stress test.",
        "2025-06-08T14:00:00Z",
        "2025-06-08T14:00:00Z",
    ),
    (
        "oscorp-007",
        "Presented findings at Materials Science World Congress in Berlin.",
        "2025-07-20T09:00:00Z",
        "2025-07-20T09:00:00Z",
    ),
    (
        "oscorp-007",
        "Licensed nano-coating tech to 3M for industrial applications.",
        "2025-09-01T10:30:00Z",
        "2025-09-01T10:30:00Z",
    ),
    (
        "oscorp-007",
        "Revenue from licensing hit $5M — first meaningful commercial income.",
        "2025-10-10T16:00:00Z",
        "2025-10-10T16:00:00Z",
    ),
    (
        "oscorp-007",
        "Hired 6 PhD researchers to expand bio-materials team.",
        "2025-11-18T08:00:00Z",
        "2025-11-18T08:00:00Z",
    ),
    (
        "oscorp-007",
        "Series B funding round raised $28M at $120M valuation.",
        "2025-12-05T11:00:00Z",
        "2025-12-05T11:00:00Z",
    ),
    (
        "oscorp-007",
        "Entered DOD supplier pipeline for advanced armor materials.",
        "2026-01-12T09:00:00Z",
        "2026-01-12T09:00:00Z",
    ),
    # ── Cyberdyne Analytics: 7 notes ─────────────────────────────────────────
    (
        "cyberdyne-008",
        "Founded in January 2025 by former Google DeepMind researchers.",
        "2025-01-05T08:00:00Z",
        "2025-01-05T08:00:00Z",
    ),
    (
        "cyberdyne-008",
        "Seed round of $2.5M closed — backed by Y Combinator.",
        "2025-03-01T10:00:00Z",
        "2025-03-01T10:00:00Z",
    ),
    (
        "cyberdyne-008",
        "Beta launch of predictive analytics platform — 50 early adopters.",
        "2025-05-15T09:00:00Z",
        "2025-05-15T09:00:00Z",
    ),
    (
        "cyberdyne-008",
        "Platform accuracy benchmarked at 94% on industry test datasets.",
        "2025-07-22T14:00:00Z",
        "2025-07-22T14:00:00Z",
    ),
    (
        "cyberdyne-008",
        "First paying customer: regional bank for fraud detection.",
        "2025-09-08T10:00:00Z",
        "2025-09-08T10:00:00Z",
    ),
    (
        "cyberdyne-008",
        "Team grew from 5 to 18 — mostly ML engineers.",
        "2025-11-01T11:00:00Z",
        "2025-11-01T11:00:00Z",
    ),
    (
        "cyberdyne-008",
        "Accepted into Microsoft for Startups program — $150K Azure credits.",
        "2026-01-18T09:30:00Z",
        "2026-01-18T09:30:00Z",
    ),
]

# ── Summaries (4 total: 2 fresh, 2 stale) ────────────────────────────────────

COMPANY_NAME_MAP = {cid: name for cid, name in COMPANIES}


def _build_summaries(note_ids_by_company: dict[str, list[str]]) -> list[tuple]:
    """Build summary rows. Needs actual note IDs so citations are valid."""

    return [
        # ── FRESH: acme-001 — summary created 2026-02-01, latest note is 2026-01-10
        (
            str(uuid.uuid4()),
            "acme-001",
            (
                "Acme Corp closed FY2025 at $52M ARR, exceeding guidance by 6%. "
                "Key drivers include 12% YoY Q3 revenue growth fueled by EMEA expansion, "
                "a $4.2M Azure infrastructure deal, and successful SOC 2 Type II completion. "
                "Leadership changes (new CFO, VP Engineering from Microsoft) signal a pivot "
                "toward AI-first strategy, formalized in the 2026 strategic plan. "
                "Employee headcount crossed 500 (+40% YoY) and the annual customer conference "
                "saw 3x attendance growth, indicating strong market momentum."
            ),
            json.dumps(note_ids_by_company["acme-001"][:10]),  # cite first 10 notes
            "2026-02-01T12:00:00Z",
            "v1.0",
        ),
        # ── STALE: globex-002 — summary created 2026-01-15, but notes exist from Feb/Mar 2026
        (
            str(uuid.uuid4()),
            "globex-002",
            (
                "Globex Industries reached $180M annual revenue (+11% YoY) despite a Q2 "
                "product recall that temporarily impacted satisfaction scores. The company "
                "recovered through aggressive quality hiring and achieved 34% gross margins "
                "by Q3. Strategic wins include an $8M HomeDepot fulfillment contract, "
                "expansion into Latin America, and the Globex Green sustainability initiative "
                "targeting net-zero by 2030. The NRF 'Best Logistics Partner' award validates "
                "operational improvements."
            ),
            json.dumps(note_ids_by_company["globex-002"][:8]),
            "2026-01-15T12:00:00Z",  # STALE: notes exist at 2026-02-01, 02-18, 03-10
            "v1.0",
        ),
        # ── FRESH: initech-003 — summary created 2026-02-10, latest note is 2026-01-15
        (
            str(uuid.uuid4()),
            "initech-003",
            (
                "Initech Solutions completed a full SAP S/4HANA migration on schedule and "
                "on budget over 12 months. All modules — Finance, Procurement, Manufacturing "
                "— are operational with a 96% UAT pass rate and a post-go-live defect rate "
                "of just 0.3%. The migration has yielded an estimated 30% efficiency gain, "
                "presented by the CIO at an industry conference. The project is a strong "
                "reference case for enterprise ERP modernization."
            ),
            json.dumps(note_ids_by_company["initech-003"][:8]),
            "2026-02-10T12:00:00Z",
            "v1.0",
        ),
        # ── STALE: umbrella-004 — summary created 2025-12-01, but notes exist from Jan/Feb/Mar 2026
        (
            str(uuid.uuid4()),
            "umbrella-004",
            (
                "Umbrella Health secured $45M in Series C funding and received FDA clearance "
                "for its portable diagnostic device. Q2 device sales tripled to 15,000 units, "
                "and a CVS Health partnership extends reach through in-store kiosks. "
                "The revenue forecast was raised from $30M to $38M. Regulatory standing "
                "remains strong with ISO 13485 renewal (zero non-conformances) and a pending "
                "510(k) for a next-gen respiratory panel."
            ),
            json.dumps(note_ids_by_company["umbrella-004"][:7]),
            "2025-12-01T12:00:00Z",  # STALE: notes exist at 2026-01-25, 02-14, 03-05
            "v1.0",
        ),
    ]


# ── Seed logic ────────────────────────────────────────────────────────────────


def seed(reset: bool = False) -> None:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if reset:
        cur.execute("DROP TABLE IF EXISTS notes")
        cur.execute("DROP TABLE IF EXISTS summaries")
        print("Dropped existing tables.")

    # Create tables
    cur.executescript(SCHEMA)

    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM notes")
    if cur.fetchone()[0] > 0:
        print(f"Database already seeded ({DB_PATH}). Use --reset to reseed.")
        conn.close()
        return

    # Insert notes — generate UUIDs and track them by company for citations
    note_ids_by_company: dict[str, list[str]] = {cid: [] for cid, _ in COMPANIES}

    for company_id, notes_text, created_on, updated_on in _NOTES_RAW:
        note_id = str(uuid.uuid4())
        company_name = COMPANY_NAME_MAP[company_id]
        cur.execute(
            "INSERT INTO notes (id, company_id, company_name, notes, created_on, updated_on) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (note_id, company_id, company_name, notes_text, created_on, updated_on),
        )
        note_ids_by_company[company_id].append(note_id)

    # Insert summaries
    for row in _build_summaries(note_ids_by_company):
        cur.execute(
            "INSERT INTO summaries (id, company_id, summary, citations, created_on, prompt_version) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            row,
        )

    conn.commit()
    conn.close()

    # Print summary
    print(f"Database created at {DB_PATH}")
    print(f"  Notes:     {len(_NOTES_RAW)} rows across {len(COMPANIES)} companies")
    print(f"  Summaries: 4 rows (2 fresh, 2 stale)")
    print()
    print("  Fresh summaries: acme-001, initech-003")
    print("  Stale summaries: globex-002 (3 new notes), umbrella-004 (3 new notes)")
    print("  No summary:      stark-005, wayne-006, oscorp-007, cyberdyne-008")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the notes database.")
    parser.add_argument(
        "--reset", action="store_true", help="Drop and recreate tables."
    )
    args = parser.parse_args()
    seed(reset=args.reset)
