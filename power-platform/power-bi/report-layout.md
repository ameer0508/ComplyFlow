# ComplyFlow Power BI Report Layout & Visual Design Specification

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Power BI Visual Layout & UX Design
**Phase:** 6 (Executive Analytics & DAX Modelling)
**Status:** Visual Specification (Standard 16:9 Canvas: 1280 x 720 px)

---

## 1. Visual Design Principles & Design System

The visual design system adheres strictly to corporate compliance and enterprise data visualization standards:

* **Visual Hierarchy:** Critical executive summary KPIs appear in the top banner; exploratory breakdowns populate the middle body; time-series trends and granular triage grids occupy the lower sections.
* **Palette Tokens:**
  - **Navy Primary (`#1B365D`):** Headers, major chart accents, and active card titles.
  - **Slate Secondary (`#4A607A`):** Neutral category bars, historical completed metrics.
  - **Status Danger / Overdue (`#C0392B`):** Overdue cases, SLA breach rate, Critical risk alerts.
  - **Status Warning (`#D35400` / `#E67E22`):** High risk tier, approaching deadline cases, escalated cases.
  - **Status Success (`#27AE60`):** SLA met cases, on-track cases, approved items.
  - **Neutral Light (`#F8F9FA`):** Card background, canvas background.
  - **Gridlines & Borders (`#E2E8F0`):** Subtle visual separation.
* **Zero Decoration Rule:** Every visual element directly addresses one of the 12 core compliance business questions. No 3D effects, no decorative icons, no uncalibrated radial gauges.

---

## 2. Page 1 — Executive Compliance Overview

### 2.1 Purpose & Target Persona
Provides the Chief Compliance Officer (CCO), Head of Regulatory Affairs, and executive management with an immediate health check of compliance throughput, backlog risk, and regulatory SLA exposure.

### 2.2 Wireframe Layout (1280 x 720)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [LOGO] ComplyFlow — Executive Compliance Overview                                   [Ref: 2026-09-26 17:00] │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬────────────────────┤
│ Total Req    │ Active Cases │ Overdue      │ Approaching  │ SLA Breach % │ Avg Res Time │ Escalated / Apprv  │
│    150       │     50       │    24        │     0        │    12.0%     │  69.27 hrs   │  17 / 70 Cases     │
├──────────────┴──────────────┴──────────────┴──────────────┼──────────────┴──────────────┴────────────────────┤
│ Visual 1: Workload by Process Area (Bar Chart)             │ Visual 2: Active Backlog by Status (Donut Chart)  │
│ AML Ops: 41 total | Customer Onboard: 40 total             │ Under Review: 18 | Pending Approval: 8            │
│ KYC Ops: 36 total | Sanctions: 18 | Policy & Gov: 15       │ Submitted: 6 | Escalated: 6 | Approved: 5         │
├───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ Visual 3: Monthly Submission & Completion Trend            │ Visual 4: Risk Distribution & Executive Summary  │
│ [Line Chart: Submissions vs Completions over 90 days]     │ Medium: 55 (36.7%) | High: 45 (30.0%)            │
│                                                           │ Low: 32 (21.3%)    | Critical: 18 (12.0%)        │
│                                                           │ [Executive Insights Text Box]                    │
└───────────────────────────────────────────────────────────┴──────────────────────────────────────────────────┘
```

### 2.3 Visual Specifications

| Visual ID | Visual Type | Title | Data Fields / Measures | Positioning (X, Y, W, H) | Expected Baseline |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **P1-C1** | Card | Total Requests | `[Total Requests]` | `(20, 70, 160, 90)` | `150` |
| **P1-C2** | Card | Active Backlog | `[Active Backlog]` | `(190, 70, 160, 90)` | `50` |
| **P1-C3** | Card (Accent Red) | Overdue Cases | `[Overdue Cases]` | `(360, 70, 160, 90)` | `24` |
| **P1-C4** | Card | Approaching Deadline | `[Approaching Deadline Cases]` | `(530, 70, 160, 90)` | `0` |
| **P1-C5** | Card (Accent Red) | SLA Breach Rate | `[SLA Breach Rate]` | `(700, 70, 160, 90)` | `12.0%` |
| **P1-C6** | Card | Avg Resolution Time | `[Average Resolution Time]` | `(870, 70, 180, 90)` | `69.27 hrs` |
| **P1-C7** | Multi-row Card | Governance Triggers | `[Escalated Cases]`, `[Approval Required Cases]` | `(1060, 70, 200, 90)` | `17 Esc / 70 Appr` |
| **P1-V1** | Clustered Bar | Total Volume by Process Area | Y-Axis: `ProcessArea`, X-Axis: `[Total Requests]`, Legend: `Status` | `(20, 180, 600, 240)` | AML (41), Onboard (40), KYC (36) |
| **P1-V2** | Donut Chart | Active Backlog by Status | Legend: `Status`, Values: `[Active Backlog]` | `(640, 180, 620, 240)` | Under Review (18), Pending (8) |
| **P1-V3** | Line & Clustered Column | Workload Intake vs Output Trend | X-Axis: `DimDate[YearMonth]`, Columns: `[Total Requests]`, Line: `[Closed Requests]` | `(20, 440, 700, 260)` | 90-day intake velocity |
| **P1-V4** | Treemap / Bar | Total Requests by Risk Level | Category: `RiskLevel`, Values: `[Total Requests]` | `(740, 440, 260, 260)` | Medium (55), High (45), Low (32), Crit (18) |
| **P1-V5** | Text Box | Management Key Insights | Narrative summary of SLA exposure and pending approvals | `(1020, 440, 240, 260)` | Focus on 24 overdue cases |

---

## 3. Page 2 — Operational Workload

### 3.1 Purpose & Target Persona
Enables Operational Team Leads, Queue Managers, and Resource Planners to balance caseload across compliance teams, assess queue congestion, and reassign work before breaches occur.

### 3.2 Wireframe Layout (1280 x 720)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [SLICER BAR] Process Area | Risk Level | Request Type | Priority | Compliance Team | Status                  │
├───────────────────────────────────────────────────────────┬──────────────────────────────────────────────────┤
│ Visual 1: Active Backlog by Process Area (Bar Chart)       │ Visual 2: Active Backlog by Risk Level (Bar)     │
│ KYC: 17 | Customer Onboard: 13 | AML: 11                  │ Medium: 23 | Low: 12                             │
│ Policy & Gov: 5 | Sanctions: 4                            │ High: 8 | Critical: 7                            │
├───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ Visual 3: Active Cases by Compliance Team (Column Chart)  │ Visual 4: Backlog Matrix by Request Type & Status │
│ Team KYC: 17 | Team Onboarding: 13 | Team AML: 11         │ Matrix showing count of active cases per type    │
│ Team Governance: 5 | Team Sanctions: 4                    │ with row/column totals                           │
├───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ Visual 5: Active Backlog Priority Breakdown               │ Visual 6: Escalation & Approval Status Breakdown │
│ Medium: 23 | High: 15 | Urgent: 7 | Low: 5                │ Requires Approval: 23 | In Escalation: 6         │
└───────────────────────────────────────────────────────────┴──────────────────────────────────────────────────┘
```

