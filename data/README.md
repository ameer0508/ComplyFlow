# ComplyFlow Datasets Guide

This directory houses all synthetic and reference datasets for the ComplyFlow platform.

---

## 🛡️ Synthetic Data Disclaimer
**ALL DATA IN THIS DIRECTORY IS 100% SYNTHETIC AND FICTIONAL.**
None of the records, entities, customer names, transactions, employee names, or operational issues represent real-world financial-services customer data, proprietary corporate information, or StoneX Group data. This data was generated exclusively for educational, development, and portfolio demonstration purposes.

---

## 📁 Dataset Catalog

### 1. `data/raw/compliance_requests.csv`
- **Purpose:** Primary operational request dataset modeling the full lifecycle of compliance cases.
- **Record Count:** Exactly 150 rows.
- **Simulation Time Horizon:** 90 Days (`2026-06-28 17:47:49` to `2026-09-26 07:52:46`).
- **Core Dimensions:**
  - `ProcessArea`: Customer Onboarding (40), AML Operations (41), KYC Operations (36), Sanctions (18), Policy & Governance (15).
  - `RequestType`: KYC Review (56), AML Transaction Inquiry (35), Sanctions Review (19), PEP Review (25), Policy Exception (15).
  - `RiskLevel`: Medium (55), High (45), Low (32), Critical (18).
  - `Status`: Closed (100), Under Review (18), Pending Approval (8), Submitted (6), Escalated (6), Approved (5), Draft (4), Rejected (3).
- **Operational SLA State (Simulation Reference Date: `2026-09-26 17:00:00`):**
  - **Closed Cases:** 100 (88 Met SLA, 12 SLA Breached).
  - **Active Open Cases:** 50
    - **Active Cases Currently Overdue:** 24 cases (Target due date has passed).
    - **Active Cases Approaching Deadline:** 0 cases (None currently in the pre-deadline warning window).
    - **Active Cases On Track:** 26 cases (Well within SLA target hours).

### 2. `data/raw/request_audit_log.csv`
- **Purpose:** Milestone audit trail capturing chronological lifecycle events for regulatory governance.
- **Record Count:** 716 milestone audit rows.
- **Action Types Logged:** `Created`, `Submitted`, `Assigned`, `Approval Requested`, `Approved`, `Rejected`, `Escalated`, `Closed`.

### 3. `data/raw/sla_policies.csv`
- **Purpose:** Standard SLA and governance rule matrix mapping risk tier to target turnaround hours, reminder thresholds, and approval requirements.
- **Record Count:** Exactly 4 rows (one per risk level).
- **SLA Parameters:**
  - `Critical`: 24 calendar hours, 6h warning, Mandatory Approval: Yes, Escalation: Head of Compliance.
  - `High`: 72 calendar hours, 24h warning, Mandatory Approval: Yes, Escalation: Compliance Team Lead.
  - `Medium`: 120 calendar hours, 24h warning, Mandatory Approval: No, Escalation: Operational Queue Manager.
  - `Low`: 240 calendar hours, 48h warning, Mandatory Approval: No, Escalation: Operations Supervisor.

---

## ⚙️ Data Generation & Validation Commands

### Reproducible Data Generation
To regenerate the exact synthetic datasets using the fixed random seed (`seed=42`):
```powershell
python analytics/scripts/generate_synthetic_data.py
```

### Data Quality & Integrity Validation
To run the full suite of business rule assertions, chronological checks, and foreign-key validation:
```powershell
python analytics/scripts/validate_data.py
```
*(Exits with code `0` on 100% compliance, or non-zero if discrepancies are discovered).*

---

## 📐 Core Business Rules Enforced in Data

1. **Deterministic SLA Deadline:**
   $$\text{TargetDueDateTime} = \text{SubmissionDateTime} + \text{SLATargetHours}$$
2. **Derived Resolution Time:**
   `ResolutionTimeHours` is not stored as a static source column in the raw CSV. It is dynamically computed in analytical views and DAX as `CompletionDateTime - SubmissionDateTime` for closed records.
3. **Audit Chronology:**
   Every compliance request maintains a strictly monotonic sequence of audit timestamps:
   $$\text{CreatedDate} \le \text{SubmissionDateTime} \le \text{AssignDateTime} \le \text{ApprovalDate} \le \text{CompletionDateTime}$$
4. **Mandatory Sign-off:**
   `High` and `Critical` cases enforce `ApprovalRequired = 1` and require an approving manager name and timestamp prior to case closure.
