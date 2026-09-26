# Power Automate Compliance Workflow & Automation

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Microsoft Power Automate Cloud Flow Architecture
**Phase:** 5 (Workflow Orchestration & Governance Automation)
**Status:** Implementation Specification & Reference Design (Manual Build Ready)

---

## 1. Executive Purpose & Architectural Role

In the ComplyFlow platform architecture, **Microsoft Power Automate** provides the **event-driven orchestration and business logic tier**. It eliminates manual chasing, enforces regulatory SLA tracking, handles multi-tier management approvals, and guarantees immutable milestone audit logging:

```
[ Power Apps UI ]
       │ (Item Created / Modified)
       ▼
[ SharePoint Online: ComplianceRequests ]
       │
       ▼ (Event Triggers & Recurrence)
[ Microsoft Power Automate (6 Core Cloud Flows) ]
  ├── CF-01: Process New Compliance Request  (SLA Stamping & Confirmation)
  ├── CF-02: Track Case Assignment           (Analyst Notification & Assignment Audit)
  ├── CF-03: Route Compliance Approval       (Adaptive Card Approval & Sign-off Audit)
  ├── CF-04: Monitor Compliance SLA          (Scheduled Warning Alerts & Escalation)
  ├── CF-05: Record Status Change            (Milestone Lifecycle Audit Ledger)
  └── CF-06: Process Case Closure            (Final Validation & Terminal Stamping)
       │
       ▼ (Writes Milestones & Updates)
[ SharePoint: RequestAuditLog & Analytics Layer ]
```

> **Live Environment Status:** As established in previous phases, no authenticated Microsoft 365 or Power Automate development tenant is connected in the local environment. This documentation provides a comprehensive, step-by-step implementation specification for manual configuration in Power Automate. No fake cloud flows, flow IDs, or connection references have been fabricated.

---

## 2. Consolidated Flow Inventory

To avoid fragile micro-flows and minimize trigger execution overhead, automation is consolidated into **six high-cohesion, auditable cloud flows**:

| Flow ID | Flow Name | Trigger Type | Trigger Event / Recurrence | Primary Business Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **`CF-01`** | **Process New Request** | Automated | *When an item is created* in `ComplianceRequests` | Looks up `SLAPolicies`, calculates `TargetDueDateTime`, stamps SLA hours, creates `Submitted` audit log, sends receipt email. |
| **`CF-02`** | **Track Case Assignment** | Automated | *When an item is modified* (`AssignedAnalyst` changes) | Validates non-null assignment, updates status to `Under Review`, dispatches analyst assignment alert, writes `Assigned` audit log. |
| **`CF-03`** | **Route Compliance Approval** | Automated | *When an item is modified* (`Status = 'Pending Approval'`) | Writes `Approval Requested` audit log, dispatches Power Automate Approval to designated role (Team Lead / Head of Compliance), processes outcome, stamps `ApprovedBy` and `ApprovalDate`. |
| **`CF-04`** | **Monitor Compliance SLA** | Scheduled | Recurrence: Daily at 08:00 UTC | Evaluates active cases: sends reminder for approaching deadlines, triggers automated escalation for overdue cases (idempotent; no duplicate re-escalations). |
| **`CF-05`** | **Record Status Change** | Automated | *When an item is modified* (`Status` changes) | Records milestone lifecycle transitions in `RequestAuditLog` for general status changes not handled by specialized approval flows. |
| **`CF-06`** | **Process Case Closure** | Automated | *When an item is modified* (`Status = 'Closed'`) | Validates `ClosureNotes`, ensures `CompletionDateTime = utcNow()`, creates `Closed` audit log, locks record from further workflow edits. |

---

## 3. Power Automate Expressions & SLA Calculation Logic

### A. Target Deadline Calculation (CF-01)
Adds policy-allocated calendar hours directly to the submission timestamp:
```json
addHours(
    triggerOutputs()?['body/SubmissionDateTime'],
    int(outputs('Get_Matching_SLAPolicy')?['body/SLATargetHours'])
)
```

