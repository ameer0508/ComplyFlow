# ComplyFlow Power BI Desktop Build Specification & Implementation Guide

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Microsoft Power BI Desktop Implementation Guide
**Phase:** 6 (Executive Analytics & DAX Modelling)
**Status:** Build-Ready Manual Implementation Specification

---

## 1. Overview & Setup Prerequisites

This specification serves as the step-by-step developer guide for assembling the **ComplyFlow Compliance Management Dashboard** in Power BI Desktop.

### Prerequisites
* **Power BI Desktop:** Version 2.128+ (Optimized for 64-bit Windows).
* **Data Sources (Local Development):**
  - Option A: Direct SQLite ODBC Driver connection to `database/complyflow.db`.
  - Option B (Recommended for maximum portability): Curated CSV data extracts from Phase 2B located in `data/raw/`.
* **Verified Row Counts:**
  - `ComplianceRequest`: 150 records
  - `RequestAuditLog`: 716 records
  - `SLAPolicy`: 4 records

---

## 2. Step 1: Data Ingestion & Power Query (M) Preparation

### 2.1 Ingesting Core Tables (Power Query)

1. Launch Power BI Desktop and select **Get Data -> Text/CSV** (or **ODBC** for SQLite).
2. Load the three core tables:
   - `FactComplianceRequests` (from `compliance_requests.csv` or `ComplianceRequest` table)
   - `FactAuditLog` (from `request_audit_log.csv` or `RequestAuditLog` table)
   - `DimSLAPolicy` (from `sla_policies.csv` or `SLAPolicy` table)

### 2.2 Applied Steps & Type Enforcements (Power Query M)

Ensure data types are explicitly cast to prevent implicit type conversion errors in DAX:

```powerquery
// FactComplianceRequests Data Types
let
    Source = Csv.Document(File.Contents("data/raw/compliance_requests.csv"),[Delimiter=",", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders,{
        {"RequestID", type text},
        {"Title", type text},
        {"RequestType", type text},
        {"ProcessArea", type text},
        {"RiskLevel", type text},
        {"Priority", type text},
        {"Status", type text},
        {"AssignedAnalyst", type text},
        {"ComplianceTeam", type text},
        {"SubmissionDateTime", type datetime},
        {"TargetDueDateTime", type datetime},
        {"CompletionDateTime", type datetime},
        {"SLATargetHours", Int64.Type},
        {"SLABreachFlag", Int64.Type},
        {"ApprovalRequired", Int64.Type},
        {"EscalationFlag", Int64.Type}
    }),
    AddedDateKey = Table.AddColumn(ChangedTypes, "SubmissionDate", each DateTime.Date([SubmissionDateTime]), type date)
in
    AddedDateKey
```

```powerquery
// FactAuditLog Data Types
let
    Source = Csv.Document(File.Contents("data/raw/request_audit_log.csv"),[Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangedTypes = Table.TransformColumnTypes(PromotedHeaders,{
        {"AuditID", Int64.Type},
        {"RequestID", type text},
        {"Timestamp", type datetime},
        {"ActionType", type text},
        {"PerformedBy", type text},
        {"OldStatus", type text},
        {"NewStatus", type text}
    })
in
    ChangedTypes
```

### 2.3 Creating the Date Dimension (`DimDate`)

Create a calculated calendar table using DAX to support standard time-intelligence:

```dax
DimDate =
VAR MinDate = DATE(2026, 6, 1)
VAR MaxDate = DATE(2026, 10, 31)
RETURN
ADDCOLUMNS(
    CALENDAR(MinDate, MaxDate),
    "Year", YEAR([Date]),
    "MonthNumber", MONTH([Date]),
    "MonthName", FORMAT([Date], "MMMM"),
    "MonthShort", FORMAT([Date], "mmm"),
    "YearMonth", FORMAT([Date], "YYYY-MM"),
    "Quarter", "Q" & FORMAT([Date], "Q"),
    "DayOfWeek", FORMAT([Date], "dddd")
)
```

---

## 3. Step 2: Data Modeling & Relationship Topology

Switch to the **Model View** in Power BI Desktop and configure the relationships:

### 3.1 Relationship Configuration

1. **`DimDate` to `FactComplianceRequests`:**
   - From: `DimDate[Date]`
   - To: `FactComplianceRequests[SubmissionDate]`
   - Cardinality: **1 to Many (1:*)**
   - Cross filter direction: **Single**
   - Make relationship active: **Yes**

2. **`DimSLAPolicy` to `FactComplianceRequests`:**
   - From: `DimSLAPolicy[RiskLevel]`
   - To: `FactComplianceRequests[RiskLevel]`
   - Cardinality: **1 to Many (1:*)**
   - Cross filter direction: **Single**
   - Make relationship active: **Yes**

3. **`FactComplianceRequests` to `FactAuditLog`:**
   - From: `FactComplianceRequests[RequestID]`
   - To: `FactAuditLog[RequestID]`
   - Cardinality: **1 to Many (1:*)**
   - Cross filter direction: **Single**
   - Make relationship active: **Yes**

