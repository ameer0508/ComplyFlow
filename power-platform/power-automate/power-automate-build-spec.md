# Power Automate Build Specification

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** Step-by-Step Cloud Flow Manual Construction Guide
**Target Environment:** Microsoft Power Automate Cloud Flows
**Phase:** 5 Implementation Manual

---

## 1. Flow Inventory Overview

```
Power Automate Cloud Flows (ComplyFlow Solution)
├── CF-01 — Process New Compliance Request  (Automated: On Item Created)
├── CF-02 — Track Case Assignment           (Automated: On Item Modified)
├── CF-03 — Route Compliance Approval       (Automated: On Pending Approval)
├── CF-04 — Monitor Compliance SLA          (Scheduled: Daily 08:00 UTC)
├── CF-05 — Record Status Change            (Automated: On Status Modified)
└── CF-06 — Process Case Closure            (Automated: On Case Closed)
```

---

## 2. Flow CF-01: Process New Compliance Request

- **Flow Type:** Automated cloud flow
- **Trigger:** SharePoint — *When an item is created*
  - **Site Address:** `https://<tenant>.sharepoint.com/sites/ComplyFlow`
  - **List Name:** `ComplianceRequests`
  - **Trigger Conditions (Settings):**
    ```
    @equals(triggerOutputs()?['body/Status/Value'], 'Submitted')
    ```

### Action-by-Action Build Sequence:
1. **Initialize Variable:** `varRiskLevel` (Type: `String`, Value: `triggerOutputs()?['body/RiskLevel/Value']`)
2. **Action: SharePoint — Get Items (`Get_SLAPolicy`)**
   - List Name: `SLAPolicies`
   - Filter Query: `Title eq '@{variables('varRiskLevel')}'`
   - Top Count: `1`
3. **Action: Condition (`Check_Policy_Exists`)**
   - Condition: `length(outputs('Get_SLAPolicy')?['body/value'])` is greater than `0`.
   - **If Yes:**
     - **Compose: `Calculate_TargetDueDateTime`**
       - Formula:
         ```json
         addHours(triggerOutputs()?['body/SubmissionDateTime'], int(first(outputs('Get_SLAPolicy')?['body/value'])?['SLATargetHours']))
         ```
     - **Action: SharePoint — Update Item (`Update_Request_With_SLA`)**
       - List Name: `ComplianceRequests`
       - Id: `triggerOutputs()?['body/ID']`
       - Fields to update:
         - `SLATargetHours`: `int(first(outputs('Get_SLAPolicy')?['body/value'])?['SLATargetHours'])`
         - `TargetDueDateTime`: `outputs('Calculate_TargetDueDateTime')`
         - `ApprovalRequired`: `bool(first(outputs('Get_SLAPolicy')?['body/value'])?['ApprovalMandatory'])`
     - **Action: SharePoint — Create Item (`Write_Submitted_AuditLog`)**
       - List Name: `RequestAuditLog`
       - Fields:
         - `Title` (`RequestID`): `triggerOutputs()?['body/RequestID']`
         - `AuditID`: `int(ticks(utcNow()))`
         - `Timestamp`: `utcNow()`
         - `ActionType`: `Submitted`
         - `PerformedBy`: `triggerOutputs()?['body/RequesterName']`
         - `OldStatus`: `Draft`
         - `NewStatus`: `Submitted`
         - `Comments`: `"Request successfully logged and SLA countdown initiated."`
     - **Action: Office 365 Outlook — Send an email (V2) (`Send_Submitter_Receipt`)**
       - To: `triggerOutputs()?['body/RequesterEmail']`
       - Subject: `"Confirmation: Compliance Request Logged - " & triggerOutputs()?['body/RequestID']`
       - Body: Rich text receipt displaying RequestID, Title, ProcessArea, RiskLevel, and calculated TargetDueDateTime.
   - **If No:**
     - **Action: Terminate** (Status: `Failed`, Message: `"SLA policy not found for RiskLevel."`)

---

## 3. Flow CF-02: Track Case Assignment

- **Flow Type:** Automated cloud flow
- **Trigger:** SharePoint — *When an item is modified*
  - **List Name:** `ComplianceRequests`
  - **Trigger Condition:**
    ```
    @not(empty(triggerOutputs()?['body/AssignedAnalyst/Email']))
    ```

### Action-by-Action Build Sequence:
1. **Action: SharePoint — Get Changes for an item or a file (properties only)**
   - Check if `AssignedAnalyst` column has changed (`Since` token).
