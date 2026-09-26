# Domain Model & Entity Relationships

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** Domain Architecture & Entity Relational Mapping
**Phase:** 2A (Refined Design Specification)
**Status:** Approved Baseline for Phase 2B Implementation

---

## 1. Conceptual Entity-Relationship Model

The ComplyFlow domain model couples relational integrity with low-code simplicity.

```mermaid
erDiagram
    SLAPOLICY {
        string RiskLevel PK "Low, Medium, High, Critical"
        int SLATargetHours "24, 72, 120, 240 calendar hours"
        int WarningThresholdHours "6, 24, 48 hours remaining"
        boolean ApprovalMandatory "True for High/Critical"
        string DefaultEscalationRole "Manager role"
    }

    COMPLIANCEREQUEST {
        string RequestID PK "e.g. CR-2026-0001"
        string Title "Summary of review request"
        string RequestType "KYC, PEP, AML, Sanctions, Policy"
        string ProcessArea "Onboarding, AML, KYC, Sanctions, Policy"
        string RiskLevel FK "References SLAPolicy"
        string Priority "Low, Medium, High, Critical"
        string Status "Draft, Submitted, Under Review, etc."
        string Description "Case narrative"
        string RequesterName "Name of submitter"
        string RequesterEmail "Contact email"
        string RequesterDepartment "Business unit"
        string AssignedAnalyst "Investigating analyst"
        string AssignedAnalystEmail "Analyst email"
        string ComplianceTeam "FCC, RegOps, Sanctions"
        datetime SubmissionDateTime "Formal submission timestamp"
        datetime TargetDueDateTime "SubmissionDateTime + SLATargetHours"
        datetime CompletionDateTime "Case conclusion timestamp"
        int SLATargetHours "Hours allocated by policy"
        boolean SLABreachFlag "1 if breached, 0 if within SLA"
        boolean ApprovalRequired "Derived from SLAPolicy"
        string ApprovedBy "Approving manager"
        datetime ApprovalDate "Timestamp of approval"
        boolean EscalationFlag "Case escalated flag"
        string EscalatedTo "Escalation recipient"
        string EscalationReason "Reason for escalation"
        string ClosureNotes "Conclusion summary"
        datetime CreatedDate "System creation timestamp"
        datetime ModifiedDate "System update timestamp"
    }

    REQUESTAUDITLOG {
        int AuditID PK "Auto-increment ID"
        string RequestID FK "References ComplianceRequest"
        datetime Timestamp "Event occurrence time"
        string ActionType "Created, Submitted, Assigned, etc."
        string PerformedBy "User or automated flow"
        string OldStatus "Status before change"
        string NewStatus "Status after change"
        string Comments "Audit description"
    }

    SLAPOLICY ||--o{ COMPLIANCEREQUEST : "governs SLA target & approval rule of"
    COMPLIANCEREQUEST ||--o{ REQUESTAUDITLOG : "generates milestone events for"
```

---

## 2. Request Lifecycle & Allowed State Transitions

The lifecycle guides the compliance request through defined operational stages, preventing arbitrary status updates and ensuring audit integrity:

```mermaid
stateDiagram-v2
    [*] --> Draft : Requester prepares form
    Draft --> Submitted : Formal Submission (SLA stamped, Analyst notified)

    Submitted --> UnderReview : Analyst assigns to self & starts review

    UnderReview --> UnderReview : Reassignment / Information Request
    UnderReview --> PendingApproval : Review complete (High/Critical risk requires sign-off)
    UnderReview --> Escalated : SLA breach imminent or high-risk finding
    UnderReview --> Approved : Low/Medium risk sign-off directly
    UnderReview --> Rejected : Non-compliant finding

    PendingApproval --> Approved : Compliance Manager approves
    PendingApproval --> Rejected : Compliance Manager rejects
    PendingApproval --> UnderReview : Manager requests additional inquiry
    PendingApproval --> Escalated : Approval SLA deadline breached

    Escalated --> UnderReview : Escalation resolved / reassigned
    Escalated --> Approved : Executive sign-off
    Escalated --> Rejected : Executive rejection

    Approved --> Closed : Archival & metrics finalized
    Rejected --> Closed : Archival & metrics finalized

    Closed --> [*]
```

### Transition Integrity Rules:
1. `Draft` records are pre-submission workspaces and do not incur SLA countdowns or queue dwell-time calculations.
2. A request cannot move to `Under Review` without an `AssignedAnalyst`.
3. High and Critical risk requests **must** pass through `Pending Approval` before moving to `Approved`.
4. Cases can transition to `Escalated` from `Under Review` or `Pending Approval` either manually by the analyst or automatically via Power Automate SLA threshold checks.
5. Once a case reaches `Closed`, its status is immutable.

