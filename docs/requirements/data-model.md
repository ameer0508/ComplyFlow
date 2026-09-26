# ComplyFlow Data Model & Business Entity Specification

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** Data Model & Entity Dictionary
**Phase:** 2A (Refined Design Specification)
**Status:** Approved Baseline for Phase 2B Implementation

---

## 1. Executive Summary & Design Principles

The ComplyFlow data model provides a streamlined, transparent foundation for managing financial-services compliance requests. The architecture supports:
- **Operational Intake & Queuing** in Microsoft Power Apps.
- **Structured Storage** in SharePoint Online.
- **Automated Workflow Orchestration** in Power Automate.
- **Process Intelligence & Bottleneck Analytics** in SQL, Python, and Power BI.

### Key Refinements for MVP
- **Simplified Calendar-Hours SLA:** Replaces complex working-day business calendars with clear, explainable **calendar hours** (24h, 72h, 120h, 240h).
- **Process Area Dimensionality:** Adds a controlled `ProcessArea` attribute to isolate operational backlogs and stage dwell times across business functions.
- **Derived Resolution Metric:** Formulates `ResolutionTimeHours` as an analytical calculation performed downstream in SQL/Python/DAX rather than manually keyed in by users.
- **Milestone-Based Governance:** Standardizes `RequestAuditLog` around nine high-value lifecycle state changes.

---

## 2. Entity Overview: Entities vs. Controlled Values

| Concept | Structure | Implementation Rationale |
| :--- | :--- | :--- |
| **ComplianceRequest** | **Core Transaction Entity (Table / List)** | Central entity tracking each compliance case, submitter metadata, assignment, risk tier, milestones, and final resolution. |
| **RequestAuditLog** | **Supporting Audit Entity (Table / List)** | Milestone event log capturing who changed status, when, old status, new status, and action comments. |
| **SLAPolicy** | **Reference Entity (Lookup / Config)** | Decoupled rule matrix mapping `RiskLevel` to `SLATargetHours`, reminder thresholds, and mandatory approval triggers. |
| **ProcessArea** | **Controlled Value (Choice / Enum)** | 5 operational areas enabling process-bottleneck drill-downs in Power BI without multi-table join overhead. |
| **RequestType** | **Controlled Value (Choice / Enum)** | 5 standardized compliance workflows for intake routing and volume analysis. |
| **RiskLevel** | **Controlled Value (Choice / Enum)** | 4 discrete tiers driving SLA duration, priority, approval requirements, and escalation paths. |
| **Status** | **Controlled Value (Choice / Enum)** | 8 defined lifecycle stages with explicit valid transition pathways. |
| **Priority** | **Controlled Value (Choice / Enum)** | Aligns with RiskLevel by default; allows operational override for time-critical filings. |
| **Approval & Escalation** | **Embedded Attributes** | Modeled directly on `ComplianceRequest` (`ApprovedBy`, `ApprovalDate`, `EscalatedTo`, `EscalationReason`) to keep Power Apps forms and SharePoint lists simple. |

---

## 3. Entity Dictionary & Field Specifications

### 3.1. `ComplianceRequest` (Primary Entity)

