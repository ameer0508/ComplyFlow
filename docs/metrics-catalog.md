# ComplyFlow — Governed Metrics Catalogue & Mathematical Definitions

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** Authoritative Operational Metrics, DAX Expressions & SQL Business Rules
**Status:** Validated Single Source of Truth

---

## 1. Metric Governance Principles

To eliminate reporting discrepancies across dashboards, SQL queries, and conversational AI answers, all operational calculations in ComplyFlow are centrally governed:

1. **Strict Temporal Segregation:** Historical completion metrics (e.g., SLA breach rates, average resolution times) apply **exclusively** to finalized cases (`Status = 'Closed'`). Current-state backlog metrics (e.g., overdue cases, approaching deadlines) apply **exclusively** to open cases (`Status <> 'Closed'`).
2. **Simulation Anchor vs. Live Clock:**
   - **Baseline Evaluation Timestamp:** For local verification and reproducible testing, all active SLA urgency metrics are evaluated against a fixed simulation anchor: `2026-09-26 17:00:00`.
   - **Production Real-Time Mode:** In a deployed cloud environment with scheduled refresh, the fixed timestamp is replaced with dynamic `NOW()` / `UTCNOW()` with regional timezone offsets.
3. **Median Computation Clarification:** In SQLite (which does not provide a native `MEDIAN()` aggregate function), the verified 44.79-hour median cycle time was calculated from ordered closed-case arrays via Python (`statistics.median`), whereas Power BI calculates it natively using the DAX `MEDIAN()` function over `ResolutionTimeHours`.

---

## 2. Authoritative Metrics Directory

### 2.1 Operational Volume Metrics

