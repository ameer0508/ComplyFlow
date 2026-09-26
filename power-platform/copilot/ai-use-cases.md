# Ask ComplyFlow — AI Use Cases & Capability Specifications

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Functional AI Capability Specifications
**Phase:** 7 (AI-Assisted Compliance Operations & Copilot Integration)
**Status:** Validated Functional Specification

---

## 1. Capability 1: Natural-Language KPI & Analytics Queries

This capability allows compliance leadership and operational supervisors to query core performance metrics using conversational language. Responses must ground strictly in governed SQL views and Power BI DAX measures, avoiding speculative or unverified aggregates.

### Governed Question Catalog (Synthetic Baseline Grounding)

#### Query 1.1: Active Backlog Scale
* **User Question:** *"How many active compliance requests are currently in the system?"*
* **Authoritative Data Source:** `vw_active_backlog` (SQLite) / `[Active Backlog]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM ComplianceRequest WHERE Status != 'Closed';` / `CALCULATE(COUNTROWS(FactComplianceRequests), FactComplianceRequests[Status] <> "Closed")`
* **Expected Grounded Answer:** **`50 active cases`** (Synthetic Dataset)
* **Contextual Explanation:** "There are currently 50 active compliance requests requiring operational handling across all process areas. The active cases consist of Under Review (18), Pending Approval (8), Submitted (6), Escalated (6), Approved (5), Draft (4), and Rejected (3)."

---

#### Query 1.2: Overdue Regulatory Cases
* **User Question:** *"How many compliance cases are currently overdue?"*
* **Authoritative Data Source:** `vw_active_backlog` (SQLite) / `[Overdue Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM vw_active_backlog WHERE SLAState = 'Overdue';` (Evaluated relative to simulation anchor: `2026-09-26 17:00:00`)
* **Expected Grounded Answer:** **`24 overdue cases`** (Synthetic Dataset)
* **Contextual Explanation:** "Relative to the baseline reference time of 2026-09-26 17:00:00, exactly 24 active cases (48.0% of the active backlog) have exceeded their target due date. These represent immediate triage priorities for queue managers."

---

#### Query 1.3: Cases Approaching SLA Deadlines
* **User Question:** *"How many cases are approaching their SLA warning deadline?"*
* **Authoritative Data Source:** `vw_active_backlog` (SQLite) / `[Approaching Deadline Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM vw_active_backlog WHERE SLAState = 'Approaching Deadline';`
* **Expected Grounded Answer:** **`0 cases`** (Synthetic Dataset)
* **Contextual Explanation:** "There are currently 0 cases in the synthetic dataset whose remaining time falls strictly within their policy warning threshold without already having breached the final deadline."

---

#### Query 1.4: Historical SLA Breach Rate
* **User Question:** *"What is our historical SLA breach rate on completed compliance cases?"*
* **Authoritative Data Source:** `vw_request_performance` (SQLite) / `[SLA Breach Rate]` (Power BI)
* **Underlying SQL / DAX:** `SELECT ROUND(AVG(SLABreachFlag)*100.0, 2) FROM ComplianceRequest WHERE Status = 'Closed';`
* **Expected Grounded Answer:** **`12.0%`** (12 breaches out of 100 closed cases)
* **Contextual Explanation:** "Historically, 88 completed cases (88.0%) met their SLA targets, while 12 completed cases (12.0%) breached regulatory turnaround times. The target enterprise benchmark is < 5.0%."

---

#### Query 1.5: Cases Requiring Governance Approval
* **User Question:** *"How many total cases require mandatory management approval?"*
* **Authoritative Data Source:** `ComplianceRequest` (SQLite) / `[Approval Required Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM ComplianceRequest WHERE ApprovalRequired = 1;`
* **Expected Grounded Answer:** **`70 cases`** (Synthetic Dataset)
* **Contextual Explanation:** "Out of the 150 total requests in the synthetic dataset, 70 cases (46.7%) carry mandatory dual-tier sign-off requirements under policy governance rules."

---

