# Power Apps Compliance Operations Interface

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Microsoft Power Apps Canvas App Specification
**Phase:** 4 (User Experience & Screen Architecture)
**Status:** Specification & Reference Design (Studio Build Ready)

---

## 1. Executive Purpose & Architectural Role

The **ComplyFlow Power Apps Canvas App** is the primary operational interface for financial-services compliance operations. It provides a structured, responsive, and role-aware workspace for:
1. Front-office and onboarding personnel submitting regulatory review requests.
2. Compliance analysts investigating cases, recording findings, and managing daily task queues.
3. Compliance managers reviewing high-risk cases, authorizing approvals, and monitoring escalations.

### Architectural Context
```
[ Operational Requester / Analyst / Manager ]
                      │
                      ▼
       [ ComplyFlow Power Apps Canvas App ]
                      │
                      ▼ (Direct Read / Patch Operations)
         [ SharePoint Online Lists ]
           • ComplianceRequests
           • RequestAuditLog
           • SLAPolicies
                      │
                      ▼ (Background Triggers & SLA Automation)
         [ Microsoft Power Automate ] (Phase 5)
                      │
                      ▼ (Analytics & Management Reporting)
         [ SQL Engine & Power BI ] (Phase 2C & Phase 6)
```

> **Live Environment Status:** As established in Phase 0–3, no active Microsoft 365 or Power Apps development tenant is connected in the local environment. This document and its accompanying build specification provide a comprehensive, step-by-step implementation specification for manual construction within Power Apps Studio.

---

## 2. Screen Architecture Overview

The application is structured into **six dedicated operational screens**:

```
ComplyFlow Canvas App
├── 1. scr_Home              (Command Center & Operational Metric Tiles)
├── 2. scr_NewRequest        (Intake Form & Client-Side Validation)
├── 3. scr_MyQueue           (Analyst Personal Worklist & Deadline Sorting)
├── 4. scr_AllRequests       (Operational Browser with Multi-Filter Slicers)
├── 5. scr_RequestDetails    (Segmented 360° Case View & Audit History)
└── 6. scr_CaseUpdate        (Authorized Status Transitions & Resolution Notes)
```

### Screen Summary & Capabilities

| Screen Name | Target Persona | Primary Business Purpose |
| :--- | :--- | :--- |
| **`scr_Home`** | All Users | High-level operational overview: dynamic KPI tiles (Active, Overdue, Approvals, My Cases) and direct navigation. |
| **`scr_NewRequest`** | Requester / Operations | Clean intake form capturing essential metadata with client-side required-field validation. |
| **`scr_MyQueue`** | Compliance Analyst | Personal workbench displaying cases assigned to `User().Email`, sorted by urgent SLA deadlines. |
| **`scr_AllRequests`** | Analyst / Team Lead | Comprehensive operational case browser with combined search, process-area, status, and risk filters. |
| **`scr_RequestDetails`** | Analyst / Manager | Full case dossier partitioned into: Overview, Risk & Priority, Ownership, SLA Countdown, Approvals, Escalations, and the `RequestAuditLog` gallery. |
| **`scr_CaseUpdate`** | Assigned Analyst / Manager| Controlled modification screen enforcing valid lifecycle state transitions, analyst assignment, and closure notes. |

---

## 3. Data Sources & Integration Model

The app is designed to bind directly to the three SharePoint lists specified in Phase 3:

| Data Source Name | SharePoint List Reference | Read/Write Usage in App |
| :--- | :--- | :--- |
| **`ComplianceRequests`** | `Lists/ComplianceRequests` | **Primary Data Source.** Forms read records, gallery queues filter items, and `Patch()` statements write updates. |
| **`RequestAuditLog`** | `Lists/RequestAuditLog` | **Read-Only in App.** Filtered by `RequestID` on `scr_RequestDetails` to render chronological audit history. *(Official writes handled by Power Automate)*. |
| **`SLAPolicies`** | `Lists/SLAPolicies` | **Lookup Collection.** Cached locally on `App.OnStart` to look up `SLATargetHours` and `WarningThresholdHours` without repeated network calls. |

---

## 4. Core Power Fx Logic & Formulas

### A. Dynamic SLA State Classification (Presentation Layer)
Rather than writing an unstable static column, the app calculates current SLA health dynamically for any active request:

```powerfx
// Formula: Deriving SLA State in Gallery Item Cards
If(
    ThisItem.Status = "Closed",
    "Completed",
    Now() > ThisItem.TargetDueDateTime,
    "Overdue",
    DateDiff(Now(), ThisItem.TargetDueDateTime, TimeUnit.Hours) <= LookUp(col_SLAPolicies, RiskLevel = ThisItem.RiskLevel, WarningThresholdHours),
    "Approaching Deadline",
    "On Track"
)
```

