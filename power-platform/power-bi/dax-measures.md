# ComplyFlow DAX Measure Catalogue & Calculation Reference

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Microsoft Power BI DAX Calculation Engine
**Phase:** 6 (Executive Analytics & DAX Modelling)
**Status:** Validated Calculation Specification

---

## 1. Overview & Measure Governance

All business intelligence calculations in the ComplyFlow Power BI data model are governed centrally to prevent conflicting business logic across reports.

### Modeling Guidelines
1. **Dedicated Measure Table:** All explicit measures are organized within a dedicated calculation container table named `_Measures`.
2. **Current-State vs. Historical Segregation:** Current active backlog metrics (e.g., `[Active Backlog]`, `[Overdue Cases]`) are strictly separated from historical completion metrics (e.g., `[SLA Breach Rate]`, `[Average Resolution Time]`). Visuals must never blend these without explicit visual labeling.
3. **Simulation Anchor vs. Live Production Timestamp:**
   - **Simulation Baseline (Verified):** The synthetic dataset is anchored to a reproducible reference point: `2026-09-26 17:00:00`.
   - **Production Real-Time Mode:** In a live Power BI Service environment with scheduled refresh, the DAX expressions replace the fixed anchor constant with `NOW()` or `UTCNOW()`. This is documented in Section 4.
4. **Alignment with SQLite Analytical Views:** All measures follow the exact conditions established in `database/queries/analytics_views.sql` (`vw_request_performance` and `vw_active_backlog`), where completed records are identified by `Status = "Closed"` and active backlog records by `Status <> "Closed"`.

---

## 2. Core Measure Catalogue

### 2.1 Volume & Workload Measures

#### [Total Requests]
* **Category:** Operational Volume
* **Scope / Type:** Historical & Current Aggregate
* **DAX Expression:**
```dax
Total Requests =
COUNTROWS(FactComplianceRequests)
```
* **Business Meaning:** Total volume of compliance requests submitted into ComplyFlow across all time and all statuses.
* **Expected Value (Full Dataset):** `150`
* **Filtering Context:** Fully sliceable by `DimDate`, `DimProcessArea`, `DimRisk`, `DimStatus`, and `DimComplianceTeam`.

---

#### [Closed Requests]
* **Category:** Operational Volume
* **Scope / Type:** Historical Only
* **DAX Expression:**
```dax
Closed Requests =
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[Status] = "Closed"
)
```
* **Business Meaning:** Cumulative count of finalized compliance cases that have exited active workflow processing and completed their lifecycle.
* **Expected Value (Full Dataset):** `100`
* **Alignment:** Directly mirrors SQLite view `vw_request_performance WHERE Status = 'Closed'`.

---

#### [Active Backlog]
* **Category:** Operational Workload
* **Scope / Type:** Current-State Only
* **DAX Expression:**
```dax
Active Backlog =
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[Status] <> "Closed"
)
```
* **Business Meaning:** Real-time operational backlog of cases currently in progress and requiring compliance team action.
* **Expected Value (Full Dataset):** `50`
* **Breakdown by Status:** `Under Review` = 18, `Pending Approval` = 8, `Submitted` = 6, `Escalated` = 6, `Approved` = 5, `Draft` = 4, `Rejected` = 3.

---

### 2.2 Active SLA & Urgency Measures

#### [Overdue Cases]
* **Category:** Operational Risk & Urgency
* **Scope / Type:** Current-State Only
* **DAX Expression (Simulation Anchor):**
```dax
Overdue Cases =
VAR ReferenceNow = DATETIME(2026, 9, 26, 17, 0, 0)
RETURN
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[Status] <> "Closed",
    FactComplianceRequests[TargetDueDateTime] < ReferenceNow
)
```
* **Business Meaning:** Active backlog cases whose contractual or regulatory SLA deadline has passed relative to the evaluation anchor.
* **Expected Value (Full Dataset):** `24`
* **Operational Significance:** Highest immediate triage priority. Represents 48.0% of the active backlog. Mirrors `vw_active_backlog WHERE SLAState = 'Overdue'`.

---

#### [Approaching Deadline Cases]
* **Category:** Operational Risk & Urgency
* **Scope / Type:** Current-State Only
* **DAX Expression (Simulation Anchor):**
```dax
Approaching Deadline Cases =
VAR ReferenceNow = DATETIME(2026, 9, 26, 17, 0, 0)
RETURN
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[Status] <> "Closed",
    FactComplianceRequests[TargetDueDateTime] >= ReferenceNow,
    FactComplianceRequests[TargetDueDateTime] <= ReferenceNow + (RELATED(DimSLAPolicy[WarningThresholdHours]) / 24)
)
```
* **Business Meaning:** Active backlog cases that have not yet breached SLA, but whose remaining time before deadline is within the risk tier's configured warning threshold.
* **Expected Value (Full Dataset):** `0`
* **Operational Significance:** Identifies cases nearing risk thresholds to prevent impending regulatory breaches. Mirrors `vw_active_backlog WHERE SLAState = 'Approaching Deadline'`.