#### Query 1.6: Escalation Volume
* **User Question:** *"How many requests have been escalated?"*
* **Authoritative Data Source:** `ComplianceRequest` (SQLite) / `[Escalated Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM ComplianceRequest WHERE EscalationFlag = 1;`
* **Expected Grounded Answer:** **`17 cases`** (Synthetic Dataset)
* **Contextual Explanation:** "A total of 17 cases (11.3% of all requests) have triggered formal escalation during their lifecycle. Of these, 6 cases remain actively unresolved in the 'Escalated' queue."

---

#### Query 1.7: Operational Cycle Time
* **User Question:** *"What is our average turnaround time for resolving compliance requests?"*
* **Authoritative Data Source:** `vw_request_performance` (SQLite) / `[Average Resolution Time]` (Power BI)
* **Underlying SQL / DAX:** `SELECT ROUND(AVG(ResolutionTimeHours), 2) FROM vw_request_performance WHERE Status = 'Closed';`
* **Expected Grounded Answer:** **`69.27 hours`** (Arithmetic Mean) / **`44.79 hours`** (Median)
* **Contextual Explanation:** "Across all 100 closed cases, the average resolution time is 69.27 hours. The median resolution time is 44.79 hours, indicating that a minority of high-complexity investigations skewed the arithmetic mean upward."

---

#### Query 1.8: Workload Concentration by Process Area
* **User Question:** *"Which process areas have active operational workload?"*
* **Authoritative Data Source:** `vw_active_backlog` (SQLite)
* **Underlying SQL / DAX:** `SELECT ProcessArea, COUNT(*) FROM vw_active_backlog GROUP BY ProcessArea ORDER BY COUNT(*) DESC;`
* **Expected Grounded Answer:**
  - KYC Operations: **`17 active cases`**
  - Customer Onboarding: **`13 active cases`**
  - AML Operations: **`11 active cases`**
  - Policy & Governance: **`5 active cases`**
  - Sanctions: **`4 active cases`**
* **Contextual Explanation:** "All 5 compliance process areas currently maintain active cases in the synthetic dataset, with KYC Operations and Customer Onboarding together accounting for 60.0% of the active queue."

---

#### Query 1.9: High and Critical Risk Backlog
* **User Question:** *"How many High and Critical risk cases are currently active?"*
* **Authoritative Data Source:** `vw_active_backlog` (SQLite) / `[High/Critical Active Cases]` (Power BI)
* **Underlying SQL / DAX:** `SELECT COUNT(*) FROM vw_active_backlog WHERE RiskLevel IN ('High', 'Critical');`
* **Expected Grounded Answer:** **`15 active cases`** (`Critical` = 7, `High` = 8)
* **Contextual Explanation:** "There are currently 15 high-exposure cases in the active backlog (30.0% of all active items). These require expedited review in accordance with executive SLA policies."

---

## 2. Capability 2: AI-Assisted Case Summarization

### 2.1 Purpose & Guardrails
Enables compliance officers to generate an instantaneous 30-second dossier on any compliance case by synthesizing tabular request fields and historical audit milestones.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CASE SUMMARY: CR-2026-0014                      │
├────────────────────────────────────────────────────────────────────────┤
│ Title:            KYC Review - Zephyr Commercial Freight               │
│ Process Area:     KYC Operations             Request Type: KYC Review  │
│ Risk Level:       Critical (24h SLA)         Priority:     Critical    │
│ Current Status:   Escalated                  Analyst:      Chen Wei    │
│ SLA Target:       2026-09-16 04:15:29        SLA State:    🔴 Overdue  │
│ Governance:       Approval Required: Yes     Escalated:    Yes         │
├────────────────────────────────────────────────────────────────────────┤
│ Key Milestones:                                                        │
│ • 2026-09-15 03:32 — Drafted by James Wilson                          │
│ • 2026-09-15 04:15 — Submitted to intake queue; SLA clock initialized │
│ • 2026-09-15 05:04 — Assigned to investigator Chen Wei                │
│ • 2026-09-15 08:59 — System Automation escalated case to Head of      │
│                      Compliance due to SLA turnaround breach           │
├────────────────────────────────────────────────────────────────────────┤
│ Outstanding Action: Case awaiting senior management review & sign-off  │
│                                                                        │
│ [AI Suggested Next Step - Requires Human Verification]:                │
│ "Contact Head of Compliance to prioritize final disposition, as case   │
│ is past its 24-hour Critical SLA deadline."                            │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Prohibited Autonomous Actions
The AI assistant must NEVER execute or imply authority for any of the following:
* Approving or rejecting a case
* Closing or archiving a request
* Modifying assigned risk levels or SLA target dates
* Altering historical audit trail logs
* Reassigning analysts autonomously