| Field Name | Data Type (SQL) | SharePoint Column Type | Nullable? | Description & Allowed Values |
| :--- | :--- | :--- | :--- | :--- |
| `RequestID` | `VARCHAR(20)` / `INT PK` | Single line of text (or ID) | No (PK) | Unique identifier (e.g., `CR-2026-0001` or auto-increment integer). |
| `Title` | `VARCHAR(150)` | Single line of text | No | Short descriptive summary of the review request. |
| `RequestType` | `VARCHAR(50)` | Choice | No | `KYC Review`, `PEP Review`, `AML Transaction Inquiry`, `Sanctions Review`, `Policy Exception`. |
| `ProcessArea` | `VARCHAR(50)` | Choice | No | `Customer Onboarding`, `AML Operations`, `KYC Operations`, `Sanctions`, `Policy & Governance`. |
| `RiskLevel` | `VARCHAR(20)` | Choice | No | `Low`, `Medium`, `High`, `Critical`. |
| `Priority` | `VARCHAR(20)` | Choice | No | `Low`, `Medium`, `High`, `Critical` (defaults to match `RiskLevel`). |
| `Status` | `VARCHAR(30)` | Choice | No | `Draft`, `Submitted`, `Under Review`, `Pending Approval`, `Escalated`, `Approved`, `Rejected`, `Closed`. |
| `Description` | `TEXT` | Multiple lines of text | No | Full background narrative, context, and counterparty details. |
| `RequesterName` | `VARCHAR(100)` | Person or Text | No | Full name of the employee submitting the request. |
| `RequesterEmail` | `VARCHAR(150)` | Single line of text | No | Email address for confirmation alerts and notifications. |
| `RequesterDepartment` | `VARCHAR(100)` | Choice | No | Business unit: `Corporate Onboarding`, `Wealth Management`, `Institutional Sales`, `Trade Operations`, `Treasury`. |
| `AssignedAnalyst` | `VARCHAR(100)` | Person or Text | Yes | Assigned compliance officer (null while in unassigned `Submitted` queue). |
| `AssignedAnalystEmail`| `VARCHAR(150)` | Single line of text | Yes | Analyst email for assignment and reminder notifications. |
| `ComplianceTeam` | `VARCHAR(100)` | Choice | No | Team queue: `Financial Crime Compliance`, `Regulatory Operations`, `Sanctions Advisory`. |
| `SubmissionDateTime` | `DATETIME` | Date and Time | No | Exact timestamp when case moved from `Draft` to `Submitted`. |
| `TargetDueDateTime` | `DATETIME` | Date and Time | No | Deadline: `SubmissionDateTime + SLATargetHours`. |
| `CompletionDateTime` | `DATETIME` | Date and Time | Yes | Timestamp when status reaches `Approved`, `Rejected`, or `Closed`. |
| `SLATargetHours` | `INT` | Number | No | Allocated SLA duration in calendar hours (24, 72, 120, 240). |
| `SLABreachFlag` | `BOOLEAN` / `INT` | Yes/No (Boolean) | No | `0` (Within SLA) or `1` (Breached). |
| `ApprovalRequired` | `BOOLEAN` / `INT` | Yes/No (Boolean) | No | Derived from `SLAPolicy`: `1` for `High`/`Critical`; `0` otherwise. |
| `ApprovedBy` | `VARCHAR(100)` | Person or Text | Yes | Manager name signing off on the case. |
| `ApprovalDate` | `DATETIME` | Date and Time | Yes | Timestamp of manager approval or rejection. |
| `EscalationFlag` | `BOOLEAN` / `INT` | Yes/No (Boolean) | No | Indicates whether the case was escalated (`0` or `1`). |
| `EscalatedTo` | `VARCHAR(100)` | Person or Text | Yes | Target role or manager name for escalation. |
| `EscalationReason` | `VARCHAR(255)` | Single line of text | Yes | E.g., `SLA Breach Imminent`, `Sanctions Match Found`, `Information Blocked`. |
| `ClosureNotes` | `TEXT` | Multiple lines of text | Yes | Analyst resolution summary upon closing the request. |
| `CreatedDate` | `DATETIME` | Date and Time | No | Record creation timestamp. |
| `ModifiedDate` | `DATETIME` | Date and Time | No | Last update timestamp. |

---

### 3.2. `RequestAuditLog` (Supporting Audit Entity)

Captures high-value lifecycle milestones for regulatory governance:

| Field Name | Data Type (SQL) | SharePoint Column Type | Nullable? | Description |
| :--- | :--- | :--- | :--- | :--- |
| `AuditID` | `INT PK` | ID (Auto-increment) | No | Unique audit record identifier. |
| `RequestID` | `VARCHAR(20)` / `INT FK`| Single line of text / Lookup| No | References `ComplianceRequest.RequestID`. |
| `Timestamp` | `DATETIME` | Date and Time | No | Exact event timestamp. |
| `ActionType` | `VARCHAR(50)` | Choice | No | One of 9 milestone events: `Created`, `Submitted`, `Assigned`, `Status Changed`, `Escalated`, `Approval Requested`, `Approved`, `Rejected`, `Closed`. |
| `PerformedBy` | `VARCHAR(100)` | Person or Text | No | User or automated service account initiating the transition. |
| `OldStatus` | `VARCHAR(30)` | Single line of text | Yes | Status before transition (null on `Created`). |
| `NewStatus` | `VARCHAR(30)` | Single line of text | No | Status after transition. |
| `Comments` | `VARCHAR(255)` | Single line of text | Yes | Explanatory note, re-assignment comment, or escalation trigger. |

---

### 3.3. `SLAPolicy` (Reference Entity / Lookup Table)

Maps risk levels to calendar-hour SLA targets and escalation parameters:

| RiskLevel (PK) | SLATargetHours | WarningThresholdHours | ApprovalMandatory? | DefaultEscalationRole |
| :--- | :--- | :--- | :--- | :--- |
| **Critical** | **24 Hours** | 6 Hours remaining | **Yes** | Head of Compliance |
| **High** | **72 Hours** | 24 Hours remaining | **Yes** | Compliance Team Lead |
| **Medium** | **120 Hours** | 24 Hours remaining | **No** | Operational Queue Manager |
| **Low** | **240 Hours** | 48 Hours remaining | **No** | Operations Supervisor |

