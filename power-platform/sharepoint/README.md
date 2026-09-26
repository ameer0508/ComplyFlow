# SharePoint Operational Data Layer

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Microsoft SharePoint Online Operational Store
**Phase:** 3 (SharePoint Architecture & Build Specification)
**Status:** Specification & Reference Design (Manual Build Ready)

---

## 1. Purpose & Architectural Role

Within the ComplyFlow platform architecture, **Microsoft SharePoint Online** functions as the **central operational data store**. It bridges user-facing interfaces and automated process logic:

```
[ Power Apps UI ]
       │ (Read / Write Records)
       ▼
[ SharePoint Online Lists ] ◄───► [ Power Automate Cloud Flows ]
  • ComplianceRequests              • SLA Stamping & Notifications
  • RequestAuditLog                 • Manager Approval Dispatch
  • SLAPolicies                     • Milestone Audit Logging
       │
       ▼ (Export / Synchronize Snapshot)
[ SQL & Python Analytics Layer ] ──► [ Power BI Management Dashboards ]
```

### Why SharePoint for Operations?
- **Low-Code Native:** Seamless out-of-the-box connector integration with Power Apps and Power Automate without custom API development or gateway infrastructure.
- **Structured Tabular Lists:** Provides typed fields (Single line, Multiline, Choices, Dates, Booleans, Person/User) with view-level filtering and item-level versioning.
- **Apprentice Explainability:** Eliminates the licensing barriers and administrative complexity of Microsoft Dataverse or Azure SQL Server for an apprentice portfolio, while demonstrating clean enterprise data management.

> **Critical Distinction:** SharePoint is **NOT** replacing the SQL analytics layer.
> - **SharePoint** holds active, live **operational workflow records** and powers daily user intake and approvals.
> - **SQLite / SQL** powers **analytical aggregations, historical trend reporting, and complex window functions**.

---

## 2. List Architecture Overview

The SharePoint operational layer consists of three dedicated lists:

```
SharePoint Site: /sites/ComplyFlow/
├── Lists/ComplianceRequests    (Primary Operational List - 28 Columns)
├── Lists/RequestAuditLog       (Supporting Event Ledger - 8 Columns)
└── Lists/SLAPolicies           (Governance Configuration Lookup - 5 Columns)
```

---

## 3. List 1: `ComplianceRequests` (Primary Operational List)

Houses active and completed compliance review cases.

### Column Mapping & Field Definitions