---

#### [On Track Cases]
* **Category:** Operational Workload
* **Scope / Type:** Current-State Only
* **DAX Expression (Simulation Anchor):**
```dax
On Track Cases =
[Active Backlog] - [Overdue Cases] - [Approaching Deadline Cases]
```
* **Business Meaning:** Active backlog cases progressing safely within their allotted SLA window with ample remaining buffer.
* **Expected Value (Full Dataset):** `26`
* **Operational Significance:** Cases operating normally without immediate escalation triggers. Mirrors `vw_active_backlog WHERE SLAState = 'On Track'`.

---

#### [High/Critical Active Cases]
* **Category:** Risk Management
* **Scope / Type:** Current-State Only
* **DAX Expression:**
```dax
High/Critical Active Cases =
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[Status] <> "Closed",
    FactComplianceRequests[RiskLevel] IN {"High", "Critical"}
)
```
* **Business Meaning:** Active backlog cases designated as High or Critical risk requiring senior oversight or expedited analyst handling.
* **Expected Value (Full Dataset):** `15` (`Critical` = 7, `High` = 8)

---

### 2.3 Historical SLA Performance Measures

#### [SLA Met Cases]
* **Category:** SLA Compliance
* **Scope / Type:** Historical Only
* **DAX Expression:**
```dax
SLA Met Cases =
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[Status] = "Closed",
    FactComplianceRequests[SLABreachFlag] = 0
)
```
* **Business Meaning:** Completed cases finalized within the mandatory SLA target window.
* **Expected Value (Full Dataset):** `88`

---

#### [SLA Breached Cases]
* **Category:** SLA Compliance
* **Scope / Type:** Historical Only
* **DAX Expression:**
```dax
SLA Breached Cases =
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[Status] = "Closed",
    FactComplianceRequests[SLABreachFlag] = 1
)
```
* **Business Meaning:** Completed cases whose resolution timestamp exceeded the target due date/time.
* **Expected Value (Full Dataset):** `12`

---

#### [SLA Breach Rate]
* **Category:** SLA Compliance
* **Scope / Type:** Historical KPI
* **DAX Expression:**
```dax
SLA Breach Rate =
DIVIDE(
    [SLA Breached Cases],
    [Closed Requests],
    0
)
```
* **Business Meaning:** Percentage of completed requests that failed to meet their SLA deadline.
* **Expected Value (Full Dataset):** `12.0%` (Format: `0.0%`)
* **Target Benchmark:** `< 5.0%`

---

#### [SLA Compliance Rate]
* **Category:** SLA Compliance
* **Scope / Type:** Historical KPI
* **DAX Expression:**
```dax
SLA Compliance Rate =
DIVIDE(
    [SLA Met Cases],
    [Closed Requests],
    0
)
```
* **Business Meaning:** Percentage of completed requests successfully finalized on time.
* **Expected Value (Full Dataset):** `88.0%` (Format: `0.0%`)

---

### 2.4 Resolution Efficiency & Duration Measures

#### [Average Resolution Time]
* **Category:** Operational Efficiency
* **Scope / Type:** Historical KPI
* **DAX Expression:**
```dax
Average Resolution Time =
CALCULATE(
    AVERAGE(FactComplianceRequests[ResolutionTimeHours]),
    FactComplianceRequests[Status] = "Closed"
)
```
* **Business Meaning:** Arithmetic mean time in decimal hours required to resolve completed compliance requests.
* **Expected Value (Full Dataset):** `69.27 hours` (Format: `#,##0.00 "hrs"`)
* **Process Area Breakdown (Closed Cases):**
  - `AML Operations`: `80.12 hrs` (30 closed cases)
  - `Sanctions`: `77.19 hrs` (14 closed cases)
  - `Customer Onboarding`: `67.89 hrs` (27 closed cases)
  - `KYC Operations`: `55.70 hrs` (19 closed cases)
  - `Policy & Governance`: `55.19 hrs` (10 closed cases)

---

#### [Median Resolution Time]
* **Category:** Operational Efficiency
* **Scope / Type:** Historical KPI
* **DAX Expression:**
```dax
Median Resolution Time =
CALCULATE(
    MEDIAN(FactComplianceRequests[ResolutionTimeHours]),
    FactComplianceRequests[Status] = "Closed"
)
```
* **Business Meaning:** Median resolution time in decimal hours. Unlike the arithmetic mean, this metric is resilient against extreme outlier cases (e.g., complex multi-week investigations).
* **Expected Value (Full Dataset):** `44.79 hours` (Format: `#,##0.00 "hrs"`)
* **Verification Note:** In SQLite (which does not provide a native `MEDIAN()` aggregate function), the verified 44.79-hour median was calculated from ordered closed-case resolution values using Python (`statistics.median`), whereas Power BI natively computes it via the DAX `MEDIAN()` function over `ResolutionTimeHours`.

---