---

## 3. Capability 3: Audit History Narrative Explanation

### 3.1 Chronological Event Synthesis
Converts sequential `RequestAuditLog` entries into a natural-language narrative for audit inspections and supervisory reviews.

* **Factual Grounding Rule:** The assistant narrates strictly recorded timestamps, actors, and state transitions. It will never interpolate or fabricate unrecorded phone calls, verbal approvals, or undocumented meetings.
* **Incomplete Record Handling:** If an audit trail has truncated steps or lacks closure notes, the assistant must explicitly append:
  > *"Insufficient recorded information to determine why this state transition occurred."*

---

## 4. Capability 4: SLA Policy & Governance Explanation

The assistant interprets and explains the governing SLA framework (`SLAPolicy`) to ensure consistent understanding across operational teams:

| Risk Tier | SLA Target | Warning Window | Mandatory Approval | Default Escalation Role |
| :--- | :---: | :---: | :---: | :--- |
| **Critical** | 24 hours | 6 hours | **Yes** | Head of Compliance |
| **High** | 72 hours | 24 hours | **Yes** | Compliance Team Lead |
| **Medium** | 120 hours | 24 hours | **No** | Operational Queue Manager |
| **Low** | 240 hours | 48 hours | **No** | Operations Supervisor |

### Natural-Language Policy Queries:
* *"What is the SLA target for a Critical case?"*
  → **Response:** "Under ComplyFlow policy, Critical risk cases have an SLA resolution target of 24 hours, enter the warning state 6 hours prior to breach, require mandatory dual approval, and escalate directly to the Head of Compliance."
* *"Who receives escalations for High-risk requests?"*
  → **Response:** "High-risk cases escalate to the Compliance Team Lead."

---

## 5. Capability 5: Operational Insight Generation

Produces factual, descriptive observations derived from verified database aggregates without making subjective, politicized, or unfounded assertions.

### 5.1 Factual Separation Framework

| Unacceptable Speculative Output (NOT ALLOWED) | Approved Factual Output (REQUIRED) |
| :--- | :--- |
| ❌ *"KYC Operations is failing and poorly managed."* | 🟢 *"KYC Operations currently maintains 17 active requests in the synthetic dataset, representing the largest single queue concentration (34.0% of total active backlog)."* |
| ❌ *"Analysts are intentionally ignoring overdue cases."* | 🟢 *"In the synthetic dataset, 24 active cases have surpassed their target due date relative to the evaluation anchor timestamp."* |
| ❌ *"The SLA breach rate will double next month."* | 🟢 *"Historical closed cases exhibit a 12.0% SLA breach rate (12 of 100 cases). Future volume projections are not modeled."* |

---

## 6. Capability 6: Process Improvement & Bottleneck Hypotheses

Surfaces analytical observations as **hypotheses and areas for managerial exploration**, rather than proven causal facts.

### 6.1 Framed Managerial Hypotheses
1. **Approval Workflow Dwell Time:**
   *"Observation: 70 requests carry mandatory approval requirements. Management could explore whether the approval stage accounts for a disproportionate share of total cycle time."*
2. **High-Risk Investigation Complexity:**
   *"Observation: Critical cases exhibit an average resolution time of 14.40 hours (against a 24-hour target), while Low-risk cases average 147.31 hours. Management could investigate if low-risk cases are intentionally deprioritized during queue congestion."*
3. **Escalation Trigger Clustering:**
   *"Observation: All 6 active escalated requests are in either KYC Operations or Policy & Governance. Compliance leadership could review intake screening quality for these specific process areas."*
