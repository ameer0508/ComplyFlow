# ComplyFlow Power BI Quality Assurance & Manual Test Plan

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Microsoft Power BI Quality Assurance & Data Verification
**Phase:** 6 (Executive Analytics & DAX Modelling)
**Status:** Verification Protocol (Desktop Testing Ready)

---

## 1. Test Objectives & Strategy

The purpose of this test plan is to provide a rigorous, repeatable manual verification protocol to validate that the ComplyFlow Power BI reporting layer faithfully reconciles against the verified SQLite database (`database/complyflow.db`) and synthetic dataset (`data/raw/`).

### Test Coverage Areas
1. **Core KPI Cards & Aggregates Reconciliation**
2. **SLA & Resolution Time Metrics**
3. **Categorical Breakdown Accuracy (Process Area, Risk, Request Type)**
4. **Active vs Historical Segmentation**
5. **Interactive Filtering & Slicer Integrity**
6. **Drill-Through Functionality**
7. **Edge Cases & Anomaly Detection**

---

## 2. Test Execution Matrix with Verified Baseline Expectations

| Test ID | Metric / Visual Under Test | Report Page | Test Step | Verified Expected Value | Pass / Fail Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Total Requests KPI | Page 1 (P1-C1) | View card with no slicers applied | **`150`** | Must equal exactly 150 |
| **TC-02** | Closed Requests Count | Page 1 / 3 | DAX measure evaluation (`Status = "Closed"`) | **`100`** | Must equal exactly 100 |
| **TC-03** | Active Backlog KPI | Page 1 (P1-C2) | View card with no slicers applied (`Status <> "Closed"`) | **`50`** | Must equal exactly 50 |
| **TC-04** | Overdue Cases KPI | Page 1 (P1-C3) | Evaluate at anchor `2026-09-26 17:00` | **`24`** | Must equal exactly 24 |
| **TC-05** | Approaching Deadline KPI| Page 1 (P1-C4) | Evaluate at anchor `2026-09-26 17:00` | **`0`** | Must equal exactly 0 |
| **TC-06** | On Track Cases Count | Page 1 | Calculate `[Active] - [Overdue] - [Appr]`| **`26`** | Must equal exactly 26 |
| **TC-07** | SLA Breach Rate KPI | Page 1 / 3 | Ratio: `[SLA Breached] / [Closed]` | **`12.0%`** (12 / 100) | Must equal exactly 12.0% |
| **TC-08** | Average Resolution Time | Page 1 / 3 | Average duration of 100 closed cases | **`69.27 hrs`** | Must equal 69.27 ± 0.05 hrs |
| **TC-09** | Median Resolution Time | Page 3 | Median duration of 100 closed cases | **`44.79 hrs`** | Must equal 44.79 ± 0.05 hrs |
| **TC-10** | Escalated Cases KPI | Page 1 / 2 | Count where `EscalationFlag = 1` | **`17`** | Must equal exactly 17 |
| **TC-11** | Approval Required Cases | Page 1 / 2 | Count where `ApprovalRequired = 1` | **`70`** | Must equal exactly 70 |
| **TC-12** | High/Critical Active | Page 2 | Active cases with Risk High/Critical | **`15`** (Crit: 7, High: 8) | Must equal exactly 15 |

---

## 3. Dimensional Breakdown Verification Matrix

### 3.1 Process Area Total Volume Verification

| Process Area | Total Requests Expected | Closed Cases Expected | Active Backlog Expected | Closed SLA Breaches | Avg Res Time (Closed) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **AML Operations** | `41` | `30` | `11` | `4` (13.3%) | `80.12 hrs` |
| **Customer Onboarding** | `40` | `27` | `13` | `2` (7.4%) | `67.89 hrs` |
| **KYC Operations** | `36` | `19` | `17` | `3` (15.8%) | `55.70 hrs` |
| **Sanctions** | `18` | `14` | `4` | `2` (14.3%) | `77.19 hrs` |
| **Policy & Governance** | `15` | `10` | `5` | `1` (10.0%) | `55.19 hrs` |
| **Total** | **`150`** | **`100`** | **`50`** | **`12`** (12.0%) | **`69.27 hrs`** |

### 3.2 Risk Tier Total Volume Verification

| Risk Level | Total Requests Expected | Closed Cases Expected | Active Backlog Expected | Closed SLA Breaches | Closed Breach Rate |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Medium** | `55` | `32` | `23` | `2` | `6.3%` |
| **High** | `45` | `37` | `8` | `5` | `13.5%` |
| **Low** | `32` | `20` | `12` | `4` | `20.0%` |
| **Critical** | `18` | `11` | `7` | `1` | `9.1%` |
| **Total** | **`150`** | **`100`** | **`50`** | **`12`** | **`12.0%`** |

### 3.3 Active Backlog Status Breakdown

| Status | Active Count Expected | Operational Meaning |
| :--- | :--- | :--- |
| **Under Review** | `18` | Primary investigation in progress by compliance analyst |
| **Pending Approval** | `8` | Investigation complete; formal sign-off pending |
| **Submitted** | `6` | Newly submitted into intake queue; unassigned / triage pending |
| **Escalated** | `6` | Exception / risk alert raised to management lead |
| **Approved** | `5` | Approved by supervisor; awaiting administrative closure |
| **Draft** | `4` | Saved draft undergoing preliminary requester edits |
| **Rejected** | `3` | Investigation rejected; awaiting post-decision documentation |
| **Total Active** | **`50`** | Reconciles to `[Active Backlog]` (`Status <> 'Closed'`) |

---

## 4. Interactive & Functional Test Procedures

### 4.1 Test Procedure TP-01: Process Area Slicer Cross-Filtering
1. Navigate to **Page 2 (Operational Workload)**.
2. Select **`AML Operations`** in the Process Area slicer.
3. Verify that the **Active Backlog** visual filters down to **`11`** cases.
4. Verify that the **Compliance Team** chart displays only **`AML Operations Team`**.
5. Deselect to restore all 50 cases.

### 4.2 Test Procedure TP-02: Overdue Triage Filtering on Page 4
1. Navigate to **Page 4 (Case / Operational Detail)**.
2. Filter the table to active cases where `TargetDueDateTime < 2026-09-26 17:00:00`.
3. Verify that exactly **`24`** rows are returned.
4. Inspect the top rows: verify they show earliest deadlines first.
5. Confirm that no closed cases (`Status = 'Closed'`) appear in this overdue triage list.

### 4.3 Test Procedure TP-03: Drill-Through to Request Audit History
1. On **Page 4**, locate request `CR-00001`.
2. Right-click on row `CR-00001` -> select **Drill-through -> Request Audit History**.
3. Verify that the landing page displays only audit records for `CR-00001`.
4. Verify that chronological transition timestamps match between `FactComplianceRequests` and `FactAuditLog`.
5. Click the Power BI back arrow button to return to Page 4.

---

## 5. Discrepancy Investigation Protocol

If any card or visual displays values differing from this test plan during manual build:

1. **Check Anchor Timestamp:** Ensure DAX overdue measures use `DATETIME(2026, 9, 26, 17, 0, 0)` rather than dynamic `NOW()`. Dynamic evaluation against the current system date will flag all historical synthetic cases as overdue!
2. **Check Closed Status Filters:** Verify that completed SLA measures explicitly filter on `Status = "Closed"`.
3. **Verify Relationship Cross-Filtering:** Confirm that relationships between `DimDate`, `DimSLAPolicy`, and `FactComplianceRequests` are single direction.
4. **Compare Directly to SQLite:** Run the verified verification script to inspect raw ground truth:
   ```powershell
   python database/verify_database.py
   ```