2. **Action: Condition (`Check_Analyst_Changed`)**
   - Condition: `outputs('Get_Changes')?['body/ColumnHasChanged_AssignedAnalyst']` is equal to `true`.
   - **If Yes:**
     - **Action: SharePoint — Create Item (`Write_Assigned_AuditLog`)**
       - List Name: `RequestAuditLog`
       - Fields:
         - `Title`: `triggerOutputs()?['body/RequestID']`
         - `AuditID`: `int(ticks(utcNow()))`
         - `Timestamp`: `utcNow()`
         - `ActionType`: `Assigned`
         - `PerformedBy`: `triggerOutputs()?['body/Editor/DisplayName']`
         - `OldStatus`: `triggerOutputs()?['body/Status/Value']`
         - `NewStatus`: `Under Review`
         - `Comments`: `concat('Case assigned to analyst ', triggerOutputs()?['body/AssignedAnalyst/DisplayName'])`
     - **Action: SharePoint — Update Item (`Set_Status_UnderReview`)**
       - Id: `triggerOutputs()?['body/ID']`
       - Status: `Under Review`
     - **Action: Office 365 Outlook — Send an email (V2) (`Notify_Assigned_Analyst`)**
       - To: `triggerOutputs()?['body/AssignedAnalyst/Email']`
       - Subject: `concat('Case Assignment: [', triggerOutputs()?['body/Priority/Value'], '] ', triggerOutputs()?['body/RequestID'], ' - ', triggerOutputs()?['body/Title'])`
       - Body: Notification card with case description and target due date.

---

## 4. Flow CF-03: Route Compliance Approval

- **Flow Type:** Automated cloud flow
- **Trigger:** SharePoint — *When an item is modified*
  - **List Name:** `ComplianceRequests`
  - **Trigger Condition:**
    ```
    @and(equals(triggerOutputs()?['body/Status/Value'], 'Pending Approval'), equals(triggerOutputs()?['body/ApprovalRequired'], true))
    ```

### Action-by-Action Build Sequence:
1. **Action: SharePoint — Create Item (`Write_Approval_Requested_AuditLog`)**
   - List Name: `RequestAuditLog`
   - Fields:
     - `Title`: `triggerOutputs()?['body/RequestID']`
     - `AuditID`: `int(ticks(utcNow()))`
     - `Timestamp`: `utcNow()`
     - `ActionType`: `Approval Requested`
     - `PerformedBy`: `triggerOutputs()?['body/Editor/DisplayName']`
     - `OldStatus`: `Under Review`
     - `NewStatus`: `Pending Approval`
     - `Comments`: `"Analyst completed preliminary inquiry; routed for formal sign-off."`
2. **Action: Switch (`Determine_Approver_Role`)**
   - Expression: `triggerOutputs()?['body/RiskLevel/Value']`
   - **Case 'Critical':**
     - Set variable `varApproverEmail` = `LookUp(SLAPolicies, Title eq 'Critical')/DefaultEscalationRole` (e.g. `head.compliance@complyflow-demo.internal`)
   - **Case 'High':**
     - Set variable `varApproverEmail` = `LookUp(SLAPolicies, Title eq 'High')/DefaultEscalationRole` (e.g. `teamlead.compliance@complyflow-demo.internal`)
3. **Action: Approvals — Start and wait for an approval (`Approval_Card`)**
   - Approval type: `Approve/Reject - First to respond`
   - Title: `concat('Approval Required: ', triggerOutputs()?['body/RequestID'], ' - ', triggerOutputs()?['body/Title'])`
   - Assigned to: `variables('varApproverEmail')`
   - Details: Markdown body detailing Counterparty, Risk Level, Process Area, and Analyst Findings.
4. **Action: Condition (`Check_Approval_Outcome`)**
   - Expression: `outputs('Approval_Card')?['body/outcome']` is equal to `Approve`
   - **If Approved:**
     - Update `ComplianceRequests`: Status = `Approved`, `ApprovedBy = outputs('Approval_Card')?['body/responses']?[0]?['responder/displayName']`, `ApprovalDate = utcNow()`.
     - Create `RequestAuditLog`: ActionType = `Approved`, Comments = `outputs('Approval_Card')?['body/responses']?[0]?['comments']`.
     - Notify Submitter & Analyst of approval.
   - **If Rejected:**
     - Update `ComplianceRequests`: Status = `Rejected`, `ApprovedBy = outputs('Approval_Card')?['body/responses']?[0]?['responder/displayName']`, `ApprovalDate = utcNow()`.
     - Create `RequestAuditLog`: ActionType = `Rejected`, Comments = `concat('Sign-off denied: ', outputs('Approval_Card')?['body/responses']?[0]?['comments'])`.
     - Notify Submitter & Analyst of rejection.

---

## 5. Flow CF-04: Monitor Compliance SLA & Escalation

