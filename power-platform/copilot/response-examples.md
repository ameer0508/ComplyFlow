# Ask ComplyFlow — Conversational Response Examples & Grounded Scenarios

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Response Templates & Grounded Dialogue Reference
**Phase:** 7 (AI-Assisted Compliance Operations & Copilot Integration)
**Status:** Validated Grounded Response Reference

---

## 1. Overview of Response Structure

Every response produced by "Ask ComplyFlow" follows a structured template:
1. **Direct Answer:** Immediate, clear answer to the user's specific prompt.
2. **Authoritative Evidence:** Exact figures, database views, or policy clauses supporting the answer.
3. **Context / Operational Significance:** Practical explanation of what the numbers mean for compliance operations.
4. **Suggested Next Step (If applicable):** Explicitly watermarked `[AI Suggested Next Step - Requires Human Verification]`.

---

## 2. Nine Governed Dialogue Scenarios

### Scenario 1: Overdue Cases Inquiry
* **User Query:** *"How many overdue cases are there?"*
* **Intent:** `Query.ActiveOverdueCases`
* **Underlying Retrieval:** `SELECT COUNT(*) FROM vw_active_backlog WHERE SLAState = 'Overdue';`
* **Assistant Response:**
> **Direct Answer:** There are currently **24 overdue cases** in the synthetic dataset.
>
> **Evidence & Context:**
> - Source: `vw_active_backlog` evaluated against the baseline simulation anchor timestamp (`2026-09-26 17:00:00`).
> - This represents **48.0%** of the total 50 active cases in the backlog.
> - By process area, overdue cases are concentrated in KYC Operations (8 cases), Customer Onboarding (6 cases), and AML Operations (5 cases).
>
> **[AI Suggested Next Step - Requires Human Verification]:**
> Filter the Page 4 Case Detail table by `Overdue Status` to triage the 24 cases in order of earliest target due date.

---

### Scenario 2: Active Backlog Scale
* **User Query:** *"How many active cases do we have?"*
* **Intent:** `Query.ActiveBacklogTotal`
* **Underlying Retrieval:** `SELECT COUNT(*) FROM ComplianceRequest WHERE Status != 'Closed';`
* **Assistant Response:**
> **Direct Answer:** There are currently **50 active compliance cases** in the ComplyFlow system.
>
> **Evidence & Breakdown:**
> - Source: `ComplianceRequest` table (cases where `Status <> 'Closed'`).
> - Breakdown by workflow status:
>   - Under Review: **18**
>   - Pending Approval: **8**
>   - Submitted: **6**
>   - Escalated: **6**
>   - Approved (awaiting archival closure): **5**
>   - Draft: **4**
>   - Rejected (awaiting post-decision closure): **3**

---

### Scenario 3: SLA Policy Clarification (Critical Tier)
* **User Query:** *"What is the SLA for a Critical case?"*
* **Intent:** `Query.SLAPolicyExplanation`
* **Underlying Retrieval:** `SELECT * FROM SLAPolicy WHERE RiskLevel = 'Critical';`
* **Assistant Response:**
> **Direct Answer:** For **Critical risk** requests, the governing SLA policy mandates:
>
> - **SLA Target Turnaround:** **24 hours** from initial submission.
> - **Warning Threshold:** **6 hours** prior to breach (at 18 hours elapsed, case enters warning state).
> - **Mandatory Approval:** **Required (Yes)** — must be reviewed and signed off by a senior authority.
> - **Default Escalation Role:** **Head of Compliance**.
>
> *Note: SLA policies are set by compliance governance and cannot be modified by analysts or this assistant.*

---

### Scenario 4: High and Critical Active Backlog
* **User Query:** *"How many High and Critical active cases exist?"*
* **Intent:** `Query.HighCriticalActive`
* **Underlying Retrieval:** `SELECT RiskLevel, COUNT(*) FROM vw_active_backlog WHERE RiskLevel IN ('High', 'Critical') GROUP BY RiskLevel;`
* **Assistant Response:**
> **Direct Answer:** There are currently **15 active High and Critical risk cases**.
>
> **Evidence & Breakdown:**
> - **Critical Risk Active:** **7 cases** (24-hour turnaround target).
> - **High Risk Active:** **8 cases** (72-hour turnaround target).
> - Source: `vw_active_backlog`. Together, these 15 cases account for **30.0%** of all active operational workload and carry the highest exposure to regulatory scrutiny.

---

### Scenario 5: Compliance Request Summarization (Real Case: `CR-2026-0014`)
* **User Query:** *"Summarize compliance request CR-2026-0014."*
* **Intent:** `Case.Summarize`
* **Underlying Retrieval:** `ComplianceRequest` and `RequestAuditLog` for `CR-2026-0014`
* **Assistant Response:**
> ### Case Dossier: CR-2026-0014
>
> - **Title:** KYC Review - Zephyr Commercial Freight
> - **Process Area:** KYC Operations
> - **Request Type:** KYC Review
> - **Risk Level:** **Critical** (24-hour turnaround target)
> - **Priority:** Critical
> - **Current Status:** **Escalated**
> - **Assigned Analyst:** Chen Wei
> - **Submission Time:** 2026-09-15 04:15:29
> - **Target Due Date:** 2026-09-16 04:15:29
> - **SLA State:** 🔴 **Overdue** (Elapsed beyond 24h deadline)
> - **Governance Controls:** Approval Required: Yes | Escalation Flag: Active (1)
>
> **Recent Audit Milestones:**
> - `2026-09-15 03:32` — Drafted by James Wilson.
> - `2026-09-15 04:15` — Formally submitted; SLA clock started.
> - `2026-09-15 05:04` — Assigned to analyst Chen Wei; moved to Under Review.
> - `2026-09-15 08:59` — System Automation triggered escalation to Head of Compliance.
>
> **Outstanding Action:** Awaiting resolution from senior compliance leadership.
>
> **[AI Suggested Next Step - Requires Human Verification]:**
> Follow up directly with the Head of Compliance to review outstanding documentation for Zephyr Commercial Freight, as this Critical case has breached its 24-hour target.