---

## 3. End-to-End Operational Data Flow

```mermaid
sequenceDiagram
    autonumber
    actor Requester as Business Requester
    participant App as Power Apps UI
    participant SP as SharePoint List
    participant Flow as Power Automate
    actor Analyst as Compliance Analyst
    actor Manager as Compliance Manager
    participant DataOps as Python & SQL Engine
    participant BI as Power BI Dashboard

    Requester->>App: Fills intake form (Title, Category, ProcessArea, Urgency, Narrative)
    App->>SP: Validates & writes record (Status = 'Submitted')
    SP->>Flow: Trigger: Item Created (Status = 'Submitted')
    Flow->>Flow: Lookup SLAPolicy by RiskLevel -> Compute TargetDueDateTime
    Flow->>SP: Updates TargetDueDateTime, SLATargetHours, & ApprovalRequired
    Flow->>Flow: Create Item in RequestAuditLog (ActionType = 'Submitted')
    Flow->>Analyst: Sends email/Teams alert for new assignment

    Analyst->>App: Opens queue, assigns self, sets Status = 'Under Review'
    App->>SP: Updates Status & AssignedAnalyst
    SP->>Flow: Creates RequestAuditLog (ActionType = 'Assigned')

    alt High / Critical Risk Case (ApprovalRequired = 1)
        Analyst->>App: Submits findings, sets Status = 'Pending Approval'
        Flow->>Manager: Dispatches approval request card
        Manager->>Flow: Approves request with sign-off comments
        Flow->>SP: Updates Status = 'Approved', ApprovedBy, ApprovalDate
        Flow->>Flow: Creates RequestAuditLog (ActionType = 'Approved')
    else Low / Medium Risk Case (ApprovalRequired = 0)
        Analyst->>App: Sets Status = 'Approved' or 'Rejected'
        App->>SP: Updates Status & ClosureNotes
        SP->>Flow: Creates RequestAuditLog (ActionType = 'Approved'/'Rejected')
    end

    Analyst->>App: Closes case (Status = 'Closed', CompletionDateTime = Now)
    App->>SP: Updates record

    loop Scheduled Analytics Run
        DataOps->>SP: Extracts operational dataset
        DataOps->>DataOps: Python validates schema, dates, and SLA compliance
        DataOps->>DataOps: Python/SQL derives ResolutionTimeHours (Closed cases only)
        DataOps->>DataOps: SQL aggregates turnaround times, breach rates, ProcessArea bottlenecks
        BI->>DataOps: Refreshes data model
        BI-->>Manager: Displays interactive KPI dashboard
    end
```

---

## 4. Platform Implementation Mapping

| Domain Concept | Microsoft SharePoint Online | Microsoft Power Apps | Microsoft Power Automate | Local SQL (SQLite) | Python Data Engine | Microsoft Power BI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Record Storage** | Primary List: `ComplianceRequests` | Data Source connection to SharePoint list | Native trigger: *When an item is created or modified* | Table: `compliance_requests` | Ingests CSV/JSON/DB via `pandas` / `sqlite3` | Ingests tables into star schema |
| **Process Area** | Choice Column (5 areas) | Dropdown on intake form & filter tab in queue | Routes to specific team channel based on area | `VARCHAR(50)` with check constraint | Validates against allowed enum set | Dimension slicer for bottleneck analysis |
| **Audit Log** | Secondary List: `RequestAuditLog` | Audit timeline gallery view on Request detail screen | Action: *Create item* in `RequestAuditLog` on 9 milestone events | Table: `request_audit_log` | Computes dwell times between audit timestamps | Linked via `RequestID` for audit drill-down |
| **SLA Targets** | Stamped Date/Time column | Visual countdown badge ("Breach in 4 hrs") | Scheduled flow evaluating `TargetDueDateTime < utcNow()` | Date arithmetic: `(JULIANDAY(TargetDueDateTime) - JULIANDAY(SubmissionDateTime)) * 24` | DateTime delta verification: `(df['TargetDueDateTime'] - df['SubmissionDateTime'])` | KPI Cards: % SLA Met, Overdue Volume |
| **Resolution Time** | *Not stored directly* (avoid manual input errors) | *Not entered by user* | *Not entered by user* | Computed in views: `(JULIANDAY(CompletionDateTime) - JULIANDAY(SubmissionDateTime)) * 24` | Derived column: `(Completion - Submission) / 3600s` | DAX Measure: `AVERAGEX('ComplianceRequests', ...)` |
