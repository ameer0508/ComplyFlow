# 0003. SharePoint as the Operational Low-Code Data Layer

**Status:** Accepted
**Date:** 2026-09-26
**Context:** Compliance Development Apprentice Portfolio Prototype

---

## Context and Problem Statement

A modern compliance technology architecture requires both **operational execution** (user forms, case routing, notifications, approvals) and **analytical intelligence** (metrics, SLA trend analysis, bottleneck identification).

When designing the operational persistence tier for Microsoft Power Platform, three potential data stores were considered:
1. Microsoft Dataverse
2. Dedicated Cloud SQL Database (Azure SQL Server)
3. Microsoft SharePoint Online Lists

We need to justify why SharePoint Online was chosen as the operational data store for ComplyFlow and clarify how it coexists with the local SQLite / SQL analytics layer.

---

## Decision Drivers

- **Zero Licensing & Administrative Overhead:** Dataverse and Azure SQL require premium Power Platform licensing (per-user or per-app plan) and dedicated Azure cloud subscriptions. SharePoint Online is universally accessible within standard Microsoft 365 Developer and enterprise tenants.
- **Native Power Platform Connectivity:** SharePoint is natively supported as a standard connector across Power Apps and Power Automate with instant integration and zero gateway configuration.
- **Explainability:** SharePoint lists provide transparent, human-readable column schemas, visual views, and audit versioning that an apprentice developer can easily explain during interviews.
- **Clear Architectural Separation:** Clear separation between **operational workflow processing** and **relational analytical querying**.

---

## Decision: SharePoint Online for Operations + SQLite for Analytics

### 1. Operational Workflow Tier: SharePoint Online
SharePoint Online is selected as the **operational transaction store** for:
- Receiving submissions from Microsoft Power Apps.
- Storing active case attributes, status transitions, and approval metadata.
- Triggering event-driven cloud flows in Microsoft Power Automate (submission alerts, approval cards, deadline countdowns).
- Providing immediate list views (Active Queue, Overdue Cases, Pending Approvals) for operational teams.

### 2. Analytical Intelligence Tier: SQLite / SQL Engine
The local SQLite database (`database/complyflow.db`) is retained as the **analytical query engine** for:
- Running multi-table joins, aggregations, and window functions.
- Performing data quality validation and schema enforcement via Python.
- Calculating derived process metrics (e.g., `ResolutionTimeHours`, stage dwell times).
- Serving as the reproducible SQL demonstration repository for technical interviews.

```
┌──────────────────────────────────────────────┐
│           Operational Workflow Tier          │
│          (SharePoint Online Lists)           │
│  • Powers Power Apps Intake                  │
│  • Triggers Power Automate Flows             │
│  • Houses Active Case Working Queues         │
└──────────────────────┬───────────────────────┘
                       │ Snapshot / Export
                       ▼
┌──────────────────────────────────────────────┐
│           Relational Analytics Tier          │
│            (SQLite / Python Engine)          │
│  • Executes SQL Analytical Views             │
│  • Calculates Process Bottleneck Metrics     │
│  • Feeds Power BI Reporting Model            │
└──────────────────────────────────────────────┘
```

---

## What SharePoint Is NOT

- **SharePoint is NOT replacing the SQL analytics layer.** SharePoint is not a relational database and lacks support for complex SQL joins, window functions, and CTEs.
- **SharePoint is NOT a heavy enterprise database.** It is chosen because it perfectly fulfills the operational requirements of an internal compliance workflow prototype without unnecessary enterprise bloat.

---

## Consequences

### Positive Consequences
- **Rapid Prototyping:** The operational lists can be created manually in under 20 minutes following the build specification.
- **Cost Effective:** Operates within standard M365 developer tenant boundaries with zero premium connector costs.
- **Clean Architecture:** Teaches the fundamental enterprise distinction between OLTP (operational transaction processing) and OLAP (analytical reporting).

### Trade-Offs & Mitigations
- **Delegation Limits:** Large SharePoint lists (>5,000 items) face query delegation constraints in Power Apps.
  *Mitigation:* In ComplyFlow, operational active queues rarely exceed a few hundred active records. Historical records are analyzed in the SQL/Power BI analytics layer.
- **Relational Constraints:** SharePoint does not natively enforce foreign keys or cascading deletes.
  *Mitigation:* Power Automate cloud flows enforce relational consistency between `ComplianceRequests` and `RequestAuditLog`.
