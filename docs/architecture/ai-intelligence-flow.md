# Ask ComplyFlow — AI Intelligence & Context Data Flow Architecture

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Document:** End-to-End AI Interaction & Retrieval Architecture
**Phase:** 7 Architecture Integration
**Status:** Validated Technical Architecture Specification

---

## 1. End-to-End Interaction & Context Flow

The "Ask ComplyFlow" assistant operates strictly as an analytical and conversational copilot above the operational and analytical layers. It implements a read-only **Retrieval-Augmented Generation (RAG)** pattern where every answer is anchored in governed enterprise records:

```mermaid
flowchart TD
    USER["Compliance Professional<br/>(Analyst / Supervisor / Executive)"]

    subgraph AICopilotLayer["Ask ComplyFlow Intelligence Tier (Read-Only)"]
        UI["Conversational Interface<br/>(Power Apps Embedded / Copilot Studio)"]
        GUARD_IN["Input Guardrails & Prompt Defense<br/>• Injection Mitigation<br/>• Scope Validation<br/>• PII Redaction Filter"]
        INTENT["Intent Classification & Entity Extraction<br/>• Identify Intent (KPI / Summary / Audit / Policy)<br/>• Extract Entities (RequestID, RiskTier, Area)"]
        CONTEXT["Context Assembly Engine<br/>• System Meta-Prompt<br/>• Governed Payload Grounding<br/>• Hallucination Control Constraints"]
        MODEL["Inference Engine<br/>(Local Prototype / Azure OpenAI GPT-4o)"]
        GUARD_OUT["Output Guardrails & Labeling<br/>• Verify Fact Grounding<br/>• Enforce '[AI Suggested Step]' Tag<br/>• Fact vs Opinion Segregation"]
    end

    subgraph DataStorageTier["Governed Authoritative Systems of Record (System of Truth)"]
        SP_DATA["SharePoint Lists / Power Apps<br/>• ComplianceRequests (150 rows)<br/>• RequestAuditLog (716 rows)"]
        SQL_VIEWS["SQLite Analytical Views<br/>• vw_active_backlog<br/>• vw_request_performance<br/>• vw_process_area_performance"]
        POLICY_DATA["SLA Policy Engine<br/>• SLAPolicy (4 Risk Tiers)"]
        PBI_MODEL["Power BI Model<br/>• 14 DAX Measures"]
    end

    subgraph HumanActionTier["Human Governance & Execution Tier"]
        HITL["Human Review & Decision-Making<br/>(Analyst verifies recommendations)"]
        ACTION["Optional Human-Controlled Action<br/>• Approve / Reject Case (in Power Apps)<br/>• Escalate to Management<br/>• Update Case Notes"]
    end

    %% User interaction flow
    USER -->|1. Natural Language Prompt| UI
    UI -->|2. Raw Utterance| GUARD_IN
    GUARD_IN -->|3. Validated Input| INTENT

    %% Governed Data Retrieval (Read-Only)
    INTENT -->|4. Parameterized Query Execution| DataStorageTier
    SQL_VIEWS -.->|Read-Only Facts| CONTEXT
    SP_DATA -.->|Read-Only Dossier| CONTEXT
    POLICY_DATA -.->|Read-Only Rules| CONTEXT
    PBI_MODEL -.->|Read-Only Metrics| CONTEXT

    %% Response Generation
    CONTEXT -->|5. Structured Grounded Context| MODEL
    MODEL -->|6. Draft Response| GUARD_OUT
    GUARD_OUT -->|7. Formatted Adaptive Card / Text| UI
    UI -->|8. Audited Presentation| USER

    %% Human in the loop action loop
    USER -->|9. Human Verification| HITL
    HITL -->|10. Authoritative Action| ACTION
    ACTION -->|11. Mutates State via Power Apps / SharePoint| SP_DATA

    %% Explicit Prohibition
    MODEL x--x|STRICTLY PROHIBITED: Autonomous Mutation| SP_DATA
```

---

## 2. Key Architecture Principles

### 2.1 Read-Only Isolation
The AI intelligence layer has **zero write permissions** to any database table, SharePoint list, or audit repository. It cannot create, update, patch, or delete records. All workflow state changes must originate from authenticated human users via the Power Apps interface or Power Automate approvals.

### 2.2 Deterministic Parameterized Retrieval
Rather than passing entire unindexed databases into large language model context windows, "Ask ComplyFlow" executes deterministic, parameterized queries based on extracted entities:
* When a user queries a specific case (`CR-2026-0014`), the system executes a targeted lookup returning only that specific row and its associated audit trail events.
* When querying aggregate KPIs, the system queries curated analytical views (`vw_active_backlog`, `vw_request_performance`) rather than calculating dynamic unverified aggregates on the fly.

### 2.3 Strict Separation of Facts from Hypotheses
Responses are programmatically structured into distinct tiers:
1. **Factual Evidence:** Hard data extracted directly from the system of record.
2. **Descriptive Summary:** Factual translation into clear English.
3. **Operational Recommendation:** Explicitly marked with the tag `[AI Suggested Next Step - Requires Human Verification]`.

---

## 3. Security, Privacy & Boundary Protection

| Security Boundary | Mechanism | Purpose |
| :--- | :--- | :--- |
| **Input Boundary** | Regex Entity Scanners & Prompt Hardening | Prevents prompt injection, jailbreaking, and cross-domain instruction manipulation. |
| **Identity Boundary** | Entra ID Token Pass-Through (Level 3) | Enforces role-based operational permissions; analysts can only inspect cases within their operational division. |
| **Network Boundary** | Azure Private Link & VNet Isolation (Level 3) | Guarantees that internal compliance data never traverses public networks or exposes endpoints externally. |
| **Output Boundary** | Hallucination Interceptor & Watermarking | Detects fabricated entities or unsupported causation and flags recommendations for human oversight. |