### 3.3 Visual Specifications & Filter Matrix

* **Global Page Slicers (Top Ribbon: Y=50, H=50):**
  - Dropdown Slicer: `DimProcessArea[ProcessArea]`
  - Dropdown Slicer: `DimRisk[RiskLevel]`
  - Dropdown Slicer: `DimRequestType[RequestType]`
  - Dropdown Slicer: `DimComplianceTeam[ComplianceTeam]`
  - Dropdown Slicer: `DimStatus[Status]` (Default filtered to Active: New, Under Review, Pending Approval, Escalated)
* **Core Visuals:**
  1. **Active Backlog by Process Area (Horizontal Bar):** Highlights operational load. KYC (17) and Customer Onboarding (13) lead active queues.
  2. **Active Backlog by Risk Tier (Horizontal Bar):** Highlights High/Critical exposure (`[High/Critical Active Cases]` = 15).
  3. **Queue Distribution by Compliance Team (Column Chart):** Highlights analyst allocation and queue capacity.
  4. **Request Type Congestion Matrix:** Rows: `RequestType`, Columns: `Status`, Values: `[Active Backlog]`.
  5. **Priority Stacked Bar:** Distribution of Urgent, High, Medium, Low urgency among active cases.

---

## 4. Page 3 — SLA & Process Performance

### 4.1 Purpose & Target Persona
Aimed at Continuous Improvement Leads, Audit Readiness Officers, and Regulatory Compliance Heads evaluating resolution throughput, operational friction, and SLA compliance.