| Display Name | Internal Name | Column Type | Required? | Description & Allowed Choices |
| :--- | :--- | :--- | :--- | :--- |
| **Title** | `Title` | Single line of text | Yes | Short descriptive title of the compliance request. |
| **Request ID** | `RequestID` | Single line of text | Yes | Unique case identifier (e.g., `CR-2026-0001`). Enforce unique values. |
| **Request Type** | `RequestType` | Choice | Yes | `KYC Review`, `PEP Review`, `AML Transaction Inquiry`, `Sanctions Review`, `Policy Exception`. |
| **Process Area** | `ProcessArea` | Choice | Yes | `Customer Onboarding`, `AML Operations`, `KYC Operations`, `Sanctions`, `Policy & Governance`. |
| **Risk Level** | `RiskLevel` | Choice | Yes | `Low`, `Medium`, `High`, `Critical`. |
| **Priority** | `Priority` | Choice | Yes | `Low`, `Medium`, `High`, `Critical` (Default: `Medium`). |
| **Status** | `Status` | Choice | Yes | `Draft`, `Submitted`, `Under Review`, `Pending Approval`, `Escalated`, `Approved`, `Rejected`, `Closed` (Default: `Draft`). |
| **Description** | `Description` | Multiple lines of text | Yes | Detailed narrative of the review request and counterparty background. |
| **Requester Name** | `RequesterName` | Single line of text | Yes | Name of submitting employee. |
| **Requester Email** | `RequesterEmail` | Single line of text | Yes | Email address of submitter for automated status notifications. |
| **Requester Department** | `RequesterDepartment` | Choice | Yes | `Corporate Onboarding`, `Wealth Management`, `Institutional Sales`, `Trade Operations`, `Treasury`. |
| **Assigned Analyst** | `AssignedAnalyst` | Person or Group | No | Compliance officer investigating the case. |
| **Assigned Analyst Email** | `AssignedAnalystEmail` | Single line of text | No | Analyst email address for direct workflow routing. |
| **Compliance Team** | `ComplianceTeam` | Choice | Yes | `Financial Crime Compliance`, `Regulatory Operations`, `Sanctions Advisory`. |
| **Submission Date Time** | `SubmissionDateTime` | Date and Time | No | Exact timestamp when status changed to `Submitted`. |
| **Target Due Date Time** | `TargetDueDateTime` | Date and Time | No | Deadline: calculated automatically by Power Automate as `SubmissionDateTime + SLATargetHours`. |
| **Completion Date Time** | `CompletionDateTime` | Date and Time | No | Timestamp when status reaches `Approved`, `Rejected`, or `Closed`. |
| **SLA Target Hours** | `SLATargetHours` | Number | Yes | Target turnaround hours (24, 72, 120, 240). Stamped from `SLAPolicies`. |
| **SLA Breach Flag** | `SLABreachFlag` | Yes/No (Boolean) | Yes | Default: `No`. Set to `Yes` if completed past deadline or currently overdue. |
| **Approval Required** | `ApprovalRequired` | Yes/No (Boolean) | Yes | Derived from policy: `Yes` for `High`/`Critical`; `No` for `Low`/`Medium`. |
| **Approved By** | `ApprovedBy` | Person or Group | No | Compliance manager granting formal sign-off. |
| **Approval Date** | `ApprovalDate` | Date and Time | No | Timestamp of management approval. |
| **Escalation Flag** | `EscalationFlag` | Yes/No (Boolean) | Yes | Default: `No`. Indicates if case was escalated. |
| **Escalated To** | `EscalatedTo` | Single line of text | No | Role or manager receiving escalation. |
| **Escalation Reason** | `EscalationReason` | Multiple lines of text | No | Rationale for escalation (e.g., `SLA Breach Imminent`, `Sanctions Match Found`). |
| **Closure Notes** | `ClosureNotes` | Multiple lines of text | No | Summary of findings upon case closure. |
| **Created Date** | `CreatedDate` | Date and Time | Yes | Record creation timestamp. |
| **Modified Date** | `ModifiedDate` | Date and Time | Yes | Last update timestamp. |

---

## 4. List 2: `RequestAuditLog` (Supporting Event Ledger)

Records milestone lifecycle transitions for compliance governance and audit readiness.

### Column Mapping & Field Definitions

| Display Name | Internal Name | Column Type | Required? | Description |
| :--- | :--- | :--- | :--- | :--- |
| **Audit ID** | `AuditID` | Number | Yes | Unique audit record sequence number. |
| **Request ID** | `RequestID` | Single line of text | Yes | References `ComplianceRequests.RequestID`. Indexed for fast lookups. |
| **Timestamp** | `Timestamp` | Date and Time | Yes | Exact time of the milestone event. |
| **Action Type** | `ActionType` | Choice | Yes | Allowed choices: `Created`, `Submitted`, `Assigned`, `Status Changed`, `Escalated`, `Approval Requested`, `Approved`, `Rejected`, `Closed`. |
| **Performed By** | `PerformedBy` | Single line of text / Person | Yes | Name or service account that initiated the transition. |
| **Old Status** | `OldStatus` | Single line of text | No | Status prior to transition (empty on `Created`). |
| **New Status** | `NewStatus` | Single line of text | Yes | Status after transition. |
| **Comments** | `Comments` | Multiple lines of text | No | Explanatory notes, re-assignment reasons, or approval remarks. |

> **Relationship Management:** In SharePoint, relationship integrity between `ComplianceRequests` and `RequestAuditLog` is maintained by **Power Automate cloud flows** on item modification events.

---

## 5. List 3: `SLAPolicies` (Reference & Governance Matrix)

Lookup list defining SLA durations, reminder thresholds, and escalation pathways.

### Column Mapping & Field Definitions