---

### Scenario 6: Chronological Audit History Explanation (Real Case: `CR-2026-0001`)
* **User Query:** *"Explain the audit history for request CR-2026-0001."*
* **Intent:** `Audit.ExplainHistory`
* **Underlying Retrieval:** `SELECT * FROM RequestAuditLog WHERE RequestID = 'CR-2026-0001' ORDER BY Timestamp ASC;`
* **Assistant Response:**
> **Audit Timeline for CR-2026-0001 (Policy Exception - Boreal Energy Holdings):**
>
> 1. **Creation (2026-07-05 19:00:54):** Request was drafted by requester Claire Dupont.
> 2. **Submission (2026-07-05 20:56:54):** Claire Dupont formally submitted the request; the 120-hour Medium risk SLA clock began.
> 3. **Assignment (2026-07-05 21:52:54):** Assigned to compliance analyst Chen Wei; status updated to 'Under Review'.
> 4. **Approval (2026-07-07 23:23:55):** Analyst Chen Wei completed the investigation and recorded outcome: 'Approved'. Total investigation took ~50.5 hours.
> 5. **Closure (2026-07-08 20:37:12):** Case archived and closed by Chen Wei with notes: "Review successfully concluded and verified under Policy & Governance standards."
>
> **Summary Outcome:** The case was completed and closed in **71.67 hours**, safely within its 120-hour SLA target (`SLABreachFlag = 0`).

---

### Scenario 7: Escalation Root Cause Query (Real Case: `CR-2026-0014`)
* **User Query:** *"Why was case CR-2026-0014 escalated?"*
* **Intent:** `Case.ExplainEscalation`
* **Underlying Retrieval:** `SELECT EscalationReason, EscalatedTo FROM ComplianceRequest WHERE RequestID = 'CR-2026-0014';`
* **Assistant Response:**
> **Direct Answer:** Case **CR-2026-0014** was escalated on **2026-09-15 at 08:59:02** by **System Automation** to the **Head of Compliance**.
>
> **Recorded Escalation Reason:**
> *"Automated escalation: Target SLA turnaround breached."*
>
> **Context:**
> Because this is a Critical risk case, automated workflow rules routed the file directly to executive oversight when progress stalled during initial review.

---

### Scenario 8: Process Areas with Active Workload
* **User Query:** *"What process areas currently have active workload?"*
* **Intent:** `Query.ActiveWorkloadByArea`
* **Underlying Retrieval:** `SELECT ProcessArea, COUNT(*) FROM ComplianceRequest WHERE Status != 'Closed' GROUP BY ProcessArea ORDER BY COUNT(*) DESC;`
* **Assistant Response:**
> **Direct Answer:** Active workload is distributed across all 5 operational compliance areas:
>
> 1. **KYC Operations:** **17 active cases** (34.0% of backlog)
> 2. **Customer Onboarding:** **13 active cases** (26.0% of backlog)
> 3. **AML Operations:** **11 active cases** (22.0% of backlog)
> 4. **Policy & Governance:** **5 active cases** (10.0% of backlog)
> 5. **Sanctions:** **4 active cases** (8.0% of backlog)
>
> **Total Active Workload:** **50 cases**.

---

### Scenario 9: Operational Friction & Investigation Areas
* **User Query:** *"What operational areas should management investigate for bottlenecks?"*
* **Intent:** `Insights.IdentifyFriction`
* **Underlying Retrieval:** `vw_process_area_performance` and `vw_request_performance`
* **Assistant Response:**
> **Descriptive Operational Observations:**
>
> Based on analysis of the synthetic compliance dataset, three specific operational areas exhibit potential process friction:
>
> 1. **AML Resolution Duration:**
>    Completed AML Operations cases have the highest average turnaround time across the platform at **80.12 hours** (compared to the platform average of 69.27 hours).
>    *Area for Investigation:* Management could examine whether transaction inquiry complexity or external correspondent banking delays are driving extended cycle times.
>
> 2. **KYC Backlog Volume:**
>    KYC Operations holds the largest single share of active cases (**17 of 50 active cases**, or 34.0%).
>    *Area for Investigation:* Operational leads could review team capacity and analyst distribution within the KYC Review Team.
>
> 3. **Approval Dependency Dwell Time:**
>    A total of **70 requests** carry mandatory dual-tier approval requirements.
>    *Area for Investigation:* Management could explore whether cases spend disproportionate time in the 'Pending Approval' queue waiting for supervisory sign-off.
>
> *Disclaimer: These observations represent analytical areas for managerial review and do not constitute definitive statements of procedural failure.*