### 4.2 Wireframe Layout (1280 x 720)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [SLICER BAR] Date Range | Process Area | Risk Tier | Request Type                                            │
├─────────────────────────────┬─────────────────────────────┬──────────────────────────────────────────────────┤
│ SLA Met vs Breached (Donut) │ SLA Breach Rate by Area     │ SLA Breach Rate by Risk Tier (Bar)               │
│ Met: 88 (88%)               │ AML: 17.4% (4/23)           │ Critical: 27.3% (3/11)                           │
│ Breached: 12 (12%)          │ Customer Onboard: 13.6%     │ High: 17.6% (3/17) | Medium: 8.2% | Low: 4.3%    │
├─────────────────────────────┴─────────────────────────────┼──────────────────────────────────────────────────┤
│ Visual 4: Average Resolution Time by Process Area (Bar)    │ Visual 5: Resolution Time by Request Type (Bar)  │
│ AML: 80.12h | Sanctions: 75.29h | KYC: 67.57h             │ Suspicious Activity Report: 89.4h                │
│ Customer Onboarding: 64.67h | Policy & Gov: 60.77h        │ Enhanced Due Diligence: 76.2h                    │
├───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────┤
│ Visual 6: Resolution Time Distribution (Histogram / Range)│ Visual 7: Escalation & Governance Bottlenecks    │
│ 0-24h: 32 | 24-72h: 41 | 72-120h: 18 | >120h: 9           │ Scatter / Column: Avg Res Time vs Escalation %   │
└───────────────────────────────────────────────────────────┴──────────────────────────────────────────────────┘
```

### 4.3 Key Performance Distinction
> **Critical Design Requirement:** Closed-case historical metrics (`[SLA Breach Rate]`, `[Average Resolution Time]`) are calculated exclusively on resolved records (`Status = "Closed"`). Current active backlog metrics (`Status <> "Closed"`) are strictly excluded from these denominators to prevent skewed cycle times.

---

## 5. Page 4 — Case / Operational Detail (Triage Grid)

### 5.1 Purpose & Target Persona
Provides compliance analysts and queue supervisors with an actionable, filterable case ledger to triage overdue items, inspect audit history, and expedite escalated investigations.

### 5.2 Wireframe Layout (1280 x 720)

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [QUICK FILTERS] [Show Overdue Only (24)] [Show High/Critical (15)] [Show Escalated (6)] [Clear All]          │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Detailed Case Triage Table (Sorted by: Overdue Status DESC, TargetDueDateTime ASC)                          │
├───────────┬──────────────┬──────────────┬──────────┬──────────┬──────────────┬──────────────┬────────┬───────┤
│ RequestID │ Title        │ Process Area │ Risk     │ Priority │ Status       │ Analyst      │ Due    │ Flags │
├───────────┼──────────────┼──────────────┼──────────┼──────────┼──────────────┼──────────────┼────────┼───────┤
│ CR-00108  │ KYC Renew... │ KYC Ops      │ Critical │ Urgent   │ Under Review │ Sarah Chen   │ Sep 21 │ 🔴 OVER│
│ CR-00042  │ PEP Screen...│ Sanctions    │ High     │ High     │ Escalated    │ Alex Rivera  │ Sep 22 │ 🔴 ESC │
│ CR-00095  │ AML Trans... │ AML Ops      │ High     │ High     │ Pending Appr │ Marcus Vance │ Sep 23 │ 🔴 OVER│
│ ...       │ ...          │ ...          │ ...      │ ...      │ ...          │ ...          │ ...    │ ...   │
├───────────┴──────────────┴──────────────┴──────────┴──────────┴──────────────┴──────────────┴────────┴───────┤
│ Drill-through Target: Right-click any row -> Drill-through to "Request Audit History" page                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Case Detail Table Specifications

* **Visual Type:** Power BI Table Visual (Canvas: `(20, 110, 1240, 580)`)
* **Included Columns:**
  1. `FactComplianceRequests[RequestID]` (Width: 90px, Center-aligned)
  2. `FactComplianceRequests[Title]` (Width: 220px, Left-aligned)
  3. `FactComplianceRequests[RequestType]` (Width: 140px, Left-aligned)
  4. `FactComplianceRequests[ProcessArea]` (Width: 120px, Left-aligned)
  5. `FactComplianceRequests[RiskLevel]` (Width: 80px, Conditional color formatting)
  6. `FactComplianceRequests[Priority]` (Width: 80px, Center-aligned)
  7. `FactComplianceRequests[Status]` (Width: 110px, Badge style)
  8. `FactComplianceRequests[AssignedAnalyst]` (Width: 120px, Left-aligned)
  9. `FactComplianceRequests[SubmissionDateTime]` (Format: `YYYY-MM-DD HH:MM`, Width: 110px)
  10. `FactComplianceRequests[TargetDueDateTime]` (Format: `YYYY-MM-DD HH:MM`, Width: 110px)
  11. `FactComplianceRequests[CompletionDateTime]` (Format: `YYYY-MM-DD HH:MM`, Width: 110px)
  12. `FactComplianceRequests[SLABreachFlag]` (Icon: Green Check if 0, Red Alert if 1)
  13. `FactComplianceRequests[EscalationFlag]` (Icon: Warning Flag if 1)
  14. `FactComplianceRequests[ApprovalRequired]` (Icon: Lock/Key if 1)
* **Default Sorting Rule:**
  - Primary Sort: `TargetDueDateTime` Ascending (surfaces earliest overdue cases at the top).
* **Conditional Formatting Rules:**
  - `RiskLevel`: Critical = Soft Red background (`#FADBD8`), High = Soft Amber (`#FDEBD0`), Medium/Low = Transparent.
  - `Status`: Overdue rows highlighted with light red left-border accent.

---

## 6. Interaction & Drill-Through Design

1. **Cross-Filtering & Highlighting:**
   - Clicking any bar in Page 1 Visual 1 (`ProcessArea`) cross-filters the donut chart and monthly trend to that specific division.
   - Slicers across all pages are synchronized using Power BI **Sync Slicers** for `ProcessArea`, `RiskLevel`, and `ComplianceTeam`.
2. **Drill-Through Capability:**
   - From any visual referencing `RequestID` on Page 1, 2, or 4, users can right-click and select **Drill-through -> Request Audit History**.
   - Filters the `FactAuditLog` table on the target hidden drill-through page, displaying all state transitions, user actors, and timestamps for that individual case.
3. **Reset Slicers Button:**
   - Configured in the upper right header using a Power BI Bookmark action that restores all slicers to their default unfiltered state.
