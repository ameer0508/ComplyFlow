# SharePoint Operational Layer: Manual Build Specification

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** Step-by-Step Implementation Guide for Microsoft 365
**Target Environment:** Microsoft SharePoint Online
**Phase:** 3 Implementation Manual

---

## 1. Overview & Setup Prerequisites

This document provides exact, step-by-step instructions to create the ComplyFlow operational data layer in a Microsoft 365 SharePoint Online site.

### Recommended Site Setup:
1. Navigate to your Microsoft 365 SharePoint Admin Center or SharePoint Home.
2. Create a **Team Site** or **Communication Site** named **`ComplyFlow`** (e.g., URL: `https://<tenant>.sharepoint.com/sites/ComplyFlow`).
3. Follow the build sequence below strictly:
   - **Step 1:** Build `SLAPolicies` (Reference List)
   - **Step 2:** Build `ComplianceRequests` (Primary Operational List)
   - **Step 3:** Build `RequestAuditLog` (Audit Event Ledger)
   - **Step 4:** Configure Operational Views

---

## 2. Step 1: Build `SLAPolicies` List

This reference list must be created first so policy values are documented for lookup.

1. In the SharePoint site, click **New** $\to$ **List** $\to$ **Blank list**.
2. Name the list: **`SLAPolicies`**.
3. Add the following columns:

| Step | Column Name | Column Type | Configuration Settings | Required? |
| :---: | :--- | :--- | :--- | :---: |
| 1.1 | **Title** *(Default)* | Single line of text | Rename display name to **Risk Level** | Yes |
| 1.2 | **SLATargetHours** | Number | Number of decimal places: `0` | Yes |
| 1.3 | **WarningThresholdHours** | Number | Number of decimal places: `0` | Yes |
| 1.4 | **ApprovalMandatory** | Yes/No (Checkbox) | Default value: `No` | Yes |
| 1.5 | **DefaultEscalationRole**| Single line of text | Max characters: `100` | Yes |

### Initial Policy Seed Records:
Click **Edit in grid view** and enter these exact 4 rows:

| Risk Level (`Title`) | SLATargetHours | WarningThresholdHours | ApprovalMandatory | DefaultEscalationRole |
| :--- | :---: | :---: | :---: | :--- |
| **Critical** | `24` | `6` | `Yes` | `Head of Compliance` |
| **High** | `72` | `24` | `Yes` | `Compliance Team Lead` |
| **Medium** | `120` | `24` | `No` | `Operational Queue Manager` |
| **Low** | `240` | `48` | `No` | `Operations Supervisor` |

---

## 3. Step 2: Build `ComplianceRequests` List

This is the central operational list for case management.

1. Click **New** $\to$ **List** $\to$ **Blank list**.
2. Name the list: **`ComplianceRequests`**.
3. Add the columns as specified below:

| Column Name | Internal Name | Type | Choices / Values / Settings | Required? |
| :--- | :--- | :--- | :--- | :---: |
| **Title** *(Default)* | `Title` | Single line text | Summary / Headline of request | Yes |
| **Request ID** | `RequestID` | Single line text | Enforce unique values: **Yes** | Yes |
| **Request Type** | `RequestType` | Choice | `KYC Review`<br>`PEP Review`<br>`AML Transaction Inquiry`<br>`Sanctions Review`<br>`Policy Exception` | Yes |
| **Process Area** | `ProcessArea` | Choice | `Customer Onboarding`<br>`AML Operations`<br>`KYC Operations`<br>`Sanctions`<br>`Policy & Governance` | Yes |
| **Risk Level** | `RiskLevel` | Choice | `Low`<br>`Medium`<br>`High`<br>`Critical` (Default: `Medium`) | Yes |
| **Priority** | `Priority` | Choice | `Low`<br>`Medium`<br>`High`<br>`Critical` (Default: `Medium`) | Yes |
| **Status** | `Status` | Choice | `Draft`<br>`Submitted`<br>`Under Review`<br>`Pending Approval`<br>`Escalated`<br>`Approved`<br>`Rejected`<br>`Closed` (Default: `Draft`) | Yes |
| **Description** | `Description` | Multiple lines text | Plain text or Rich text | Yes |
| **Requester Name** | `RequesterName` | Single line text | Submitter's full name | Yes |
| **Requester Email** | `RequesterEmail` | Single line text | Submitter's corporate email | Yes |
| **Requester Department** | `RequesterDepartment` | Choice | `Corporate Onboarding`<br>`Wealth Management`<br>`Institutional Sales`<br>`Trade Operations`<br>`Treasury` | Yes |
| **Assigned Analyst** | `AssignedAnalyst` | Person or Group | Allow multiple selections: **No** | No |
| **Assigned Analyst Email**| `AssignedAnalystEmail`| Single line text | Analyst corporate email | No |
| **Compliance Team** | `ComplianceTeam` | Choice | `Financial Crime Compliance`<br>`Regulatory Operations`<br>`Sanctions Advisory` | Yes |
| **Submission Date Time** | `SubmissionDateTime` | Date and Time | Include Time: **Yes**, Format: Friendly/Standard | No |
| **Target Due Date Time** | `TargetDueDateTime` | Date and Time | Include Time: **Yes** | No |
| **Completion Date Time** | `CompletionDateTime` | Date and Time | Include Time: **Yes** | No |
| **SLA Target Hours** | `SLATargetHours` | Number | Decimal places: `0` | Yes |
| **SLA Breach Flag** | `SLABreachFlag` | Yes/No | Default: `No` | Yes |
| **Approval Required** | `ApprovalRequired` | Yes/No | Default: `No` | Yes |
| **Approved By** | `ApprovedBy` | Person or Group | Allow multiple selections: **No** | No |
| **Approval Date** | `ApprovalDate` | Date and Time | Include Time: **Yes** | No |
| **Escalation Flag** | `EscalationFlag` | Yes/No | Default: `No` | Yes |
| **Escalated To** | `EscalatedTo` | Single line text | Manager / Role | No |
| **Escalation Reason** | `EscalationReason` | Multiple lines text | Plain text | No |
| **Closure Notes** | `ClosureNotes` | Multiple lines text | Plain text | No |
| **Created Date** | `CreatedDate` | Date and Time | Include Time: **Yes** | Yes |
| **Modified Date** | `ModifiedDate` | Date and Time | Include Time: **Yes** | Yes |

