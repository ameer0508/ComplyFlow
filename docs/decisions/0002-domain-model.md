# 0002. Domain Model and Entity Simplification

**Status:** Accepted (Refined Baseline)
**Date:** 2026-09-26
**Context:** Compliance Development Apprentice Portfolio Prototype

---

## Context and Problem Statement

When designing a compliance operations platform, there is a temptation to introduce extensive enterprise complexity—such as multi-regional working calendar engines, separate relational approval hierarchies, per-keystroke audit databases, and multi-table team schemas.

ComplyFlow is designed as a focused, realistic, and explainable prototype tailored for a **Compliance Development Apprentice** portfolio. The architecture must:
1. Support genuine operational automation (Power Automate).
2. Store clean operational records (SharePoint & SQL).
3. Provide rich analytical insights into operational bottlenecks, process areas, and SLAs (Power BI & Python).
4. Remain fully understandable and defendable by a junior developer during technical and HR interviews.

We need to justify why specific entities were retained, why specific attributes were refined, and how this design fulfills the job specification's core requirements.

---

## Key Refinements & Architectural Decisions

### 1. SLA Model: Calendar Hours for MVP Simplicity
- **Decision:** Selected **calendar hours** (Critical = 24h, High = 72h, Medium = 120h, Low = 240h) rather than business days.
- **Rationale:** Business-day calculations introduce heavy calendar lookup tables, regional bank holiday logic, and complex weekend skipping algorithms that distract from core workflow concepts. In an interview, an apprentice can clearly explain:
  $$\text{TargetDueDateTime} = \text{SubmissionDateTime} + \text{SLATargetHours}$$
  This provides immediate, clean, explainable timestamps while documenting that a production system would later incorporate regional banking holiday calendars.

### 2. Operational Dimension: `ProcessArea`
- **Decision:** Added a controlled `ProcessArea` choice attribute (`Customer Onboarding`, `AML Operations`, `KYC Operations`, `Sanctions`, `Policy & Governance`) directly to `ComplianceRequest`.
- **Rationale:** Allows management reporting to answer critical operational questions:
  - *Which process area experiences the highest SLA breach rate?*
  - *Where is the longest average resolution time?*
  - *Which area carries the largest backlog?*
  Modeled as a controlled choice rather than a separate table to eliminate join friction in SharePoint and Power Apps.

### 3. Derived Analytical Metric: `ResolutionTimeHours`
- **Decision:** `ResolutionTimeHours` is **strictly derived in the analytics layer** (SQL views, Python scripts, or Power BI DAX measures) rather than stored as an editable form field.
- **Rationale:** Storing user-entered cycle times invites human error, inconsistencies, and audit tampering. By defining:
  $$\text{ResolutionTimeHours} = \text{CompletionDateTime} - \text{SubmissionDateTime} \quad (\text{Closed cases only})$$
  open cases remain cleanly un-resolved, and metric integrity is preserved across all reporting platforms.

### 4. Approval & Escalation Logic
- **Decision:** `ApprovalRequired` is derived directly from `SLAPolicy` (mandatory for `High` and `Critical` risk tiers). Approval and escalation fields are embedded directly on `ComplianceRequest` rather than in separate child tables.
- **Rationale:** 95%+ of compliance requests require at most one primary management sign-off. Embedding approval metadata (`ApprovalRequired`, `ApprovedBy`, `ApprovalDate`) and escalation metadata (`EscalationFlag`, `EscalatedTo`, `EscalationReason`) avoids complex 1-to-many relationship handling in Power Apps while fully satisfying audit and workflow requirements.

### 5. Milestone-Based Audit Trail (`RequestAuditLog`)
- **Decision:** Standardized `RequestAuditLog` on 9 discrete milestone actions: `Created`, `Submitted`, `Assigned`, `Status Changed`, `Escalated`, `Approval Requested`, `Approved`, `Rejected`, `Closed`.
- **Rationale:** Per-keystroke or per-field change data capture creates massive noise and list bloat without adding portfolio value. Milestone logging captures exactly who made critical decisions, when status transitions occurred, and what rationale accompanied escalations or sign-offs.

---

## Retained Core Schema Summary

```
SLAPolicy (1) ──────────< ComplianceRequest (M) ──────────< RequestAuditLog (M)
[Reference Entity]       [Core Transactional]              [Supporting Audit]
```

- **`SLAPolicy`:** Decouples SLA rules and approval mandates from application code.
- **`ComplianceRequest`:** Central hub capturing request details, risk, timestamps, and resolution.
- **`RequestAuditLog`:** Chronological ledger of key operational milestones.

---

## Consequences & Interview Readiness

- **High Explainability:** The entire data architecture can be articulated in 3 minutes with zero ambiguity.
- **Direct Alignment with Job Description:** Demonstrates process redesign (intake validation), workflow automation (event-driven triggers), governance (audit logs), and process intelligence (bottleneck analysis by `ProcessArea`).
- **Complete Offline Portability:** Schema is 100% compatible with SQLite, Python `pandas`, and Power BI Desktop before any cloud tenant is provisioned.
