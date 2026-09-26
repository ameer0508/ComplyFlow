# ComplyFlow Canvas App: Step-by-Step Build Specification

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** Power Apps Studio Manual Construction Guide
**App Type:** Tablet / Responsive Desktop Canvas App (16:9)
**Phase:** 4 Implementation Specification

---

## 1. Global Setup & App OnStart Configuration

### Step 1.1: Create App & Connect Data Sources
1. Open [make.powerapps.com](https://make.powerapps.com).
2. Click **Create** $\to$ **Blank app** $\to$ **Blank canvas app**.
   - **App Name:** `ComplyFlow`
   - **Format:** `Tablet`
3. In the left navigation, click **Data** $\to$ **Add data** $\to$ Select **SharePoint**:
   - Site: `https://<tenant>.sharepoint.com/sites/ComplyFlow`
   - Select lists: **`ComplianceRequests`**, **`RequestAuditLog`**, **`SLAPolicies`**.

### Step 1.2: App `OnStart` Formula
Select **App** in the Tree View $\to$ In the formula bar, select property **`OnStart`**:
```powerfx
// Cache reference SLA policies into a global collection for instant lookup
ClearCollect(col_SLAPolicies, SLAPolicies);

// Set theme color palette tokens
Set(varThemeNavy, RGBA(27, 54, 93, 1));      // Primary Brand (#1B365D)
Set(varThemeSlate, RGBA(244, 246, 249, 1));  // Background (#F4F6F9)
Set(varThemeBorder, RGBA(224, 228, 234, 1)); // Card Borders
Set(varThemeCrimson, RGBA(217, 56, 58, 1));  // Overdue / Critical
Set(varThemeAmber, RGBA(245, 166, 35, 1));   // Approaching Deadline
Set(varThemeEmerald, RGBA(46, 125, 50, 1));  // On Track / Closed

// Initialize session state
Set(varCurrentUser, User());
```

---

## 2. Screen 1: `scr_Home` (Command Center)

**Purpose:** Executive operational cockpit giving analysts and managers real-time visibility into active queues, overdue risks, and personal workloads.

### Controls & Hierarchy:
- `con_HomeHeader` (Horizontal Container)
  - `lbl_HomeAppTitle` (Text: `"COMPLYFLOW"`)
  - `lbl_HomeUserGreeting` (Text: `"Welcome, " & varCurrentUser.FullName`)
- `con_HomeKPIContainer` (Horizontal Container)
  - `card_KPITotalActive` (Container - Border: 1px)
    - `lbl_ValTotalActive` (Text: `CountRows(Filter(ComplianceRequests, Status <> "Closed"))`)
    - `lbl_TitleTotalActive` (Text: `"Active Backlog"`)
  - `card_KPIOverdue` (Container - Border: 1px Crimson)
    - `lbl_ValOverdue` (Text: `CountRows(Filter(ComplianceRequests, Status <> "Closed" && (Now() > TargetDueDateTime || SLABreachFlag = true)))`)
    - `lbl_TitleOverdue` (Text: `"Overdue Cases"`)
  - `card_KPIPendingApproval` (Container - Border: 1px Amber)
    - `lbl_ValPendingApproval` (Text: `CountRows(Filter(ComplianceRequests, Status = "Pending Approval"))`)
    - `lbl_TitlePendingApproval` (Text: `"Pending Approval"`)
  - `card_KPIMyAssigned` (Container - Border: 1px Navy)
    - `lbl_ValMyAssigned` (Text: `CountRows(Filter(ComplianceRequests, Status <> "Closed" && (AssignedAnalyst.Email = varCurrentUser.Email || AssignedAnalystEmail = varCurrentUser.Email)))`)
    - `lbl_TitleMyAssigned` (Text: `"Assigned to Me"`)
- `con_HomeNavigation` (Vertical Container)
  - `btn_NavNewRequest` (Button: `"+ Submit New Compliance Request"`, `OnSelect`: `Navigate(scr_NewRequest, ScreenTransition.Fade)`)
  - `btn_NavMyQueue` (Button: `"Open My Working Queue"`, `OnSelect`: `Navigate(scr_MyQueue, ScreenTransition.Fade)`)
  - `btn_NavAllRequests` (Button: `"Browse All Operational Requests"`, `OnSelect`: `Navigate(scr_AllRequests, ScreenTransition.Fade)`)

---

## 3. Screen 2: `scr_NewRequest` (Intake Form)

**Purpose:** Guided intake form enforcing required data capture with immediate client-side validation.

### Controls & Hierarchy:
- `con_NewHeader` (Horizontal Container)
  - `btn_BackToHome` (Icon: Left Arrow, `OnSelect`: `Navigate(scr_Home, ScreenTransition.None)`)
  - `lbl_NewFormTitle` (Text: `"New Compliance Request Intake"`)
- `frm_NewComplianceRequest` (Edit Form / Group of Input Cards)
  - `txt_NewTitle` (Text Input, Required, HintText: `"Short summary of counterparty/review"`)
  - `cmb_NewRequestType` (Dropdown, `Items`: `Choices(ComplianceRequests.RequestType)`)
  - `cmb_NewProcessArea` (Dropdown, `Items`: `Choices(ComplianceRequests.ProcessArea)`)
  - `cmb_NewRiskLevel` (Dropdown, `Items`: `Choices(ComplianceRequests.RiskLevel)`, `Default`: `"Medium"`)
  - `cmb_NewPriority` (Dropdown, `Items`: `Choices(ComplianceRequests.Priority)`, `Default`: `cmb_NewRiskLevel.Selected.Value`)
  - `cmb_NewDepartment` (Dropdown, `Items`: `Choices(ComplianceRequests.RequesterDepartment)`)
  - `txt_NewDescription` (Text Input - Multiline, Required, Height: 120)
  - `con_NewSLAEstimateCard` (Container displaying calculated deadline):
    - `lbl_EstimatedSLA` (Text: `"Target Turnaround: " & LookUp(col_SLAPolicies, RiskLevel = cmb_NewRiskLevel.Selected.Value, SLATargetHours) & " Hours"`)
- `con_NewActionFooter` (Horizontal Container)
  - `btn_CancelNew` (Button: `"Cancel"`, `OnSelect`: `Navigate(scr_Home, ScreenTransition.Fade)`)
  - `btn_SubmitNew` (Button: `"Submit Request"`)
    - `OnSelect` formula:
      ```powerfx
      If(
          IsBlank(txt_NewTitle.Text) || IsBlank(cmb_NewRequestType.Selected.Value) ||
          IsBlank(cmb_NewProcessArea.Selected.Value) || IsBlank(cmb_NewRiskLevel.Selected.Value) ||
          IsBlank(txt_NewDescription.Text),
          Notify("Please complete all mandatory fields (*).", NotificationType.Error),

          With(
              {
                  varPol: LookUp(col_SLAPolicies, RiskLevel = cmb_NewRiskLevel.Selected.Value)
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
                      RequesterName: varCurrentUser.FullName,
                      RequesterEmail: varCurrentUser.Email,
                      RequesterDepartment: { Value: cmb_NewDepartment.Selected.Value },
                      ComplianceTeam: { Value: "Financial Crime Compliance" },
                      SubmissionDateTime: Now(),
                      SLATargetHours: varPol.SLATargetHours,
                      TargetDueDateTime: DateAdd(Now(), varPol.SLATargetHours, TimeUnit.Hours),
                      ApprovalRequired: varPol.ApprovalMandatory,
                      SLABreachFlag: false,
                      EscalationFlag: false,
                      CreatedDate: Now(),
                      ModifiedDate: Now()
                  }
              )
          );
          Notify("Case successfully logged in queue!", NotificationType.Success);
          Navigate(scr_Home, ScreenTransition.Cover)
      )
      ```

---

## 4. Screen 3: `scr_MyQueue` (Analyst Personal Worklist)

**Purpose:** Analyst-specific workbench prioritizing active tasks by earliest SLA deadline.

### Controls:
- `con_MyQueueHeader` (Title: `"My Assigned Queue"`)
- `txt_SearchMyQueue` (Text Input: Search by Title or Request ID)
- `cmb_FilterMyStatus` (Dropdown: `["All", "Under Review", "Pending Approval", "Escalated"]`)
- `gal_MyQueue` (Vertical Gallery):
  - `Items` property:
    ```powerfx
    SortByColumns(
        Filter(
            ComplianceRequests,
            Status <> "Closed",
            (AssignedAnalyst.Email = varCurrentUser.Email || AssignedAnalystEmail = varCurrentUser.Email),
            (IsBlank(txt_SearchMyQueue.Text) || StartsWith(RequestID, txt_SearchMyQueue.Text) || StartsWith(Title, txt_SearchMyQueue.Text)),
            (cmb_FilterMyStatus.Selected.Value = "All" || Status = cmb_FilterMyStatus.Selected.Value)
        ),
        "TargetDueDateTime",
        SortOrder.Ascending
    )
    ```
  - **Gallery Item Card Controls:**
    - `lbl_CardRequestID` (Text: `ThisItem.RequestID`)
    - `lbl_CardTitle` (Text: `ThisItem.Title`)
    - `lbl_CardProcessArea` (Text: `ThisItem.ProcessArea.Value`)
    - `badge_CardRisk` (Fill: `If(ThisItem.RiskLevel.Value="Critical", varThemeCrimson, varThemeNavy)`, Text: `ThisItem.RiskLevel.Value`)
    - `badge_CardSLAState` (Text derived dynamically):
      ```powerfx
      If(
          Now() > ThisItem.TargetDueDateTime, "OVERDUE",
          DateDiff(Now(), ThisItem.TargetDueDateTime, TimeUnit.Hours) <= LookUp(col_SLAPolicies, RiskLevel = ThisItem.RiskLevel.Value, WarningThresholdHours), "APPROACHING DEADLINE",
          "ON TRACK"
      )
      ```
      - `Fill`: `If(Now() > ThisItem.TargetDueDateTime, varThemeCrimson, DateDiff(Now(), ThisItem.TargetDueDateTime, TimeUnit.Hours) <= LookUp(col_SLAPolicies, RiskLevel = ThisItem.RiskLevel.Value, WarningThresholdHours), varThemeAmber, varThemeEmerald)`
    - `btn_OpenDetails` (Icon: Right chevron, `OnSelect`: `Set(varSelectedRequest, ThisItem); Navigate(scr_RequestDetails, ScreenTransition.Fade)`)

---

## 5. Screen 4: `scr_AllRequests` (Operational Case Browser)

**Purpose:** Master repository search browser for supervisors and analysts with multi-criteria filters.

### Controls:
- `con_FilterBar` (Horizontal Bar):
  - `txt_MasterSearch` (Text Input)
  - `cmb_MasterProcessArea` (`Items`: `["All", "Customer Onboarding", "AML Operations", "KYC Operations", "Sanctions", "Policy & Governance"]`)
  - `cmb_MasterRisk` (`Items`: `["All", "Critical", "High", "Medium", "Low"]`)
  - `cmb_MasterStatus` (`Items`: `["All", "Draft", "Submitted", "Under Review", "Pending Approval", "Escalated", "Approved", "Rejected", "Closed"]`)
- `gal_AllRequests` (Vertical Gallery):
  - `Items` property:
    ```powerfx
    SortByColumns(
        Filter(
            ComplianceRequests,
            (IsBlank(txt_MasterSearch.Text) || StartsWith(RequestID, txt_MasterSearch.Text) || StartsWith(Title, txt_MasterSearch.Text)),
            (cmb_MasterProcessArea.Selected.Value = "All" || ProcessArea.Value = cmb_MasterProcessArea.Selected.Value),
            (cmb_MasterRisk.Selected.Value = "All" || RiskLevel.Value = cmb_MasterRisk.Selected.Value),
            (cmb_MasterStatus.Selected.Value = "All" || Status.Value = cmb_MasterStatus.Selected.Value)
        ),
        "TargetDueDateTime",
        SortOrder.Ascending
    )
    ```
  - `OnSelect` (on item): `Set(varSelectedRequest, ThisItem); Navigate(scr_RequestDetails, ScreenTransition.Fade)`

---

## 6. Screen 5: `scr_RequestDetails` (360° Case Dossier)

**Purpose:** Complete read/review dossier displaying case facts, risk indicators, SLA countdown, approval trail, and audit ledger.

### Layout & Panels:
1. **Header Panel:**
   - Case Title, Request ID, and dynamic SLA status badge.
   - Action Buttons:
     - `btn_EditCase` (Visible: `varSelectedRequest.Status.Value <> "Closed"`, `OnSelect`: `Navigate(scr_CaseUpdate, ScreenTransition.Fade)`)
     - `btn_Back` (Icon: Back arrow, `OnSelect`: `Navigate(scr_Home, ScreenTransition.None)`)
2. **Section 1 — Case Information & Risk:**
   - Displays `RequestType`, `ProcessArea`, `RiskLevel`, `Priority`, `Description`, `RequesterName`, `RequesterDepartment`.
3. **Section 2 — SLA & Assignment:**
   - Displays `AssignedAnalyst`, `ComplianceTeam`, `SubmissionDateTime`, `TargetDueDateTime`, `SLATargetHours`.
   - Countdown Label:
     ```powerfx
     "Deadline: " & Text(varSelectedRequest.TargetDueDateTime, "dd mmm yyyy hh:mm") &
     " (" & Round(DateDiff(Now(), varSelectedRequest.TargetDueDateTime, TimeUnit.Minutes)/60, 1) & " hours remaining)"
     ```
4. **Section 3 — Approval & Escalation Status:**
   - If `ApprovalRequired = true`: Shows `ApprovedBy` and `ApprovalDate`.
   - If `EscalationFlag = true`: Shows `EscalatedTo` and `EscalationReason`.
5. **Section 4 — Audit History Ledger:**
   - `gal_AuditTimeline` (Gallery):
     - `Items`: `SortByColumns(Filter(RequestAuditLog, Title = varSelectedRequest.RequestID || RequestID = varSelectedRequest.RequestID), "Timestamp", SortOrder.Descending)`
     - Displays: `Timestamp`, `ActionType.Value`, `PerformedBy`, `OldStatus` $\to$ `NewStatus`, `Comments`.

---

## 7. Screen 6: `scr_CaseUpdate` (Authorized Operations)

**Purpose:** Allows analysts and managers to update operational state, assign cases, record approvals, or finalize closure notes.

### Controls:
- `lbl_UpdateHeader` (Text: `"Update Case: " & varSelectedRequest.RequestID`)
- `cmb_UpdateStatus` (Dropdown, `Items`: `Choices(ComplianceRequests.Status)`, `Default`: `varSelectedRequest.Status.Value`)
- `txt_UpdateAnalyst` (Person picker or email string)
- `txt_UpdateClosureNotes` (Multiline text input, Required if `cmb_UpdateStatus.Selected.Value = "Closed"`)
- `chk_UpdateEscalate` (Checkbox: `"Flag for Escalation"`, `Default`: `varSelectedRequest.EscalationFlag`)
- `txt_UpdateEscalationReason` (Visible: `chk_UpdateEscalate.Value = true`)
- `btn_SaveUpdate` (Button: `"Save Changes"`):
  - `OnSelect` formula:
    ```powerfx
    If(
        cmb_UpdateStatus.Selected.Value = "Closed" && IsBlank(txt_UpdateClosureNotes.Text),
        Notify("Closure notes are mandatory when closing a compliance case.", NotificationType.Error),

        Patch(
            ComplianceRequests,
            varSelectedRequest,
            {
                Status: { Value: cmb_UpdateStatus.Selected.Value },
                ClosureNotes: txt_UpdateClosureNotes.Text,
                CompletionDateTime: If(cmb_UpdateStatus.Selected.Value = "Closed", Now(), Blank()),
                EscalationFlag: chk_UpdateEscalate.Value,
                EscalationReason: txt_UpdateEscalationReason.Text,
                ModifiedDate: Now()
            }
        );
        Notify("Case updated successfully.", NotificationType.Success);
        Navigate(scr_Home, ScreenTransition.Cover)
    )
    ```