| Display Name | Internal Name | Column Type | Required? | Values |
| :--- | :--- | :--- | :--- | :--- |
| **Risk Level** | `Title` / `RiskLevel` | Choice / Single line | Yes | Primary Key: `Critical`, `High`, `Medium`, `Low`. |
| **SLA Target Hours** | `SLATargetHours` | Number | Yes | `24`, `72`, `120`, `240`. |
| **Warning Threshold Hours** | `WarningThresholdHours` | Number | Yes | `6`, `24`, `24`, `48`. |
| **Approval Mandatory** | `ApprovalMandatory` | Yes/No | Yes | `Yes` (Critical, High) / `No` (Medium, Low). |
| **Default Escalation Role** | `DefaultEscalationRole` | Single line of text | Yes | `Head of Compliance`, `Compliance Team Lead`, `Operational Queue Manager`, `Operations Supervisor`. |

---

## 6. SharePoint Views Specification

Configuring focused views prevents information overload and mirrors operational queues:

1. **View 1: All Compliance Requests (Default View)**
   - *Purpose:* Complete administrative list of all requests.
   - *Columns:* `RequestID`, `Title`, `RequestType`, `ProcessArea`, `RiskLevel`, `Priority`, `Status`, `AssignedAnalyst`, `TargetDueDateTime`, `SLABreachFlag`.
   - *Sort:* `TargetDueDateTime` Ascending.
2. **View 2: Active Compliance Queue**
   - *Purpose:* Working queue for operational analysts.
   - *Filter:* `Status` is not equal to `Closed`.
   - *Columns:* `RequestID`, `Title`, `ProcessArea`, `RiskLevel`, `Priority`, `Status`, `AssignedAnalyst`, `TargetDueDateTime`, `SLABreachFlag`, `EscalationFlag`.
3. **View 3: Overdue Cases**
   - *Purpose:* Immediate escalation view for SLA-breached cases.
   - *Filter:* `Status` is not equal to `Closed` **AND** `SLABreachFlag` is equal to `Yes`.
   - *Sort:* `TargetDueDateTime` Ascending.
4. **View 4: Pending Approval**
   - *Purpose:* Working queue for compliance managers.
   - *Filter:* `Status` is equal to `Pending Approval`.
   - *Sort:* `TargetDueDateTime` Ascending.
5. **View 5: Escalated Cases**
   - *Purpose:* Triage view for team leads and supervisors.
   - *Filter:* `EscalationFlag` is equal to `Yes`.
   - *Sort:* `ModifiedDate` Descending.
6. **View 6: Closed Cases**
   - *Purpose:* Audit archive and historical research.
   - *Filter:* `Status` is equal to `Closed`.
   - *Sort:* `CompletionDateTime` Descending.

---

## 7. Proposed Prototype Governance & Permissions

In a production environment, SharePoint permission groups enforce segregation of duties:

| Proposed Role | Target Membership | List Permissions | Operational Scope |
| :--- | :--- | :--- | :--- |
| **Requester** | Front-Office / Operations Staff | Contribute (Item-level: Create & View Own) | Submit requests, track status of own submissions. |
| **Compliance Analyst** | Investigating Officers | Edit | Assign cases, update notes, change status to Under Review / Pending Approval. |
| **Compliance Manager** | Team Leads / Department Heads | Edit / Full on approvals | Approve or reject cases in Pending Approval, review escalations. |
| **Administrator** | Compliance Operations Lead / IT | Full Control | Maintain lists, modify `SLAPolicies`, manage views. |

*(Note: These are documented architectural recommendations for prototype demonstration; no live M365 tenant accounts are provisioned).*

---

## 8. Downstream Platform Integration

- **Power Apps:** Connects directly to `ComplianceRequests` and `SLAPolicies` as data sources. Forms read choice values dynamically and patch updates directly to SharePoint items.
- **Power Automate:** Triggers on `When an item is created or modified` in `ComplianceRequests`. Automates:
  1. Stamping `TargetDueDateTime = SubmissionDateTime + SLATargetHours`.
  2. Creating a milestone record in `RequestAuditLog`.
  3. Dispatching Teams/Email approval adaptive cards when `Status = Pending Approval`.
- **Power BI:** Connects to SharePoint Online Lists via the native OData/SharePoint Online List connector to pull live operational backlog data into management reports.
