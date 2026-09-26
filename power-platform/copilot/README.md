# Ask ComplyFlow — AI-Assisted Compliance Intelligence Layer

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Microsoft Copilot & Practical AI Intelligence Specification ("Ask ComplyFlow")
**Phase:** 7 (AI-Assisted Compliance Operations & Copilot Integration)
**Status:** Architecture & Prototype Specification (Design Ready / Non-Deployed Reference)

---

## 1. Executive Purpose & Positioning

**"Ask ComplyFlow"** is an AI-assisted compliance intelligence assistant designed to support compliance analysts, queue managers, and executive leadership by providing intuitive, natural-language interaction with governed compliance operational data, regulatory SLA policies, and case audit histories.

In high-stakes financial compliance environments, operational data is often fragmented across intake queues, workflow approvals, and analytical reports. "Ask ComplyFlow" solves this by translating complex regulatory metrics, multi-stage case progressions, and SLA exposure into contextual, accessible insights.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        "Ask ComplyFlow" Assistant                      │
│       Natural-Language Explanations, Triage Guidance & Insights       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Read-Only Governed Data Retrieval)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      Authoritative Systems of Record                   │
│                                                                        │
│   [ Power BI Layer ]      [ SQLite Analytical Views ]   [ SLA Policies ]
│    • 14 DAX Measures       • vw_request_performance     • 4 Risk Tiers
│    • Star-Schema Facts     • vw_active_backlog          • Escalation Roles
│                                                                        │
│   [ SharePoint / Power Apps ]            [ Immutable Audit Trail ]     │
│    • 150 Compliance Requests              • 716 RequestAuditLog Events │
└────────────────────────────────────────────────────────────────────────┘
```

### Core Architecture Tenet: AI is NEVER the System of Record
1. **Assistance, Not Decision-Making:** "Ask ComplyFlow" assists compliance professionals with analysis, summarization, and query navigation; it **never** replaces human compliance judgment or makes autonomous regulatory decisions.
2. **Authoritative Sources:** All facts, timestamps, SLA statuses, and metrics originate from governed operational and analytical layers (SQLite, SharePoint, Power BI, and SLA policies). The AI layer stores no persistent case state.
3. **Zero Autonomous Mutation:** The assistant has read-only access. It cannot approve, reject, escalate, reassign, or alter any compliance request or audit entry.
4. **Transparent Source Grounding:** Every answer cites its governing source (e.g., SQLite view, DAX measure, audit entry, or policy rule).

> **Deployment Reality Disclosure:** In accordance with project governance standards, no live Microsoft Copilot Studio, Azure OpenAI, OpenAI API, or Power Platform AI Builder tenant has been deployed or queried. This component is a verified reference design and prototype specification.

---

## 2. Six Core AI Capabilities

| Capability | Business Focus | Primary Source Grounding | Key Behavior |
| :--- | :--- | :--- | :--- |
| **1. Natural Language KPI Questions** | Rapid executive query answering without navigating dashboards | Power BI DAX Measures / SQL Views | Retrieves exact verified metrics (e.g., 50 active, 24 overdue, 12% breach rate) |
| **2. Case Summarization** | 30-second operational briefings on complex compliance files | `ComplianceRequest` & `RequestAuditLog` | Structured summaries highlighting status, SLA health, and AI-suggested next steps |
| **3. Audit History Explanation** | Plain-language chronological timeline narrative | `RequestAuditLog` (716 rows) | Summarizes status changes; explicitly says *"Insufficient recorded information"* if data is missing |
| **4. SLA Policy Explanation** | Clarifies SLA targets, warning windows, and escalation tiers | `SLAPolicy` (4 tiers) | Explains policy rules without altering thresholds |
| **5. Operational Insight Generation** | Identifies queue concentrations and capacity friction | `vw_process_area_performance`, `vw_risk_performance` | Purely descriptive factual observations (e.g., KYC has 17 active cases) without unsupported bias |
| **6. Process Improvement Assistance** | Surfaces hypotheses for workflow bottleneck investigations | Historical resolution distributions | Frames observations as questions and areas for managerial exploration |

---

## 3. Implementation Tiers: From Conceptual Prototype to Enterprise

ComplyFlow structures its AI roadmap across three distinct governance tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 1: Conceptual Prototype & Reference Design (Current Project State)│
│ • Local Python / SQL grounding against verified complyflow.db          │
│ • Strict deterministic prompt templates & mock dialogue verification   │
│ • 0 external API calls; 100% offline data privacy                      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Roadmap Progression)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 2: Microsoft Power Platform & Copilot Studio (Future Staging)    │
│ • Custom Copilot configured in Microsoft Copilot Studio                │
│ • Connectors to SharePoint Online Lists & Power BI Certified Datasets  │
│ • Power Automate flows executing parameterized read-only queries       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Enterprise Scale)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 3: Enterprise Production AI Governance (Target Production State) │
│ • Azure OpenAI Service with private VNet endpoints and CMEK            │
│ • Entra ID RBAC role-level data trimming (matching user clearance)     │
│ • Complete audit logging of all AI prompts, grounding context, and outputs│
│ • Data Loss Prevention (DLP) enforcing strict zero-retention policies  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. AI Governance & The "Human-in-the-Loop" Principle

> **Core Principle:** *"AI assists compliance professionals; it does not replace compliance judgment."*

1. **No Autonomous Approvals:** A human analyst must review all case materials and sign off on approvals, rejections, or closures.
2. **Defensible Grounding:** The assistant will not hallucinate facts. If requested details are absent from the audit trail or request record, the system explicitly reports incomplete records.
3. **Segregation of Duties:** AI-generated recommendations are explicitly tagged with `[AI Suggested Next Step - Requires Human Verification]`.

---

## 5. Artifact Navigation

* [power-platform/copilot/copilot-build-spec.md](copilot-build-spec.md) — Comprehensive technical implementation guide for Copilot Studio and Power Platform integration.
* [power-platform/copilot/ai-use-cases.md](ai-use-cases.md) — Detailed operational use cases, user personas, prompt flows, and data mapping.
* [power-platform/copilot/guardrails.md](guardrails.md) — Enterprise safety guardrails, prompt defense, and source-grounded hallucination controls.
* [power-platform/copilot/response-examples.md](response-examples.md) — Realistic dialogue examples grounded strictly in the verified Phase 2B/2C dataset.
* [power-platform/copilot/test-plan.md](test-plan.md) — 15 comprehensive quality assurance and boundary test scenarios.
* [power-platform/copilot/copilot-schema.json](copilot-schema.json) — Structured JSON definition of intents, entities, topics, and grounding queries.
* [docs/architecture/ai-intelligence-flow.md](../../docs/architecture/ai-intelligence-flow.md) — Architectural data flow and context retrieval diagram.
