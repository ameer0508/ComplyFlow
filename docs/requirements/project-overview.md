# Project Requirements & Overview

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** Project Requirements Specification
**Version:** 1.0 (Phase 1 Baseline)

---

## 1. Problem Statement

Financial-services organizations face strict regulatory obligations requiring rapid, consistent, and thoroughly documented compliance handling. However, operational compliance workflows frequently suffer from severe manual inefficiencies:

- **Unstructured Intake Channels:** Operational requests (e.g., onboarding exceptions, KYC updates, sanctions screening queries) arrive through scattered emails, chats, and spreadsheets without required validation.
- **SLA Invisibility & Late Escalations:** Turnaround times are governed by strict Service Level Agreements (SLAs). Without centralized automated tracking, deadlines are tracked manually or missed, causing compliance breaches.
- **Labor-Intensive Status Chasing:** Team members waste valuable analytical capacity drafting repetitive status updates, reminder emails, and manual manager sign-offs.
- **Absence of Process Intelligence:** Operational managers lack unified metrics regarding queue velocity, stage duration, and individual analyst capacity, preventing data-driven process optimization.

ComplyFlow provides a lightweight, automated, and explainable prototype demonstrating how modern low-code tools (Microsoft Power Platform) paired with core data analytics (SQL and Python) eliminate these operational bottlenecks.

---

## 2. Target Users

| User Persona | Role & Responsibilities | Key Needs in ComplyFlow |
| :--- | :--- | :--- |
| **Operational Requester** | Front-office staff, onboarding specialist, or client relationship manager submitting a compliance review. | Simple, structured submission form; clear status visibility; automated confirmation notifications. |
| **Compliance Analyst** | Investigates cases, reviews documentation, evaluates risk, and recommends approval/rejection. | Centralized workload queue; automated deadline countdowns; clear case priority indicators. |
| **Compliance Team Lead / Manager** | Supervises analyst queue, reassigns cases, handles escalations, and approves high-risk items. | Notification of approaching breaches; one-click approval workflows; team capacity balancing. |
| **Head of Compliance / Leadership** | Accountable for regulatory compliance adherence and operational efficiency. | High-level KPI dashboards; bottleneck analysis; trend visibility across request types. |

---

## 3. Main Use Cases

1. **UC-01: Standardized Request Submission**
   - Requester submits a case specifying request category, business entity, urgency rationale, and supporting details. Form enforces required inputs before submission.
2. **UC-02: Risk-Weighted Priority Triage & SLA Calculation**
   - System categorizes risk level (*Low, Medium, High, Critical*) and automatically stamps a target resolution timestamp based on predefined SLA business rules.
3. **UC-03: Automated Analyst Assignment & Notification**
   - Case is routed to the designated compliance queue. An automated notification alert is generated for the assigned analyst.
4. **UC-04: Automated Deadline Reminders & Escalations**
   - Automated workflow checks pending cases. If a case enters the final 24 hours of its SLA window without closure, a reminder is triggered. If breached, the case is flagged and escalated to management.
5. **UC-05: Review, Multi-Tier Approval, & Closure**
   - Analyst completes their findings. If high risk, a management approval request is triggered via workflow. Once approved/rejected, the case is closed with an audit log timestamp.
6. **UC-06: Operational Performance & Bottleneck Analysis**
   - Operational data is processed and aggregated via SQL queries to track volume trends, average turnaround time, SLA breach percentage, and stage-by-stage dwell time.

---

## 4. MVP Scope Definition

The Minimum Viable Product (MVP) focuses on a single, end-to-end, high-integrity business journey:

```
[Requester]
   ↓
1. Submit Compliance Request (Intake via Power Apps Form)
   ↓
2. Capture Structured Record (SharePoint Online List)
   ↓
3. Assess Priority & Calculate SLA (Automated Rule-based Stamping)
   ↓
4. Assign Analyst & Send Notification (Power Automate Workflow)
   ↓
5. Track Deadline & Monitor SLA Countdown
   ↓
6. Conduct Review & Document Findings (Analyst Queue)
   ↓
7. Trigger Approval / Escalation (Manager Sign-off if High Risk)
   ↓
8. Close Request & Record Completion Metrics
   ↓
9. Extract & Analyze Operational Data (SQL Queries + Python Validation)
   ↓
10. Render Process Intelligence Dashboard (Power BI KPIs)
```

### Core MVP Deliverables:
- **Intake & Store:** Documented schema for a centralized compliance request store with validated fields.
- **Workflow Triggers:** Documented logic for submission confirmation, reminder thresholds, and manager escalation.
- **Synthetic Dataset:** A realistic tabular dataset reflecting 100+ simulated compliance cases across different stages, categories, and SLA states.
- **Data Quality Pipeline:** Python script to validate record integrity (date logic, non-null constraints, SLA calculation accuracy).
- **Analytical Query Pack:** SQL scripts calculating core operational metrics (SLA breach rate, open backlog by risk, analyst capacity).
- **Management Reporting Model:** Power BI dashboard layout delivering executive visibility into operational throughput and bottlenecks.

---

## 5. Out-of-Scope Functionality (Non-Goals)

To keep the platform realistic, beginner-friendly, and easy to explain during an apprentice/junior interview, the following elements are explicitly **out of scope**:

- ❌ **Predictive Machine Learning / AI Risk Scoring:** No statistical machine learning models or black-box predictions. Risk is evaluated via transparent, rule-based business logic.
- ❌ **Custom Backend APIs & Microservices:** No unnecessary microservice architectures, custom Express/Django API layers, or distributed queues.
- ❌ **Direct Integration with Core Banking / Trading Engines:** No real-time connections to live trade booking, SWIFT messaging, or banking ledger systems.
- ❌ **Real Customer or Proprietary Data Processing:** Zero real-world PII, client identities, or proprietary corporate data.
- ❌ **Custom Identity & Authentication Infrastructure:** No bespoke OAuth/OpenID servers; relies strictly on standard Microsoft 365 identity primitives in production.