### 3.2 Calculated Column for Resolution Duration
In `FactComplianceRequests`, add the resolution duration in decimal hours (matching the verified SQLite logic):

```dax
ResolutionTimeHours =
IF(
    NOT ISBLANK(FactComplianceRequests[CompletionDateTime]),
    ROUND(
        (FactComplianceRequests[CompletionDateTime] - FactComplianceRequests[SubmissionDateTime]) * 24,
        2
    ),
    BLANK()
)
```

---

## 4. Step 3: DAX Measure Implementation

1. Select **Enter Data** and create an empty table named `_Measures`.
2. Delete the default empty column after creating your first measure.
3. Author the complete measure suite as specified in [dax-measures.md](dax-measures.md):
   - `[Total Requests]`
   - `[Closed Requests]`
   - `[Active Backlog]`
   - `[Overdue Cases]`
   - `[Approaching Deadline Cases]`
   - `[On Track Cases]`
   - `[High/Critical Active Cases]`
   - `[SLA Met Cases]`
   - `[SLA Breached Cases]`
   - `[SLA Breach Rate]`
   - `[Average Resolution Time]`
   - `[Median Resolution Time]`
   - `[Escalated Cases]`
   - `[Approval Required Cases]`

---

## 5. Step 4: Report Page Construction

Construct the four report pages adhering to the coordinates and specifications in [report-layout.md](report-layout.md):

* **Page 1: Executive Compliance Overview**
  - Add top KPI banner (7 cards: Total, Active Backlog, Overdue, Approaching, SLA Breach %, Avg Res Time, Escalated/Appr).
  - Add Bar Chart: Workload by Process Area.
  - Add Donut Chart: Active Backlog by Status.
  - Add Trend Chart: Intake vs Completion velocity over 90 days.
  - Add Risk distribution treemap and executive summary callout.
* **Page 2: Operational Workload**
  - Add top Slicer Ribbon (Process Area, Risk Level, Request Type, Priority, Team).
  - Add Bar Charts for Backlog by Process Area, Risk Level, and Team.
  - Add Request Type vs Status congestion matrix.
* **Page 3: SLA & Process Performance**
  - Add SLA Met vs Breached Donut Chart.
  - Add SLA Breach Rate by Process Area and Risk Tier.
  - Add Average Resolution Time by Process Area and Request Type.
  - Add resolution duration distribution histogram.
* **Page 4: Case / Operational Detail**
  - Add quick action filter buttons (Overdue, High/Critical, Escalated).
  - Add the 14-column granular Case Detail Table.
  - Configure default sort: `TargetDueDateTime` Ascending.
  - Configure conditional background color formatting for `RiskLevel` and overdue alerts.

---

## 6. Step 5: Drill-Through & Interactivity

1. **Create Drill-Through Page:**
   - Create a hidden page named `Request Audit History`.
   - In the Visualizations pane, add `FactComplianceRequests[RequestID]` to the **Drill-through fields** bucket.
   - Insert a table containing: `FactAuditLog[Timestamp]`, `FactAuditLog[ActionType]`, `FactAuditLog[PerformedBy]`, `FactAuditLog[OldStatus]`, `FactAuditLog[NewStatus]`.
2. **Configure Sync Slicers:**
   - In the **View -> Sync Slicers** pane, synchronize `DimProcessArea[ProcessArea]` and `DimRisk[RiskLevel]` across Pages 1, 2, and 3.
3. **Configure Reset Button:**
   - Create a bookmark with all filters cleared.
   - Add a "Reset Filters" icon button on Page 2 and 3 mapped to this bookmark.

---

## 7. Step 6: Role-Level Security (RLS) Specification

To protect operational team boundaries in an enterprise rollout, define the following RLS roles:

```dax
// Role: AML Analysts
FactComplianceRequests[ComplianceTeam] = "AML Operations Team"

// Role: KYC Analysts
FactComplianceRequests[ComplianceTeam] = "KYC Review Team"

// Role: Onboarding Team
FactComplianceRequests[ComplianceTeam] = "Onboarding Compliance Team"

// Role: Compliance Management & Audit
// No filter expression (Unrestricted view of all records)
```

---

## 8. Refresh & Gateway Configuration Scenarios

| Environment | Data Storage | Connector Type | Gateway Required | Scheduled Refresh Support |
| :--- | :--- | :--- | :--- | :--- |
| **Local Prototype (Current)** | SQLite (`complyflow.db`) / CSV | Folder / Local File / ODBC | Yes (On-premises) | Manual Only (No live Power BI Service) |
| **SharePoint Operational** | SharePoint Online Lists | SharePoint Online List Connector | No (Cloud native) | Up to 8x daily (Power BI Pro) |
| **Enterprise Azure SQL** | Azure SQL Database | Azure SQL Connector | No (Cloud native) | Scheduled or DirectQuery |
