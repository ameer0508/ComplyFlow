# ComplyFlow — End-to-End Enterprise Architecture

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** Unified Architecture, Component Topology & Cross-Tier Integration
**Status:** Architecture Specification & Multi-Tier Implementation Blueprint

---

## 1. Architectural Mission & Positioning

ComplyFlow is designed as a modular, enterprise-grade compliance platform architecture that unifies operational request intake, workflow automation, analytical intelligence, and assistive AI into a coherent, governed system.

```
┌────────────────────────────────────────────────────────────────────────┐
│                               COMPLYFLOW                               │
│                   Unified Compliance Architecture                      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
       [ Requester / Compliance Analyst / Operational Supervisor ]
                                    │
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │ 1. User Interface Layer: Microsoft Power Apps (Canvas)   │ 🟡 DESIGNED
       │    • Standardized Request Submission (scr_NewRequest)    │
       │    • Personal Analyst Caseload (scr_MyQueue)             │
       │    • Case Investigation & Status Updates (scr_CaseUpdate)│
       │    • Operational Triage & Filtering (scr_OperationalQueue│
       └────────────────────────────┬─────────────────────────────┘
                                    │ (Patch / Read-Write Binding)
                                    ▼
       ┌──────────────────────────────────────────────────────────┐
       │ 2. Operational Data Store: SharePoint Online Lists       │ 🟡 DESIGNED
       │    • ComplianceRequests (Core case attributes)           │
       │    • RequestAuditLog (Immutable sequential milestones)   │
       │    • SLAPolicies (Governance tier definitions)           │
       └──────────────┬────────────────────────────┬──────────────┘
                      │                            │
         (Event / Scheduled Triggers)              │ (ETL / Curated Sync)
                      ▼                            ▼
┌──────────────────────────────────────┐ ┌──────────────────────────────────────┐
│ 3. Workflow Automation Tier          │ │ 4. Analytical Data Tier              │
│    Microsoft Power Automate          │ │    SQLite / SQL Engine               │
│    🟡 DESIGNED                       │ │    🟢 REAL / VERIFIED                │
│ • CF-01: Process New Request & SLA   │ │ • Database: complyflow.db            │
│ • CF-02: Track Case Assignment       │ │ • vw_request_performance             │
│ • CF-03: Route Compliance Approvals  │ │ • vw_active_backlog                  │
│ • CF-04: Monitor Compliance SLAs     │ │ • vw_process_area_performance        │
│ • CF-05: Record Milestone Audit Log  │ │ • 150 requests, 716 audit events     │
│ • CF-06: Process Case Closure        │ │ • Automated Python Quality Validator  │
└──────────────────────────────────────┘ └──────────────────┬───────────────────┘
                                                            │
                                                            ▼
                                         ┌──────────────────────────────────────┐
                                         │ 5. Business Intelligence Layer       │
                                         │    Microsoft Power BI Desktop        │
                                         │    🟡 DESIGNED                       │
                                         │ • Star Schema: DimDate, DimSLA, Facts│
                                         │ • 14 Governed DAX Calculations       │
                                         │ • Page 1: Executive Overview         │
                                         │ • Page 2: Operational Workload       │
                                         │ • Page 3: SLA & Process Performance  │
                                         │ • Page 4: Case / Operational Detail  │
                                         └──────────────────┬───────────────────┘
                                                            │
                                                            ▼
                                         ┌──────────────────────────────────────┐
                                         │ 6. AI Intelligence & Copilot Layer   │
                                         │    "Ask ComplyFlow" Assistant        │
                                         │    🟡 DESIGNED                       │
                                         │ • Natural-Language KPI Q&A           │
                                         │ • 30-Second Case Summaries           │
                                         │ • Chronological Audit Narratives     │
                                         │ • Read-Only RAG Grounding            │
                                         │ • Strict Human-in-the-Loop Safeguards│
                                         └──────────────────┬───────────────────┘
                                                            │
                                                            ▼
                                         ┌──────────────────────────────────────┐
                                         │ 7. Human Governance & Decision Tier  │
                                         │ • Compliance Officer reviews outputs │
                                         │ • Human executes final determination │
                                         │ • Zero autonomous compliance actions │
                                         └──────────────────────────────────────┘
```

---

## 2. Component Inventory & Implementation Classification

Every component in ComplyFlow is explicitly classified according to its current implementation state:

| Architectural Tier | Specific Component | Target Technology | Implementation Classification | Description |
| :--- | :--- | :--- | :---: | :--- |
| **Data Layer** | Synthetic Compliance Dataset | Python / CSV | 🟢 REAL / VERIFIED | 150 compliance requests, 716 audit events, 4 SLA policies in `data/raw/`. |
| **Data Layer** | Relational Database & Views | SQLite (`complyflow.db`) | 🟢 REAL / VERIFIED | Relational schema, indexes, foreign keys, and 5 analytical views. |
| **Validation Layer** | Data Quality Test Suite | Python (`validate_data.py`) | 🟢 REAL / VERIFIED | Automated checks for lifecycle state transitions, dates, and SLA consistency. |
| **Validation Layer** | Database Verification Suite | Python (`verify_database.py`)| 🟢 REAL / VERIFIED | Automated verification of row counts, key integrity, and KPI reconciliation. |
| **Scenario Layer** | Financial Institution Scenario | Fictional Design | 🔵 SYNTHETIC / SIMULATED | Fictional demonstration context; zero connection to any real enterprise. |
| **UI Tier** | Canvas Application Interface | Power Apps | 🟡 DESIGNED / SPECIFIED | 6-screen specification with complete formulas, validation, and design tokens. |
| **Operational Store**| Relational List Schema | SharePoint Online | 🟡 DESIGNED / SPECIFIED | Complete list schema, field typing, indexing, and lookup relationships. |
| **Automation Tier** | Workflow Orchestration Suite | Power Automate | 🟡 DESIGNED / SPECIFIED | 6 consolidated cloud flows with triggers, conditions, and error-handling. |
| **Reporting Tier** | Star-Schema Analytics & DAX | Power BI Desktop | 🟡 DESIGNED / SPECIFIED | 4-page report layout, 14 DAX measures, and dimensional relationships. |
| **AI Tier** | "Ask ComplyFlow" Copilot | Copilot Studio / AI | 🟡 DESIGNED / SPECIFIED | 6 core capabilities, 12 governance pillars, 11 guardrails, and test plan. |
| **Cloud Deployment** | Live M365 / Power Platform | Microsoft 365 Cloud | 🔴 NOT BUILT / NOT DEPLOYED | No live enterprise tenant or production gateway connected. |
| **Cloud Deployment** | Live Copilot / Azure OpenAI | Azure AI / OpenAI | 🔴 NOT BUILT / NOT DEPLOYED | No live cloud model instance, bot deployment, or API endpoint configured. |

---

## 3. End-to-End Data Pipeline Flow

The lifecycle of compliance information progresses through six defined transformation phases:

```
[ CAPTURE ] ──► [ GOVERN ] ──► [ AUTOMATE ] ──► [ ANALYZE ] ──► [ IMPROVE ] ──► [ ASSIST ]
```

### Stage 1: Capture (Operational Intake)
- **Actor:** Operational business requester (e.g., front-office trading desk, onboarding specialist).
- **Interface:** Power Apps `scr_NewRequest`.
- **Action:** User submits a request with required fields (`RequestType`, `ProcessArea`, `Priority`, `Description`, counterparty details).
- **Control:** Client-side validation prevents submission of incomplete records.

### Stage 2: Govern (SLA Assignment & Initial Stamping)
- **Mechanism:** Power Automate flow `CF-01: Process New Request`.
- **Action:** Flow queries `SLAPolicies` matching the selected `RiskLevel`, computes `TargetDueDateTime = SubmissionDateTime + SLATargetHours`, and stamps `ApprovalRequired` and `EscalationRole`.
- **Ledger:** Writes the initial immutable `Submitted` milestone to `RequestAuditLog`.

### Stage 3: Automate (Lifecycle Orchestration & Alerts)
- **Mechanism:** Power Automate flows `CF-02` through `CF-06`.
- **Action:** Dispatches assignment notices when analysts take ownership (`CF-02`); routes dual-tier sign-off tasks when cases enter `Pending Approval` (`CF-03`); monitors approaching deadlines and auto-escalates breached cases (`CF-04`); records milestone transitions (`CF-05`); validates closure criteria (`CF-06`).

### Stage 4: Analyze (Governed Analytics & Reporting)
- **Mechanism:** Curated SQLite analytical views (`vw_*`) and Power BI Star Schema.
- **Action:** Translates operational transactions into management-grade intelligence:
  - `[Active Backlog]` (50 cases)
  - `[Overdue Cases]` (24 cases)
  - `[Historical SLA Breach Rate]` (12.0%)
  - `[Average Resolution Time]` (69.27 hours)
  - Workload distribution across 5 Process Areas and 3 Compliance Teams.

### Stage 5: Improve (Process Bottleneck Discovery)
- **Mechanism:** Power BI Page 3 and analytical queries.
- **Action:** Surfaces operational friction points, such as AML turnaround times (80.12h avg) and queue dwell times, providing management with empirical evidence for process optimization.

### Stage 6: Assist (AI-Assisted Context & Triage)
- **Mechanism:** "Ask ComplyFlow" conversational assistant.
- **Action:** Provides compliance analysts and managers with natural-language access to case dossiers, chronological audit timelines, and SLA policies.
- **Boundary:** Strictly read-only; all outputs are assistive and require human verification.

---

## 4. Security, Governance & Audit Architecture

1. **Separation of Duties:** Requesters, investigating analysts, and approving managers operate under distinct operational personas and permissions.
2. **Immutability of the Audit Ledger:** The `RequestAuditLog` table maintains an append-only transaction history. System rules forbid updating or deleting historical audit entries.
3. **Data Quality Enforcements:** Automated Python validation scripts verify that all completed cases possess non-null completion dates and that historical SLA breach flags reconcile with recorded timestamps.
4. **Human-in-the-Loop Primacy:** Neither automated workflows nor AI assistants possess autonomous authority to approve, reject, or close regulatory compliance matters.
