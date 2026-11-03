# LeadPilot — zero-cost AI-ready lead qualification demo

**Runnable Python portfolio proof of concept:** synthetic B2B prospects → explainable scoring → duplicate suppression → customer exclusions → human review → local searchable dashboard and CSV export. A read-only JSON API is provided.

> **Important:** Independent educational demo, not deployed for any client. All businesses and evidence are fictional. No live CRM, AI API, customer data, lead scraping, production marketing results, or automated outreach. Optional AI enrichment is an *architectural next step*, not a claim about this implementation.

## Run (Python 3.9+; no pip or API key)

```bash
python app.py
# visit http://127.0.0.1:8000/
# JSON: http://127.0.0.1:8000/api/leads
python -m unittest -v
```

**All software dependencies are Python standard library. Cost to run: $0** beyond your existing computer/internet.

## Architecture

```text
Synthetic CSV
    ↓
Normalize company + city / detect duplicates
    ↓
Score: sector fit + service area + evidence + verified contact
    ↓
Block: duplicates / existing customers / outside territory
    ↓
Flag: potential or unknown usage needs human verification
    ↓
Local browser dashboard + evidence explanations
    ├─ CSV review queue export
    └─ Read-only JSON endpoint (/api/leads)
    ↓
[Future: CRM adapter] → [Future: supervised LLM enrichment]
                     → [Future: sales-approved outreach]
```

## Scoring rules

- Industry fit: warehouse, forklift service and manufacturing +35; restaurant and hotel +20.
- In service area: +25.
- Propane evidence: **confirmed** +30; **potential** +10; **unknown** +0. These are labels in deliberately synthetic input, not real-world claims.
- Verified business contact: +10.
- Priority: high ≥75, medium 50–74, low below 50.
- Duplicate records, existing customers and out-of-area leads are blocked **regardless of score**. Other leads are still flagged for human review. There is intentionally no send/approve endpoint.

## How to use

1. Open local dashboard and review summary counters.
2. Search by name or city, and filter by priority or review state.
3. Expand **Show details** to inspect every scoring reason and safety flag.
4. Export filtered review records with **Export review CSV**.
5. Use `/api/leads` for JSON suitable for a future tested CRM integration.

## Files

- `app.py`: scoring rules, browser dashboard, read-only HTTP API.
- `sample_leads.csv`: eight fictional examples including duplicates and exclusions.
- `test_app.py`: unit tests for data, scoring and safeguards.
- `.gitignore`: avoids publishing secrets and local artifacts.

## Next production milestones (not implemented)

Use licensed business data with source provenance and consent; connect CRM via authenticated API; add idempotent imports, retry/backoff, role-based access and durable audit records; optional Claude classification with structured JSON and grounded source citations; approved email provider, opt-out controls and sales-team review gates; measure real funnel results with a client-approved pilot.

**Suggested portfolio line:** “Built an original, dependency-free B2B lead qualification prototype with deterministic scoring, deduplication, existing-customer filtering, evidence labels, a review dashboard, JSON endpoint, CSV export and automated tests, using only fictional data.”