#### [Min Resolution Time] & [Max Resolution Time]
* **Category:** Statistical Range
* **Scope / Type:** Historical
* **DAX Expressions:**
```dax
Min Resolution Time =
CALCULATE(
    MIN(FactComplianceRequests[ResolutionTimeHours]),
    FactComplianceRequests[Status] = "Closed"
)

Max Resolution Time =
CALCULATE(
    MAX(FactComplianceRequests[ResolutionTimeHours]),
    FactComplianceRequests[Status] = "Closed"
)
```
* **Expected Values (Full Dataset):** Min = `4.50 hrs`, Max = `304.32 hrs`

---

### 2.5 Governance, Escalation & Workflow Measures

#### [Escalated Cases]
* **Category:** Workflow Governance
* **Scope / Type:** Historical & Current Aggregate
* **DAX Expression:**
```dax
Escalated Cases =
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[EscalationFlag] = 1
)
```
* **Business Meaning:** Total count of requests that required management escalation during their lifecycle.
* **Expected Value (Full Dataset):** `17` (11.3% of all requests)

---

#### [Active Escalated Cases]
* **Category:** Workflow Governance
* **Scope / Type:** Current-State Only
* **DAX Expression:**
```dax
Active Escalated Cases =
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[Status] = "Escalated"
)
```
* **Business Meaning:** Active requests currently sitting in the Escalated queue awaiting senior leadership sign-off or remediation.
* **Expected Value (Full Dataset):** `6`

---

#### [Approval Required Cases]
* **Category:** Workflow Governance
* **Scope / Type:** Historical & Current Aggregate
* **DAX Expression:**
```dax
Approval Required Cases =
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[ApprovalRequired] = 1
)
```
* **Business Meaning:** Total requests requiring mandatory two-tier governance sign-off prior to closure.
* **Expected Value (Full Dataset):** `70` (46.7% of all requests)

---

#### [Pending Approval Cases]
* **Category:** Workflow Governance
* **Scope / Type:** Current-State Only
* **DAX Expression:**
```dax
Pending Approval Cases =
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[Status] = "Pending Approval"
)
```
* **Business Meaning:** Active cases where investigation has concluded and formal compliance sign-off is pending.
* **Expected Value (Full Dataset):** `8`

---

## 3. Measure Mapping to SQLite Analytical Views

To ensure architectural alignment and single-source-of-truth governance, every Power BI measure directly mirrors verified SQL logic:

| Power BI Measure | Source Table / SQLite View | Underlying SQL Logic | Verified Baseline Value |
| :--- | :--- | :--- | :--- |
| `[Total Requests]` | `ComplianceRequest` | `COUNT(*)` | `150` |
| `[Closed Requests]` | `vw_request_performance` | `COUNT(*) WHERE Status = 'Closed'` | `100` |
| `[Active Backlog]` | `vw_active_backlog` | `COUNT(*) WHERE Status != 'Closed'` | `50` |
| `[Overdue Cases]` | `vw_active_backlog` | `SUM(is_overdue)` relative to `2026-09-26 17:00:00` | `24` |
| `[Approaching Deadline Cases]`| `vw_active_backlog` | `SUM(is_approaching)` relative to threshold | `0` |
| `[On Track Cases]` | `vw_active_backlog` | `COUNT(*) - SUM(is_overdue) - SUM(is_approaching)` | `26` |
| `[SLA Breached Cases]` | `vw_request_performance` | `SUM(SLABreachFlag)` | `12` |
| `[SLA Breach Rate]` | `vw_request_performance` | `ROUND(AVG(SLABreachFlag) * 100.0, 2)` | `12.0%` |
| `[Average Resolution Time]` | `vw_request_performance` | `ROUND(AVG(ResolutionTimeHours), 2)` | `69.27 hrs` |
| `[Escalated Cases]` | `ComplianceRequest` | `SUM(EscalationFlag)` | `17` |
| `[Approval Required Cases]` | `ComplianceRequest` | `SUM(ApprovalRequired)` | `70` |
| `[High/Critical Active Cases]`| `vw_active_backlog` | `COUNT(*) WHERE RiskLevel IN ('High', 'Critical')` | `15` |

---

## 4. Production Real-Time Implementation Considerations

In a live production Power BI Service deployment connected to SharePoint Online or Azure SQL, the fixed anchor variable in `[Overdue Cases]` and `[Approaching Deadline Cases]` should be converted to dynamic system time:

```dax
-- Dynamic Production DAX Pattern
Overdue Cases (Live Production) =
VAR CurrentTime = NOW()
RETURN
CALCULATE(
    COUNTROWS(FactComplianceRequests),
    FactComplianceRequests[Status] <> "Closed",
    FactComplianceRequests[TargetDueDateTime] < CurrentTime
)
```

> **Warning:** When testing against the Phase 2B verified synthetic dataset, developers **must** use the static anchor timestamp `DATETIME(2026, 9, 26, 17, 0, 0)` so that expected KPI card values match verified SQLite counts exactly.
