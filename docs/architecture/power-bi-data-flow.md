# Power BI Analytical Data Flow & Pipeline Architecture

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** End-to-End Analytical Data Pipeline & Reporting Architecture
**Phase:** 6 Architecture Integration
**Status:** Validated Technical Architecture Specification

---

## 1. End-to-End Analytical Architecture

The ComplyFlow reporting solution bridges transactional compliance workflows with executive decision support. It consumes governed operational data from the transactional layer, shapes it via a dimensional star-schema model, and surfaces interactive insights through four specialized report pages:

```mermaid
flowchart TD
    subgraph OperationalLayer["Operational & Transactional Tier"]
        PA["Power Apps Canvas App"] -->|Patch / Create / Update| SP_REQ["SharePoint: ComplianceRequests"]
        PA -->|Event Audit| SP_AUD["SharePoint: RequestAuditLog"]
        SP_POL["SharePoint: SLAPolicies"]
        FLOW["Power Automate Cloud Flows"] -->|Background Logging| SP_AUD
    end

    subgraph AnalyticalDataTier["Analytical & Storage Foundation"]
        SQL_REQ["SQLite: ComplianceRequest<br/>(150 rows)"]
        SQL_AUD["SQLite: RequestAuditLog<br/>(716 rows)"]
        SQL_POL["SQLite: SLAPolicy<br/>(4 rows)"]

        SQL_VIEWS["Analytical Views<br/>• vw_request_performance<br/>• vw_active_backlog<br/>• vw_process_area_performance<br/>• vw_risk_performance"]

        SQL_REQ --> SQL_VIEWS
        SQL_AUD --> SQL_VIEWS
        SQL_POL --> SQL_VIEWS
    end

    subgraph PowerBIModel["Power BI Desktop (Star Schema Engine)"]
        PQ["Power Query (M) Data Shaping<br/>• Schema Validation<br/>• Date Key Extraction<br/>• Typing Enforcements"]

        DIM_DATE["DimDate<br/>(Calendar DAX)"]
        DIM_SLA["DimSLAPolicy<br/>(4 rows)"]
        FACT_REQ["FactComplianceRequests<br/>(150 rows)"]
        FACT_AUD["FactAuditLog<br/>(716 rows)"]
        MEASURES["_Measures Container<br/>(14+ Centralized DAX Measures)"]

        PQ --> FACT_REQ
        PQ --> FACT_AUD
        PQ --> DIM_SLA

        DIM_DATE -->|1:Many (SubmissionDate)| FACT_REQ
        DIM_SLA -->|1:Many (RiskLevel)| FACT_REQ
        FACT_REQ -->|1:Many (RequestID)| FACT_AUD
        MEASURES -.-> FACT_REQ
    end

    subgraph PresentationLayer["Presentation Tier (4-Page Executive Report)"]
        P1["Page 1: Executive Overview<br/>• KPI Cards (150 Total, 50 Active, 24 Overdue)<br/>• Intake vs Output Trend<br/>• Process Area Volume"]
        P2["Page 2: Operational Workload<br/>• Backlog by Process Area & Risk<br/>• Queue by Compliance Team<br/>• Congestion Matrix"]
        P3["Page 3: SLA & Performance<br/>• Met vs Breached (88% vs 12%)<br/>• Avg Cycle Time (69.27 hrs)<br/>• Bottleneck Distribution"]
        P4["Page 4: Case Detail Triage<br/>• 14-Column Actionable Grid<br/>• Overdue & High-Risk Sorting<br/>• Right-Click Audit Drill-Through"]

        FACT_REQ --> P1
        FACT_REQ --> P2
        FACT_REQ --> P3
        FACT_REQ --> P4
        FACT_AUD --> P4
    end

    SP_REQ -.->|Future Cloud Sync / Gateway| PQ
    SQL_REQ -->|Local Prototype Ingestion| PQ
    SQL_AUD -->|Local Prototype Ingestion| PQ
    SQL_POL -->|Local Prototype Ingestion| PQ
```

---

## 2. Ingestion & Transformation Responsibilities

To maintain optimal reporting performance and prevent duplicated business logic, computational responsibilities are layered across the stack:

| Responsibility Layer | Tool / Mechanism | Transformations Handled | Examples |
| :--- | :--- | :--- | :--- |
| **Source of Truth** | SQLite / SharePoint | Transactional integrity, ACID enforcement, operational audit trail | Raw dates, status codes, analyst assignment |
| **Curated SQL Views** | SQLite Engine | Heavy joins, aggregate verification, analytical baseline validation | `vw_request_performance`, `vw_active_backlog` |
| **Data Ingestion (ETL)** | Power Query (M) | Type casting, column renaming, null handling, key extraction | `SubmissionDate = DateTime.Date([SubmissionDateTime])` |
| **Model Relationships** | VertiPaq Engine | Cross-table star-schema filtering | 1:Many relationships from `DimDate` and `DimSLAPolicy` |
| **Business Logic** | DAX Engine | Dynamic multi-dimensional filtering, KPI evaluation, ratios | `[SLA Breach Rate]`, `[Overdue Cases]`, `[Active Backlog]` |

---

## 3. Data Refresh Pathways & Network Topologies

### Scenario A: Local Development & Verification (Current State)
* **Data Origin:** Local SQLite database (`database/complyflow.db`) and CSV files (`data/raw/`).
* **Connection Method:** Local Power BI Desktop file import / ODBC connector.
* **Latency:** Instantaneous manual reload on developer request.
* **Authentication:** Local filesystem security.
* **Deployment Status:** 🟢 Verified in local environment.

### Scenario B: Cloud M365 / SharePoint Operational Sync (Production Candidate)
* **Data Origin:** SharePoint Online lists (`ComplianceRequests`, `RequestAuditLog`, `SLAPolicies`).
* **Connection Method:** Native Power BI SharePoint Online List Connector (`v2.0` implementation).
* **Gateway Requirement:** None (Cloud-to-Cloud connectivity within Microsoft 365 tenant boundary).
* **Refresh Frequency:** Scheduled cloud refresh up to 8 times daily (Power BI Pro) or 48 times daily (Power BI Premium).
* **Deployment Status:** 🟡 Designed and specified; pending tenant provisioning.

### Scenario C: Enterprise Scaled Architecture (Azure SQL / Fabric)
* **Data Origin:** Azure SQL Database / Microsoft Fabric OneLake Lakehouse.
* **Connection Method:** Azure SQL Connector / Direct Lake / DirectQuery.
* **Latency:** Near real-time / sub-second telemetry.
* **Security:** Entra ID authentication with Row-Level Security (RLS) enforcement.
* **Deployment Status:** 🟡 Future enterprise scale option.

---

## 4. Alignment Between SQL Analytical Views and Power BI Model

A foundational requirement of ComplyFlow's architecture is that Power BI metrics must mirror the verified SQLite analytical views rather than inventing independent rules:

```
[ SQLite Analytical Layer ]                      [ Power BI Analytical Model ]
vw_request_performance                       --> FactComplianceRequests + DAX
  ├── SUM(SLABreachFlag)                     --> [SLA Breached Cases] (12)
  ├── AVG(SLABreachFlag) * 100.0             --> [SLA Breach Rate] (12.0%)
  └── AVG(ResolutionTimeHours)               --> [Average Resolution Time] (69.27 hrs)

vw_active_backlog                            --> FactComplianceRequests + Anchor DAX
  ├── COUNT(*)                               --> [Active Backlog] (50)
  ├── SUM(is_overdue)                        --> [Overdue Cases] (24)
  ├── SUM(is_approaching)                    --> [Approaching Deadline Cases] (0)
  └── COUNT(*) - Overdue - Approaching       --> [On Track Cases] (26)

ComplianceRequest Base Table                 --> FactComplianceRequests + DAX
  ├── COUNT(*)                               --> [Total Requests] (150)
  ├── SUM(EscalationFlag)                    --> [Escalated Cases] (17)
  └── SUM(ApprovalRequired)                  --> [Approval Required Cases] (70)
```

---

## 5. Security & Governance Architecture

1. **Analytical Segregation:** Read-only access to analytical views guarantees that reporting queries never lock or mutate transactional records in SQLite or SharePoint.
2. **Data Consistency:** Because the Power BI star-schema uses identical business rules to the SQLite views, audit committees and operational staff see identical figures regardless of which tool produces the summary.
3. **Auditing Traceability:** Power BI report users can drill down from any aggregated visual directly to granular case audit trails (`FactAuditLog`), providing end-to-end regulatory defensibility.