- **Flow Type:** Scheduled cloud flow
- **Recurrence:** Every `1` Day at `08:00` UTC

### Action-by-Action Build Sequence:
1. **Action: SharePoint — Get Items (`Get_Active_Requests`)**
   - List Name: `ComplianceRequests`
   - Filter Query: `Status ne 'Closed'`
2. **Action: Apply to each (`Process_Each_Active_Case`)**
   - Items: `outputs('Get_Active_Requests')?['body/value']`
   - **Step 2.1: Lookup SLA Policy** (`Get_Policy_For_Case`)
     - Filter: `Title eq '@{items('Process_Each_Active_Case')?['RiskLevel/Value']}'`
   - **Step 2.2: Condition (`Is_Case_Overdue`)**
     - Expression: `greater(utcNow(), items('Process_Each_Active_Case')?['TargetDueDateTime'])`
     - **If Yes (Overdue):**
       - **Condition (`Check_If_Already_Escalated`):**
         - Expression: `items('Process_Each_Active_Case')?['EscalationFlag']` is equal to `false` (Idempotency Guard)
         - **If Not Escalated Yet:**
           - **Action: SharePoint — Update Item (`Escalate_Request`)**
             - Set `EscalationFlag = true`
             - Set `SLABreachFlag = true`
             - Set `EscalatedTo = first(outputs('Get_Policy_For_Case')?['body/value'])?['DefaultEscalationRole']`
             - Set `EscalationReason = "Automated SLA Monitoring: Turnaround deadline exceeded without case closure."`
           - **Action: SharePoint — Create Item (`Write_Escalated_AuditLog`)**
             - ActionType = `Escalated`
             - PerformedBy = `System Automation`
             - Comments = `"Automated breach alert triggered."`
           - **Action: Send Email (`Alert_Escalation_Manager`)**
             - Urgent notification dispatched to designated escalation role.
     - **If No (Within Deadline):**
       - **Condition (`Check_Approaching_Deadline`):**
         - Expression:
           ```json
           greaterOrEquals(
               utcNow(),
               addHours(items('Process_Each_Active_Case')?['TargetDueDateTime'], sub(0, int(first(outputs('Get_Policy_For_Case')?['body/value'])?['WarningThresholdHours'])))
           )
           ```
         - **If Yes (Approaching):**
           - Send reminder email / Teams ping to `items('Process_Each_Active_Case')?['AssignedAnalyst/Email']`.

---

## 6. Flow CF-05: Record Status Change (Audit Ledger)

- **Flow Type:** Automated cloud flow
- **Trigger:** SharePoint — *When an item is modified*
  - **List Name:** `ComplianceRequests`
  - **Trigger Condition:**
    ```
    @and(
        not(equals(triggerOutputs()?['body/Status/Value'], 'Submitted')),
        not(equals(triggerOutputs()?['body/Status/Value'], 'Pending Approval')),
        not(equals(triggerOutputs()?['body/Status/Value'], 'Closed'))
    )
    ```
- **Action:** Writes a generic `Status Changed` entry to `RequestAuditLog` when operational status moves between active states (e.g. `Under Review` $\leftrightarrow$ `Escalated`).

---

## 7. Flow CF-06: Process Case Closure

- **Flow Type:** Automated cloud flow
- **Trigger:** SharePoint — *When an item is modified*
  - **List Name:** `ComplianceRequests`
  - **Trigger Condition:**
    ```
    @equals(triggerOutputs()?['body/Status/Value'], 'Closed')
    ```

### Action-by-Action Build Sequence:
1. **Action: Condition (`Validate_Closure_Metadata`)**
   - Check if `triggerOutputs()?['body/CompletionDateTime']` is empty.
   - **If Empty:**
     - Update `ComplianceRequests`: Set `CompletionDateTime = utcNow()`.
2. **Action: SharePoint — Create Item (`Write_Closed_AuditLog`)**
   - List Name: `RequestAuditLog`
   - Fields:
     - `Title`: `triggerOutputs()?['body/RequestID']`
     - `AuditID`: `int(ticks(utcNow()))`
     - `Timestamp`: `utcNow()`
     - `ActionType`: `Closed`
     - `PerformedBy`: `triggerOutputs()?['body/Editor/DisplayName']`
     - `OldStatus`: `triggerOutputs()?['body/Status/Value']`
     - `NewStatus`: `Closed`
     - `Comments`: `concat('Case archived. Closure notes: ', triggerOutputs()?['body/ClosureNotes'])`
3. **Action: Send Email (`Send_Final_Closure_Notice`)**
   - Informs submitter that the compliance inquiry has officially finalized and archived.
