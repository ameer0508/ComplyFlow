# Power Automate Workflow Test Plan

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** Cloud Flow Functional Test Cases & Validation Protocol
**Phase:** 5 Quality Assurance Specification
**Execution Context:** Manual Verification in Microsoft Power Automate Studio

---

## 1. Overview & Verification Strategy

Because no live Microsoft 365 or Power Automate environment is connected locally, this document establishes the protocol for verifying cloud flows once constructed in Power Automate Studio.

- **Designed / Manual Test:** Detailed scenarios, trigger payloads, step-by-step actions, and expected outputs documented for execution in Power Automate Test mode (*"Manually"* or *"With recently used trigger data"*).
- **Live Cloud Behavior:** Untested until a genuine Microsoft 365 development tenant is provisioned.

---

## 2. Test Case Matrix (15 Scenarios)

| Test ID | Flow ID | Test Scenario | Trigger Payload / Action | Expected Result | Pass Criteria |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **TC-01** | `CF-01` | **New Request Intake** | Create item in `ComplianceRequests` with `Status = Submitted`, `RiskLevel = Medium`. | Flow triggers immediately. Calculates `TargetDueDateTime = SubmissionDateTime + 120h`. Stamps `ApprovalRequired = No`. | Record updated with target deadline. |
| **TC-02** | `CF-01` | **SLA Policy Lookup** | Create item with `RiskLevel = High`. | Flow executes `Get_SLAPolicy` and retrieves `SLATargetHours = 72`, `ApprovalMandatory = Yes`. | Exact parameters mapped from `SLAPolicies`. |
| **TC-03** | `CF-01` | **Target Deadline Math** | Submit request at `2026-10-01 10:00:00` with `Critical` risk. | `TargetDueDateTime` set to exactly `2026-10-02 10:00:00` (+24 calendar hours). | Zero date rounding error. |
| **TC-04** | `CF-02` | **Analyst Assignment Alert**| Edit request: populate `AssignedAnalyst` with a valid user profile. | Flow triggers. Dispatches Outlook email notification to analyst with case summary. | Email received in analyst inbox. |
| **TC-05** | `CF-02` | **Assignment Audit Event** | Edit request: assign to analyst. | New record created in `RequestAuditLog`: `ActionType = Assigned`, `OldStatus = Submitted`, `NewStatus = Under Review`. | Audit record verified in list. |
| **TC-06** | `CF-03` | **High-Risk Approval Route**| Update case: `Status = Pending Approval`, `RiskLevel = High`. | Flow routes approval card to Compliance Team Lead (`teamlead.compliance@...`). | Adaptive card delivered to Team Lead. |
| **TC-07** | `CF-03` | **Critical-Risk Route** | Update case: `Status = Pending Approval`, `RiskLevel = Critical`. | Flow routes approval card to Head of Compliance (`head.compliance@...`). | Adaptive card delivered to Head of Compliance. |
| **TC-08** | `CF-03` | **Approval Sign-off** | Approver clicks *Approve* in Teams card with comment: *"Approved per policy."* | Status becomes `Approved`. `ApprovedBy` and `ApprovalDate` stamped. Audit log created (`ActionType = Approved`). | Outcome recorded cleanly. |
| **TC-09** | `CF-03` | **Approval Rejection** | Approver clicks *Reject* with comment: *"Insufficient UBO evidence."* | Status becomes `Rejected`. Audit log created (`ActionType = Rejected`). Denial notification sent to submitter. | Case marked rejected with notes. |
| **TC-10** | `CF-04` | **Approaching SLA Alert** | Case has 4 hours remaining (within 6h warning threshold for Critical). Run CF-04 recurrence. | Flow identifies case inside warning threshold. Sends reminder ping to assigned analyst. | Warning email sent; case remains on track. |
| **TC-11** | `CF-04` | **SLA Breach Escalation** | Case has passed `TargetDueDateTime` without closure. Run CF-04 recurrence. | Sets `EscalationFlag = Yes`, `SLABreachFlag = Yes`, `EscalatedTo = Role`. Creates `Escalated` audit log. Alerts supervisor. | Escalation metadata and alert generated. |
| **TC-12** | `CF-04` | **Escalation Idempotency**| Case is already overdue and already has `EscalationFlag = Yes`. Run CF-04 recurrence again. | Condition detects `EscalationFlag == true`. Case is bypassed. No duplicate email or audit entry created. | Zero duplicate escalation events. |
| **TC-13** | `CF-05` | **Status Change Audit** | Reassign case from `Under Review` to `Escalated` manually. | CF-05 triggers and creates `RequestAuditLog` entry with `ActionType = Status Changed`. | Audit timeline reflects transition. |
| **TC-14** | `CF-06` | **Case Closure Stamping** | Update case: `Status = Closed`, `ClosureNotes = "Verification complete."` | CF-06 validates closure notes, stamps `CompletionDateTime = utcNow()`, and creates `Closed` audit record. | Terminal state enforced. |
| **TC-15** | `CF-01` | **Missing Policy Error** | Test item created with unmapped RiskLevel. | Flow enters `Scope_Catch`, logs failure alert to administrator, and cleanly terminates as `Failed`. | Controlled failure without infinite loop. |