> **Calendar Hours Rationale:** Using calendar hours eliminates dependencies on regional holiday tables and business-day logic at the prototype stage. A production system could later integrate custom holiday calendars without altering the core schema.

---

## 4. Controlled Values & Allowed Choices

### 4.1. Request Types (Fictional Financial-Services Scenarios)
1. **KYC Review:** Periodic review of customer identification, ownership structure, and documentation.
2. **PEP Review:** Risk assessment of Politically Exposed Persons and associated entities.
3. **AML Transaction Inquiry:** Operational follow-up on anomalous or threshold-exceeding transactions.
4. **Sanctions Review:** Pre-trade screening or counterparty evaluation against sanctions restrictions.
5. **Policy Exception:** Front-office request for temporary deviation from compliance policies.

### 4.2. Process Areas (Operational Dimension)
1. **Customer Onboarding**
2. **AML Operations**
3. **KYC Operations**
4. **Sanctions**
5. **Policy & Governance**

### 4.3. Risk Levels & Priority
- `Low` | `Medium` | `High` | `Critical`
- *Priority defaults to matching RiskLevel, but can be elevated if operational urgency dictates.*

### 4.4. Lifecycle Statuses
- `Draft` → Intake preparation, not yet visible in active analyst queue.
- `Submitted` → Formally logged; SLA countdown begins; awaiting analyst pickup.
- `Under Review` → Analyst actively investigating.
- `Pending Approval` → Analyst completed review; waiting for manager sign-off (mandatory for High/Critical).
- `Escalated` → Case flagged for leadership review due to breach risk or complex findings.
- `Approved` → Review successfully concluded with favorable outcome.
- `Rejected` → Review concluded with denial or prohibition.
- `Closed` → Case archived; completion metrics finalized.

---

## 5. Derived Analytical Metrics: `ResolutionTimeHours`

To prevent data corruption and eliminate manual entry errors, `ResolutionTimeHours` is **strictly derived in the analytics layer** (SQL, Python, or Power BI/DAX):

### Definition:
- **For Closed Requests:**
  $$\text{ResolutionTimeHours} = \text{CompletionDateTime} - \text{SubmissionDateTime} \quad (\text{in fractional or whole hours})$$
- **For Open Requests (`Status != 'Closed'`):**
  $\text{ResolutionTimeHours} = \text{NULL}$ (Open cases must not be counted as resolved).

### Where Calculated:
1. **SQL View / Query:**
   ```sql
   CASE
       WHEN Status = 'Closed' AND CompletionDateTime IS NOT NULL
       THEN ROUND((JULIANDAY(CompletionDateTime) - JULIANDAY(SubmissionDateTime)) * 24.0, 1)
       ELSE NULL
   END AS ResolutionTimeHours
   ```
2. **Python:**
   ```python
   df['ResolutionTimeHours'] = np.where(
       df['Status'] == 'Closed',
       (df['CompletionDateTime'] - df['SubmissionDateTime']).dt.total_seconds() / 3600.0,
       np.nan
   )
   ```
3. **Power BI / DAX Measure:**
   ```dax
   AvgResolutionTimeHours =
   CALCULATE(
       AVERAGEX('ComplianceRequests', DATEDIFF('ComplianceRequests'[SubmissionDateTime], 'ComplianceRequests'[CompletionDateTime], HOUR)),
       'ComplianceRequests'[Status] = "Closed"
   )
   ```

---

## 6. Business Validation Rules (Data Quality)

1. **Intake Completeness:** `Title`, `RequestType`, `ProcessArea`, `RiskLevel`, `Description`, `RequesterName`, and `RequesterDepartment` must never be null.
2. **Chronological Validity:**
   - `SubmissionDateTime >= CreatedDate`
   - `TargetDueDateTime = SubmissionDateTime + SLATargetHours`
   - `CompletionDateTime >= SubmissionDateTime` (when status is `Closed`)
   - `ApprovalDate >= SubmissionDateTime` (when approval occurs)
3. **Queue Assignment Guard:** Case cannot move to `Under Review` unless `AssignedAnalyst` is assigned.
4. **Governance Approval Guard:** High or Critical risk cases cannot move to `Approved` or `Closed` without `ApprovedBy` and `ApprovalDate` being populated.
5. **SLA Breach Flag Consistency:**
   - Closed cases: `SLABreachFlag = 1` if `CompletionDateTime > TargetDueDateTime`, else `0`.
   - Open cases: `SLABreachFlag = 1` if `CurrentDateTime > TargetDueDateTime`, else `0`.
6. **Milestone Audit Rule:** Every transition between distinct status values must generate a corresponding record in `RequestAuditLog`.
