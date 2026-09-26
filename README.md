# ComplyFlow

## Compliance Workflow & Process Intelligence Platform

[![Feature Branch](https://img.shields.io/badge/Branch-feature%2Frepository--foundation-blue.svg)](https://github.com/ameer0508/ComplyFlow)
[![Python 3.13](https://img.shields.io/badge/Python-3.13-green.svg)](https://www.python.org/)
[![SQLite Verified](https://img.shields.io/badge/SQLite-Verified%20(complyflow.db)-brightgreen.svg)](database/README.md)
[![Status](https://img.shields.io/badge/Architecture-Portfolio%20Specification-orange.svg)](#implementation-status)

ComplyFlow is a portfolio-grade compliance operations platform concept that unifies regulatory request intake, SLA governance, workflow automation, operational analytics, and AI-assisted triage into a single auditable ecosystem.

---

### Overview

In financial services, regulatory compliance operations (e.g., KYC periodic refreshes, AML transaction reviews, sanctions screenings, and policy exceptions) are time-critical and legally sensitive. Yet operations teams often manage these high-stakes requests through disconnected email inboxes, spreadsheets, and ad-hoc chat threads.

ComplyFlow demonstrates how modern low-code tools (Microsoft Power Platform), relational SQL modeling, Python validation, and generative AI copilot patterns can be architected together to eliminate operational blind spots, enforce statutory deadlines, and deliver executive-grade visibility.

---

### Business Problem

Compliance operations face five major challenges in unintegrated environments:
1. **Fragmented Intake:** Requests arrive via untracked emails with missing counterparty details and unverified risk classifications.
2. **Opaque SLA Exposure:** SLA deadlines are calculated manually, leaving managers unaware when regulatory breaches are imminent.
3. **Administrative Chasing:** Analysts spend valuable investigative hours emailing managers for sign-offs and status updates.
4. **Supervisory Blind Spots:** Department heads lack real-time visibility into queue congestion and analyst workload allocation.
5. **Auditability Deficits:** Reconstructing an audit trail for regulators requires manual compilation across disparate mailboxes.

---

### Solution

ComplyFlow replaces operational fragmentation with a unified, 6-stage transformation model:

```
CAPTURE  ──►  GOVERN  ──►  AUTOMATE  ──►  ANALYZE  ──►  IMPROVE  ──►  ASSIST
```

* **Standardized Intake:** Enforces structured capture of counterparty details and risk classifications.
* **Deterministic SLA Governance:** Automatically assigns turnaround deadlines based on policy risk tier (Critical = 24h, High = 72h, Medium = 120h, Low = 240h).
* **Automated Workflow Orchestration:** Dispatches assignment notices, approval requests, deadline warning alerts, and executive escalations.
* **Governed Analytical Modeling:** Powers interactive star-schema dashboards that cleanly separate current active backlogs from completed historical cycle times.
* **Assistive Intelligence:** Delivers 30-second case summaries and audit explanations with strict human-in-the-loop safeguards.

---

### End-to-End Workflow

```
Request Intake ──► SLA Calculation ──► Assignment ──► Investigation ──► Approval ──► Closure ──► Audit Ledger ──► Analytics ──► AI Assistance
```

1. **Intake:** Requester submits request in Power Apps (`scr_NewRequest`).
2. **Governance:** Flow looks up `SLAPolicies`, calculates `TargetDueDateTime`, stamps SLA hours, and creates initial `Submitted` audit log.
3. **Assignment:** Assigned analyst receives notice; status updates to `Under Review`.
4. **Approval:** High/Critical cases automatically route to supervisory roles (`Pending Approval`).
5. **Escalation:** Overdue or flagged items escalate to designated roles (e.g., Head of Compliance for Critical items).
6. **Archival:** Final disposition is validated, closure notes recorded, and case archived (`Closed`).
7. **Audit Trail:** Every transition is recorded in an immutable, append-only audit ledger (`RequestAuditLog`).
8. **Analytics & AI:** Curated views feed Power BI dashboards and the "Ask ComplyFlow" assistant.

---

### Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                               COMPLYFLOW                               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
       [ Requester / Compliance Analyst / Operational Supervisor ]
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │ Microsoft Power Apps Canvas App (User Interface)         │ 🟡 DESIGNED
       │ scr_NewRequest | scr_MyQueue | scr_CaseUpdate            │
       └────────────────────────────┬─────────────────────────────┘
                                    │ (Patch / Read-Write Binding)
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │ SharePoint Online Lists (Operational Store)              │ 🟡 DESIGNED
       │ ComplianceRequests | RequestAuditLog | SLAPolicies       │
       └──────────────┬────────────────────────────┬──────────────┘
                      │                            │
         (Event / Scheduled Triggers)              │ (ETL / Curated Sync)
                      ▼                            ▼
┌──────────────────────────────────────┐ ┌──────────────────────────────────────┐
│ Microsoft Power Automate             │ │ SQLite Analytical Engine             │
│ Workflow Orchestration Engine        │ │ database/complyflow.db               │
│ 🟡 DESIGNED                          │ │ 🟢 REAL / VERIFIED                   │
│ • CF-01: Intake & SLA Stamping       │ │ • vw_request_performance             │
│ • CF-02: Analyst Assignment          │ │ • vw_active_backlog                  │
│ • CF-03: Supervisory Approvals       │ │ • vw_process_area_performance        │
│ • CF-04: SLA Warnings & Escalations  │ │ • 150 requests, 716 audit events     │
│ • CF-05: Milestone Audit Logging     │ │ • Automated Python Quality Validator │
│ • CF-06: Case Closure Validation     │ └──────────────────┬───────────────────┘
└──────────────────────────────────────┘                    │
                                                            ▼
                                         ┌──────────────────────────────────────┐
                                         │ Microsoft Power BI Desktop           │
                                         │ Dimensional Star-Schema Reporting    │
                                         │ 🟡 DESIGNED                          │
                                         │ • 14 Governed DAX Calculations       │
                                         │ • 4-Page Executive & Triage Suite    │
                                         └──────────────────┬───────────────────┘
                                                            │
                                                            ▼
                                         ┌──────────────────────────────────────┐
                                         │ "Ask ComplyFlow" AI Copilot          │
                                         │ Read-Only Contextual Intelligence    │
                                         │ 🟡 DESIGNED                          │
                                         │ • Natural-Language KPI Q&A           │
                                         │ • Case Dossiers & Audit Narratives   │
                                         │ • Strict Human-in-the-Loop Controls  │
                                         └──────────────────────────────────────┘
```

---

### Technology Stack

* **Relational Database & Analytics:** SQLite 3, ANSI SQL, Relational Modeling, Star-Schema Dimensional Design
* **Data Engineering & Testing:** Python 3.13 (`csv`, `sqlite3`, `pathlib`, `statistics`), Automated Quality Suites
* **Application Interface (Design):** Microsoft Power Apps (6-Screen Canvas App Specification)
* **Operational Data Store (Design):** SharePoint Online (Relational List Schemas & Lookups)
* **Workflow Automation (Design):** Microsoft Power Automate (6 Consolidated Cloud Flows)
* **Business Intelligence (Design):** Microsoft Power BI Desktop (Star-Schema, 14 DAX Measures, 4 Pages)
* **Assistive AI (Design):** "Ask ComplyFlow" Copilot Specification (RAG Architecture, 11 Guardrails)
* **Assistant Environment:** Antigravity (Advanced Agentic Coding Environment)

---

### Key Capabilities

* **Standardized Intake & Triage:** Enforces complete counterparty metadata, risk tiering, and operational classification.
* **Automated SLA Governance:** Automatic due date stamping with proactive warning notifications and supervisory escalation.
* **Immutable Auditability:** 100% append-only audit trail capturing every state change, actor, and timestamp.
* **Executive & Queue Analytics:** Granular visibility into active backlogs, overdue items, cycle times, and bottleneck stages.
* **Assistive AI Summarization:** Rapid 30-second case briefs and natural-language queries under strict human oversight.

---

### Verified Prototype Metrics

All analytical views and calculations are verified against a local SQLite database ([database/complyflow.db](database/README.md)) populated with 150 synthetic compliance requests:

| Operational Metric | Underlying Source / View | Verified Value | Scope |
| :--- | :--- | :---: | :--- |
| **Total Requests** | `ComplianceRequest` table | **`150`** | Cumulative aggregate |
| **Closed Requests** | `vw_request_performance WHERE Status = 'Closed'` | **`100`** | Historical completed |
| **Active Backlog** | `vw_active_backlog WHERE Status != 'Closed'` | **`50`** | Current open queue |
| **Overdue Active Cases** | `vw_active_backlog WHERE SLAState = 'Overdue'` | **`24`** | Evaluated at anchor `2026-09-26 17:00` |
| **Approaching Deadline** | `vw_active_backlog WHERE SLAState = 'Approaching'` | **`0`** | Current warning window |
| **On Track Active Cases**| `vw_active_backlog WHERE SLAState = 'On Track'` | **`26`** | Safe SLA buffer |
| **Historical Breached** | `ComplianceRequest WHERE Status = 'Closed' AND SLABreachFlag = 1` | **`12`** | Historical closed |
| **Historical Breach Rate**| `12 / 100 * 100.0` | **`12.0%`** | Target benchmark: `< 5.0%` |
| **Average Resolution Time**| `AVG(ResolutionTimeHours) WHERE Status = 'Closed'` | **`69.27 hrs`** | Arithmetic mean |
| **Median Resolution Time** | `statistics.median(ResolutionTimeHours)` | **`44.79 hrs`** | Python verified array |
| **High/Critical Active** | `RiskLevel IN ('High', 'Critical') AND Status != 'Closed'` | **`15`** | Critical: 7, High: 8 |
| **Approval Required** | `ComplianceRequest WHERE ApprovalRequired = 1` | **`70`** | 46.7% of all requests |
| **Escalated Cases** | `ComplianceRequest WHERE EscalationFlag = 1` | **`17`** | 6 currently active in queue |

---

### Power Platform Mapping

ComplyFlow leverages Microsoft Power Platform components according to their optimal enterprise roles:

* **Power Apps:** Acts as the operational "front door"—providing analysts and requesters with a role-based, accessible interface.
* **SharePoint Online:** Serves as the operational data store—providing cloud-native list storage with version history.
* **Power Automate:** Serves as the workflow engine—decoupling background automation, reminders, and escalations from the UI.
* **Power BI:** Serves as the analytical engine—providing executive visibility, multi-dimensional slicing, and drill-through triage grids.

> *Note: Power Platform components are documented as complete implementation blueprints ready for manual tenant deployment; no live cloud tenant is currently provisioned.*

---

### AI / Ask ComplyFlow

**"Ask ComplyFlow"** is an AI compliance operations copilot designed to sit above the analytical and operational layers.

```
┌────────────────────────────────────────────────────────────────────────┐
│  Governing Principle:                                                  │
│  "AI assists compliance professionals; it does not replace compliance  │
│   judgment."                                                           │
└────────────────────────────────────────────────────────────────────────┘
```

* **Read-Only Context Retrieval:** Implements a RAG pattern grounded exclusively in governed SQL views, request records, and SLA policies.
* **Zero Autonomous Authority:** AI cannot approve, reject, escalate, or close cases.
* **Hallucination Controls:** If data is missing or incomplete, the assistant states: *"Insufficient recorded information."*
* **Mandatory Labeling:** Suggestions are tagged `[AI Suggested Next Step - Requires Human Verification]`.

---

### Data & Governance

* **Synthetic Data Integrity:** The dataset contains 150 requests, 716 audit milestone rows, and 4 SLA policies across 5 process areas (AML Operations, Customer Onboarding, KYC Operations, Sanctions, Policy & Governance).
* **Privacy & Compliance:** All client names, counterparties, emails, and transaction notes are 100% synthetic. Zero real customer or institutional data is used.
* **Immutable Audit Trail:** All state changes are permanently logged to `RequestAuditLog` with user IDs and timestamps.

---

### Implementation Status

To maintain engineering integrity, all components are classified into four explicit categories:

* 🟢 **REAL / VERIFIED:** Synthetic dataset (150 requests, 716 audit rows, 4 policies), SQLite database (`database/complyflow.db`), 5 analytical SQL views, automated Python validation suites (`analytics/scripts/validate_data.py`), and database verification suites (`database/verify_database.py`).
* 🟡 **DESIGNED / SPECIFIED:** Power Apps Canvas App blueprint, SharePoint Online list schemas, 6 Power Automate cloud flow designs, Power BI dimensional star-schema with 14 DAX measures, and "Ask ComplyFlow" AI governance architecture.
* 🔵 **SYNTHETIC / SIMULATED:** Fictional compliance scenarios, client entities, and operational transactions used for portfolio demonstration.
* 🔴 **NOT BUILT / NOT DEPLOYED:** Live Microsoft 365 cloud tenant, live Power Apps deployment, live cloud flows, Power BI Service workspace, or live Azure OpenAI endpoints.

---

### Repository Structure

```
ComplyFlow/
├── analytics/                      # Python validation scripts & test suites
│   └── scripts/validate_data.py    # Automated dataset quality validator
├── data/                           # Verified synthetic dataset
│   └── raw/                        # compliance_requests.csv, request_audit_log.csv, sla_policies.csv
├── database/                       # Relational database layer
│   ├── complyflow.db               # SQLite database with tables & analytical views
│   ├── load_database.py            # Automated database loader
│   ├── verify_database.py          # Database QA & KPI verification suite
│   └── queries/                    # Analytical views & business question queries
├── docs/                           # Strategic architecture & interview documentation
│   ├── architecture/               # End-to-end, data flow, AI, and domain models
│   ├── business-value.md           # Business problem, process transformation & qualitative ROI
│   ├── project-summary.md          # 2-minute executive summary for recruiters & managers
│   ├── portfolio-description.md    # Portfolio descriptions & resume-ready impact bullets
│   ├── interview-guide.md          # 25 interview questions/answers & spoken talk tracks
│   └── metrics-catalog.md          # Authoritative metric definitions, DAX & SQL formulas
├── power-platform/                 # Enterprise low-code implementation specifications
│   ├── power-apps/                 # Canvas App build spec, 6 screens, formulas, tokens
│   ├── sharepoint/                 # List schemas, field definitions, relationships
│   ├── power-automate/             # 6 consolidated cloud flows, trigger logic, error handling
│   ├── power-bi/                   # Star-schema design, 14 DAX measures, 4 report wireframes
│   └── copilot/                    # Ask ComplyFlow architecture, guardrails, response examples
└── README.md                       # Primary portfolio entry point
```

---

### Key Documentation

* [docs/business-value.md](docs/business-value.md) — Strategic business value, qualitative benefits, and process transformation.
* [docs/architecture/end-to-end-architecture.md](docs/architecture/end-to-end-architecture.md) — Unified enterprise architecture blueprint.
* [docs/project-summary.md](docs/project-summary.md) — 2-minute executive project briefing.
* [docs/portfolio-description.md](docs/portfolio-description.md) — Resume bullets, portfolio text, and tech stack details.
* [docs/interview-guide.md](docs/interview-guide.md) — 25 natural Q&As, architectural defensibility, and 30s/60s/2m talk tracks.
* [docs/metrics-catalog.md](docs/metrics-catalog.md) — Governed single source of truth for all operational calculations.

---

### Limitations

1. **Local Prototype Validation:** Data and analytics are verified locally in SQLite and Python; Microsoft cloud components are implementation specifications.
2. **Fixed Evaluation Timestamp:** SLA urgency metrics reference the fixed simulation anchor (`2026-09-26 17:00:00`) for reproducible testing.
3. **Calendar-Hour SLAs:** The current SLA engine calculates turnarounds in continuous calendar hours rather than business-day shifts.
4. **Assistive AI Scope:** "Ask ComplyFlow" has read-only visibility and cannot execute workflow actions autonomously.

---

### Future Implementation

With an active Microsoft 365 enterprise tenant, the next implementation phases would include:
1. Provisioning SharePoint Online lists using the documented schema.
2. Deploying the Power Apps Canvas interface using the validated formulas and layout tokens.
3. Activating the six Power Automate cloud flows.
4. Publishing the Power BI model to Power BI Service with scheduled cloud refresh.
5. Connecting Microsoft Copilot Studio via Power Platform custom connectors.

---

### Interview Summary

> *"ComplyFlow demonstrates how compliance intake, SLA governance, automated approvals, star-schema reporting, and assistive AI can be architected into a single governed system. I built and verified the data, SQL views, and validation scripts locally, while documenting the Power Platform and Copilot components as complete enterprise implementation specifications."*