### B. "My Queue" Personal Filtering
Delegation-conscious filtering that isolates cases assigned to the logged-in analyst:

```powerfx
// Items property for gal_MyQueue
SortByColumns(
    Filter(
        ComplianceRequests,
        Status <> "Closed",
        AssignedAnalyst.Email = User().Email || AssignedAnalystEmail = User().Email
    ),
    "TargetDueDateTime",
    SortOrder.Ascending
)
```

### C. Multi-Criteria Search & Filter ("All Requests")
Combines text search with three distinct dropdown filters using delegation-friendly clauses:

```powerfx
// Items property for gal_AllRequests
SortByColumns(
    Filter(
        ComplianceRequests,
        (IsBlank(txt_SearchBox.Text) ||
            StartsWith(RequestID, txt_SearchBox.Text) ||
            StartsWith(Title, txt_SearchBox.Text)),
        (cmb_FilterStatus.Selected.Value = "All" || Status = cmb_FilterStatus.Selected.Value),
        (cmb_FilterRisk.Selected.Value = "All" || RiskLevel = cmb_FilterRisk.Selected.Value),
        (cmb_FilterProcessArea.Selected.Value = "All" || ProcessArea = cmb_FilterProcessArea.Selected.Value)
    ),
    "TargetDueDateTime",
    SortOrder.Ascending
)
```

### D. Controlled Request Submission (`Patch`)
Executes atomic creation with client-side required field guards:

```powerfx
// OnSelect property of btn_SubmitNewRequest
If(
    IsBlank(txt_NewTitle.Text) || IsBlank(cmb_NewRequestType.Selected.Value) ||
    IsBlank(cmb_NewProcessArea.Selected.Value) || IsBlank(cmb_NewRiskLevel.Selected.Value) ||
    IsBlank(txt_NewDescription.Text),
    Notify("Please complete all mandatory fields marked with an asterisk (*).", NotificationType.Error),

    // Set busy state & perform write
    Set(varIsSubmitting, True);
    With(
        {
            varMatchedPolicy: LookUp(col_SLAPolicies, RiskLevel = cmb_NewRiskLevel.Selected.Value)
        },
        Patch(
            ComplianceRequests,
            Defaults(ComplianceRequests),
            {
                Title: txt_NewTitle.Text,
                RequestType: { Value: cmb_NewRequestType.Selected.Value },
                ProcessArea: { Value: cmb_NewProcessArea.Selected.Value },
                RiskLevel: { Value: cmb_NewRiskLevel.Selected.Value },
                Priority: { Value: Coalesce(cmb_NewPriority.Selected.Value, cmb_NewRiskLevel.Selected.Value) },
                Status: { Value: "Submitted" },
                Description: txt_NewDescription.Text,
                RequesterName: User().FullName,
                RequesterEmail: User().Email,
                RequesterDepartment: { Value: cmb_NewDepartment.Selected.Value },
                ComplianceTeam: { Value: "Financial Crime Compliance" },
                SubmissionDateTime: Now(),
                SLATargetHours: varMatchedPolicy.SLATargetHours,
                TargetDueDateTime: DateAdd(Now(), varMatchedPolicy.SLATargetHours, TimeUnit.Hours),
                ApprovalRequired: varMatchedPolicy.ApprovalMandatory,
                SLABreachFlag: false,
                EscalationFlag: false,
                CreatedDate: Now(),
                ModifiedDate: Now()
            }
        )
    );
    Notify("Compliance request successfully submitted!", NotificationType.Success);
    Navigate(scr_Home, ScreenTransition.Cover)
)
```

---

## 5. Lifecycle Transition Guards

To guarantee data integrity, `scr_CaseUpdate` enforces strict state validation:
1. **Assignment Guard:** Case cannot move from `Submitted` to `Under Review` unless `AssignedAnalyst` is selected.
2. **Approval Route Guard:** High or Critical risk cases cannot move directly from `Under Review` to `Approved`—they must transition to `Pending Approval`.
3. **Closure Completeness:** Case cannot transition to `Closed` unless `ClosureNotes` is populated.
4. **Terminal Finality:** Closed cases are strictly read-only; the update button is disabled (`DisplayMode.Disabled`).

---

## 6. Role-Aware Experience & Visual Design

- **Professional Financial-Services Palette:** Built on deep navy (`#1B365D`), subtle slate backgrounds (`#F4F6F9`), clean white card containers, and standard compliance status accents (Overdue = Crimson `#D9383A`, Approaching = Amber `#F5A623`, On Track = Emerald `#2E7D32`).
- **Role Awareness:**
  - *Requesters* see intake options and track their own submissions.
  - *Analysts* see assigned workload and active triage tools.
  - *Managers* see dedicated approval badges and escalation indicators.
