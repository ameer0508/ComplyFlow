# Power Apps Operational Test Plan

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** Functional Test Cases & Validation Script
**Phase:** 4 Quality Assurance Specification
**Execution Context:** Manual Verification in Microsoft Power Apps Studio

---

## 1. Overview & Testing Strategy

Because no live Microsoft 365 or Power Apps connection exists in the local environment, this test plan documents the exact manual test scenarios, inputs, and expected outcomes to be verified once the app is constructed in Power Apps Studio.

---

## 2. Test Case Matrix (13 Scenarios)

| Test ID | Test Scenario | Steps / Action | Expected Result | Pass Criteria |
| :---: | :--- | :--- | :--- | :--- |
| **TC-01** | **Required-Field Validation** | On `scr_NewRequest`, leave `Title` or `Description` blank and click *Submit*. | Red error notification banner: *"Please complete all mandatory fields (*)"*. No record written to SharePoint. | Submission blocked. |
| **TC-02** | **Successful Submission** | Populate all fields: Title = *"Test Review"*, Type = *KYC*, Area = *Customer Onboarding*, Risk = *High*. Click *Submit*. | Success notification banner displayed. Record patched to `ComplianceRequests` with `Status = Submitted`. Form navigates to `scr_Home`. | Record exists in SharePoint list. |
| **TC-03** | **Invalid Form Handling** | Enter special characters or excessively long strings (>500 chars) in single-line title. | Form enforces character bounds; prevents UI overflow. | Clean UI handling. |
| **TC-04** | **Keyword Search** | On `scr_AllRequests`, type a specific RequestID (e.g. `"CR-2026-0012"`) into `txt_MasterSearch`. | Gallery filters instantly to display only the matching record. | Single record returned. |
| **TC-05** | **Status Filter** | On `scr_AllRequests`, select `Status = "Pending Approval"`. | Gallery displays only requests currently in `Pending Approval` status. | Zero closed or draft cases displayed. |
| **TC-06** | **Risk Level Filter** | On `scr_AllRequests`, select `RiskLevel = "Critical"`. | Gallery filters to show only Critical risk tier records. | Only Critical cases displayed. |
| **TC-07** | **Process Area Filter** | On `scr_AllRequests`, select `ProcessArea = "Sanctions"`. | Gallery isolates only Sanctions department cases. | Only Sanctions records shown. |
| **TC-08** | **"My Queue" Scoping** | Open `scr_MyQueue` as logged-in analyst. | Gallery evaluates `AssignedAnalyst.Email = User().Email` and displays only personal cases. | Excludes cases assigned to other analysts. |
| **TC-09** | **SLA State Calculation** | View case cards with past due date vs future due date. | Cases where `Now() > TargetDueDateTime` render Crimson badge `"OVERDUE"`. Cases within warning threshold render Amber `"APPROACHING"`. Others render Emerald `"ON TRACK"`. | Badge colors & text match SLA policy rules. |
| **TC-10** | **Invalid Status Transition** | On `scr_CaseUpdate`, attempt to select `Status = "Approved"` for a `Critical` risk case without manager sign-off. | UI prevents bypass, enforcing routing to `Pending Approval`. | Direct approval blocked. |
| **TC-11** | **Closed Case Immutability** | Open a case with `Status = "Closed"` on `scr_RequestDetails`. | `btn_EditCase` is hidden or disabled (`DisplayMode.Disabled`). Terminal status prevents further edits. | No edit controls accessible. |
| **TC-12** | **Audit Trail Gallery** | On `scr_RequestDetails`, scroll to the Audit History section. | `gal_AuditTimeline` displays chronological milestones linked by `RequestID` (e.g., Created $\to$ Submitted $\to$ Assigned $\to$ Closed). | Complete milestone timeline rendered. |
| **TC-13** | **Role-Based Experience** | Log in as Requester vs Compliance Manager. | Requester cannot see Manager sign-off controls; Manager sees approval action buttons on `Pending Approval` cases. | Segregation of duties respected. |