#### Total Requests
* **Definition:** Cumulative count of all compliance requests submitted to the platform across all time and all workflow statuses.
* **Scope / Temporal Mode:** Aggregate (All Records)
* **Authoritative Source:** `ComplianceRequest` (SQLite) / `FactComplianceRequests` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM ComplianceRequest;` / `COUNTROWS(FactComplianceRequests)`
* **Verified Baseline Value:** **`150`**

---

#### Closed Requests
* **Definition:** Count of finalized compliance requests that have completed their investigative lifecycle and exited active queue processing.
* **Scope / Temporal Mode:** Historical Only
* **Authoritative Source:** `vw_request_performance` (SQLite) / `[Closed Requests]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM ComplianceRequest WHERE Status = 'Closed';` / `CALCULATE(COUNTROWS(FactComplianceRequests), FactComplianceRequests[Status] = "Closed")`
* **Verified Baseline Value:** **`100`**

---

#### Active Backlog
* **Definition:** Real-time count of compliance requests currently in progress across active workflow stages requiring operational attention.
* **Scope / Temporal Mode:** Current-State Only
* **Authoritative Source:** `vw_active_backlog` (SQLite) / `[Active Backlog]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM ComplianceRequest WHERE Status != 'Closed';` / `CALCULATE(COUNTROWS(FactComplianceRequests), FactComplianceRequests[Status] <> "Closed")`
* **Verified Baseline Value:** **`50`**
* **Active Status Breakdown:** Under Review (18), Pending Approval (8), Submitted (6), Escalated (6), Approved (5), Draft (4), Rejected (3).

---

### 2.2 Active SLA Urgency & Health Metrics

#### Overdue Cases
* **Definition:** Active backlog requests whose contractual or regulatory SLA deadline has expired relative to the evaluation anchor.
* **Scope / Temporal Mode:** Current-State Only
* **Authoritative Source:** `vw_active_backlog` (SQLite) / `[Overdue Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM vw_active_backlog WHERE SLAState = 'Overdue';` / Evaluated relative to `2026-09-26 17:00:00`
* **Verified Baseline Value:** **`24`** (48.0% of active backlog)

---

#### Approaching Deadline Cases
* **Definition:** Active backlog requests that have not yet breached their deadline, but whose remaining time falls within the configured warning threshold (e.g., within 6h for Critical, 24h for High/Medium, 48h for Low).
* **Scope / Temporal Mode:** Current-State Only
* **Authoritative Source:** `vw_active_backlog` (SQLite) / `[Approaching Deadline Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM vw_active_backlog WHERE SLAState = 'Approaching Deadline';`
* **Verified Baseline Value:** **`0`**

---

#### On Track Cases
* **Definition:** Active backlog requests progressing safely within their allotted SLA window with sufficient buffer.
* **Scope / Temporal Mode:** Current-State Only
* **Authoritative Source:** `vw_active_backlog` (SQLite) / `[On Track Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM vw_active_backlog WHERE SLAState = 'On Track';` / `[Active Backlog] - [Overdue Cases] - [Approaching Deadline Cases]`
* **Verified Baseline Value:** **`26`** (52.0% of active backlog)

---

#### High/Critical Active Cases
* **Definition:** Active backlog requests designated as High or Critical risk requiring expedited handling and senior supervisory oversight.
* **Scope / Temporal Mode:** Current-State Only
* **Authoritative Source:** `vw_active_backlog` (SQLite) / `[High/Critical Active Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM vw_active_backlog WHERE RiskLevel IN ('High', 'Critical');`
* **Verified Baseline Value:** **`15`** (`Critical` = 7, `High` = 8)

---

### 2.3 Historical SLA Performance Metrics

#### SLA Met Cases
* **Definition:** Completed compliance requests that were finalized on or before their target due date/time.
* **Scope / Temporal Mode:** Historical Only
* **Authoritative Source:** `vw_request_performance` (SQLite) / `[SLA Met Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM ComplianceRequest WHERE Status = 'Closed' AND SLABreachFlag = 0;`
* **Verified Baseline Value:** **`88`** (88.0% compliance rate)

---

#### SLA Breached Cases
* **Definition:** Completed compliance requests whose final completion timestamp exceeded their target due date/time.
* **Scope / Temporal Mode:** Historical Only
* **Authoritative Source:** `vw_request_performance` (SQLite) / `[SLA Breached Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM ComplianceRequest WHERE Status = 'Closed' AND SLABreachFlag = 1;`
* **Verified Baseline Value:** **`12`**

---

#### SLA Breach Rate
* **Definition:** Proportion of completed requests that failed to satisfy their mandatory SLA turnaround window.
* **Scope / Temporal Mode:** Historical KPI
* **Authoritative Source:** `vw_process_area_performance` (SQLite) / `[SLA Breach Rate]` (Power BI)
* **Underlying SQL / DAX:** `SELECT ROUND(AVG(SLABreachFlag) * 100.0, 2) FROM ComplianceRequest WHERE Status = 'Closed';` / `DIVIDE([SLA Breached Cases], [Closed Requests], 0)`
* **Verified Baseline Value:** **`12.0%`** (Target benchmark: `< 5.0%`)

---

### 2.4 Resolution Efficiency & Duration Metrics

#### Average Resolution Time
* **Definition:** Arithmetic mean duration in decimal hours required to resolve and close completed compliance requests.
* **Scope / Temporal Mode:** Historical KPI
* **Authoritative Source:** `vw_request_performance` (SQLite) / `[Average Resolution Time]` (Power BI)
* **Underlying SQL / DAX:** `SELECT ROUND(AVG(ResolutionTimeHours), 2) FROM vw_request_performance WHERE Status = 'Closed';`
* **Verified Baseline Value:** **`69.27 hours`**
* **Process Area Breakdown (Closed Cases):**
  - AML Operations: **`80.12 hrs`** (30 closed cases)
  - Sanctions: **`77.19 hrs`** (14 closed cases)
  - Customer Onboarding: **`67.89 hrs`** (27 closed cases)
  - KYC Operations: **`55.70 hrs`** (19 closed cases)
  - Policy & Governance: **`55.19 hrs`** (10 closed cases)

---

#### Median Resolution Time
* **Definition:** 50th percentile resolution time in decimal hours. Unlike the arithmetic mean, the median is resilient against extreme outlier investigations.
* **Scope / Temporal Mode:** Historical KPI
* **Authoritative Source:** Python Array Calculation (SQLite layer) / `[Median Resolution Time]` (Power BI)
* **Underlying Calculation / DAX:** `statistics.median(ResolutionTimeHours)` / `CALCULATE(MEDIAN(FactComplianceRequests[ResolutionTimeHours]), FactComplianceRequests[Status] = "Closed")`
* **Verified Baseline Value:** **`44.79 hours`** (Min: 4.50 hrs, Max: 304.32 hrs)

---

### 2.5 Governance & Workflow Metrics

#### Escalated Cases
* **Definition:** Total count of requests that triggered formal escalation to senior leadership during their operational lifecycle.
* **Scope / Temporal Mode:** Aggregate (All Records)
* **Authoritative Source:** `ComplianceRequest` (SQLite) / `[Escalated Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM ComplianceRequest WHERE EscalationFlag = 1;`
* **Verified Baseline Value:** **`17`** (11.3% of all requests; 6 currently active in 'Escalated' status)

---

#### Approval Required Cases
* **Definition:** Total count of requests carrying mandatory dual-tier supervisory sign-off prior to closure.
* **Scope / Temporal Mode:** Aggregate (All Records)
* **Authoritative Source:** `ComplianceRequest` (SQLite) / `[Approval Required Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM ComplianceRequest WHERE ApprovalRequired = 1;`
* **Verified Baseline Value:** **`70`** (46.7% of all requests)