---

## 4. Step 3: Build `RequestAuditLog` List

This supporting list stores milestone audit records.

1. Click **New** $\to$ **List** $\to$ **Blank list**.
2. Name the list: **`RequestAuditLog`**.
3. Configure the columns:

| Column Name | Internal Name | Type | Settings / Allowed Choices | Required? |
| :--- | :--- | :--- | :--- | :---: |
| **Title** *(Default)* | `Title` | Single line text | Rename display name to **Request ID** | Yes |
| **Audit ID** | `AuditID` | Number | Decimals: `0`, Unique: **Yes** | Yes |
| **Timestamp** | `Timestamp` | Date and Time | Include Time: **Yes** | Yes |
| **Action Type** | `ActionType` | Choice | `Created`<br>`Submitted`<br>`Assigned`<br>`Status Changed`<br>`Escalated`<br>`Approval Requested`<br>`Approved`<br>`Rejected`<br>`Closed` | Yes |
| **Performed By** | `PerformedBy` | Single line text | Submitter, Analyst, Manager, or `System Automation` | Yes |
| **Old Status** | `OldStatus` | Single line text | Status before transition | No |
| **New Status** | `NewStatus` | Single line text | Status after transition | Yes |
| **Comments** | `Comments` | Multiple lines text | Audit notes | No |

---

## 5. Step 4: Configure Operational Views in `ComplianceRequests`

To configure views, navigate to the `ComplianceRequests` list $\to$ Click the View dropdown $\to$ **Create new view**.

### View 1: Active Compliance Queue
- **View Name:** `Active Compliance Queue`
- **View Type:** Standard List
- **Columns to Display:** `RequestID`, `Title`, `ProcessArea`, `RequestType`, `RiskLevel`, `Priority`, `Status`, `AssignedAnalyst`, `TargetDueDateTime`, `SLABreachFlag`, `EscalationFlag`.
- **Filter:** Show items only when:
  `Status` is not equal to `Closed`
- **Sort:** `TargetDueDateTime` (Ascending)

### View 2: Overdue Cases
- **View Name:** `Overdue Cases`
- **Filter:** Show items only when:
  `Status` is not equal to `Closed` **AND** `SLABreachFlag` is equal to `Yes`
- **Sort:** `TargetDueDateTime` (Ascending)

### View 3: Pending Approval Queue
- **View Name:** `Pending Approval Queue`
- **Filter:** Show items only when:
  `Status` is equal to `Pending Approval`
- **Sort:** `TargetDueDateTime` (Ascending)

### View 4: Escalated Cases
- **View Name:** `Escalated Cases`
- **Filter:** Show items only when:
  `EscalationFlag` is equal to `Yes`
- **Sort:** `Modified` (Descending)

### View 5: Closed Cases Archive
- **View Name:** `Closed Cases Archive`
- **Filter:** Show items only when:
  `Status` is equal to `Closed`
- **Sort:** `CompletionDateTime` (Descending)

---

## 6. Step 5: Optional List Validation Formula

To prevent data corruption at the SharePoint level, navigate to **List Settings** $\to$ **Validation settings** on `ComplianceRequests` and paste this formula:

```excel
=IF([Status]="Closed", IF(ISBLANK([CompletionDateTime]), FALSE, TRUE), TRUE)
```
*(User message: "A closed compliance request must have a valid Completion Date Time populated.")*