### B. Pre-Deadline Warning Window Calculation (CF-04)
Calculates the exact timestamp threshold when warning reminders must trigger:
```json
addHours(
    items('Apply_to_each_Active_Request')?['TargetDueDateTime'],
    sub(0, int(items('Apply_to_each_Active_Request')?['WarningThresholdHours']))
)
```

### C. Live vs. Simulation SLA State Evaluation
- **Phase 2B/2C Historical Simulation:** Used a deterministic fixed anchor `2026-09-26 17:00:00` to validate 150 synthetic records.
- **Production Power Automate Implementation:** Uses dynamic UTC clock `utcNow()` converted to standard organization timezone (e.g. `UTC` or `GMT Standard Time`):
```json
if(
    greater(utcNow(), items('Apply_to_each_Active_Request')?['TargetDueDateTime']),
    'Overdue',
    if(
        greaterOrEquals(
            utcNow(),
            addHours(items('Apply_to_each_Active_Request')?['TargetDueDateTime'], sub(0, int(items('Apply_to_each_Active_Request')?['WarningThresholdHours'])))
        ),
        'Approaching Deadline',
        'On Track'
    )
)
```

---

## 4. Idempotency & Loop Prevention Strategy

In SharePoint-triggered flows, updating a list item from within the flow can accidentally re-trigger `When an item is modified`, creating an infinite loop. ComplyFlow prevents this through three architectural controls:

1. **Trigger Conditions (Filter Expressions):**
   Flows only execute when explicit business conditions are met:
   - *CF-01 Trigger Condition:* `@equals(triggerOutputs()?['body/Status/Value'], 'Submitted')`
   - *CF-03 Trigger Condition:* `@and(equals(triggerOutputs()?['body/Status/Value'], 'Pending Approval'), equals(triggerOutputs()?['body/ApprovalRequired'], true))`
   - *CF-06 Trigger Condition:* `@equals(triggerOutputs()?['body/Status/Value'], 'Closed')`
2. **Escalation Idempotency Guard (CF-04):**
   Before flagging an overdue case, CF-04 checks:
   `@equals(items('Apply_to_each_Active_Request')?['EscalationFlag'], false)`.
   If already escalated, the case is bypassed.
3. **Audit Milestone Deduplication:**
   Each flow creates exactly one audit event corresponding to its primary lifecycle transition.

---

## 5. Notification Architecture

| Event | Recipient | Delivery Channel | Message Summary |
| :--- | :--- | :--- | :--- |
| **New Submission** | Submitter (`RequesterEmail`) | Outlook Email (V2) | Formal confirmation with `RequestID`, case summary, and calculated `TargetDueDateTime`. |
| **New Assignment** | Analyst (`AssignedAnalyst/Email`) | Outlook Email / Teams | Alert with priority badge, case category, and link to open `scr_RequestDetails` in Power Apps. |
| **Approval Requested**| Approver Role (Team Lead/Head) | Power Automate Approvals / Teams Card | Interactive Adaptive Card displaying risk narrative, counterparty details, and Approve/Reject buttons. |
| **Approval Outcome** | Requester & Analyst | Outlook Email (V2) | Notification of managerial sign-off or denial with comments. |
| **Approaching SLA** | Assigned Analyst | Teams Chat / Email | Early-warning reminder (e.g. 6h/24h remaining) to prevent breach. |
| **SLA Breach Escalated**| Escalation Role (`EscalatedTo`) | High-Priority Email / Teams | Urgent escalation alert detailing breached target deadline and operational dwell time. |

---

## 6. Error Handling & Resilience Patterns

All cloud flows implement structured Power Automate error handling:
- **`Scope_Try`:** Encapsulates core business actions (SharePoint updates, approval calls, audit log creation).
- **`Scope_Catch`:** Configured with `Configure Run After: has failed, has timed out`.
  - Dispatches an operational diagnostic email to `complyflow-admin@complyflow-demo.internal`.
  - Captures failed action name and error message via `result('Scope_Try')`.
  - Terminates the flow run as `Failed` with meaningful diagnostics.
- **Retry Policies:** SharePoint API calls use exponential backoff (`Count: 4`, `Interval: PT10S`).
