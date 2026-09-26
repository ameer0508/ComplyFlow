# Ask ComplyFlow — Copilot Studio & Practical AI Implementation Guide

**Project:** ComplyFlow — Compliance Workflow & Process Intelligence Platform
**Component:** Microsoft Copilot Studio & Multi-Tier Implementation Guide
**Phase:** 7 (AI-Assisted Compliance Operations & Copilot Integration)
**Status:** Build-Ready Technical Implementation Specification

---

## 1. Multi-Tier Architecture & Implementation Levels

To provide a practical and defensible engineering roadmap, "Ask ComplyFlow" is architected across three progressive implementation tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 1: Local Deterministic / Conceptual Prototype (Current State)   │
│ • Runs locally against database/complyflow.db (SQLite) & CSV files     │
│ • Zero cloud AI service dependencies; zero subscription requirements   │
│ • 100% reproducible offline verification                               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Cloud Readiness Transition)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 2: Microsoft Copilot Studio & Power Platform (Future Staging)    │
│ • Low-code Copilot deployed within Microsoft Copilot Studio            │
│ • Direct Power Platform connectors to SharePoint Online & Power BI    │
│ • Power Automate cloud flows executing parameterized read-only queries │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Enterprise Production Scale)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 3: Governed Enterprise AI Architecture (Target Production State) │
│ • Azure OpenAI Service (GPT-4o) with Private Endpoints (VNet)          │
│ • Entra ID RBAC token pass-through for row-level operational security  │
│ • Immutable query/response logging to Azure Log Analytics / Sentinel   │
└────────────────────────────────────────────────────────────────────────┘
```

> **Important Deployment Notice:** Level 2 and Level 3 represent forward-looking enterprise implementation designs. No live Copilot Studio bots, Azure OpenAI instances, or cloud connectors have been deployed in this environment.

---

## 2. Level 2: Microsoft Copilot Studio Configuration Specification

### 2.1 Bot Identity & Generative AI Settings
* **Bot Display Name:** `Ask ComplyFlow`
* **Bot Description:** *"Compliance operations intelligence assistant providing case summarization, SLA tracking, and audit log analysis."*
* **Primary Language:** `English (en-US)`
* **Content Moderation Level:** `High` (Ensures strict adherence to enterprise compliance tone)
* **Generative Answers Source:** Configured exclusively with authenticated internal enterprise endpoints; external public web browsing is **disabled**.

---

### 2.2 Core Topics & Trigger Phrasing Architecture

The Copilot is structured into distinct conversation topics with deterministic trigger phrases:

| Topic Name | Trigger Phrases | Purpose | Action / Flow Invocation |
| :--- | :--- | :--- | :--- |
| **`Topic_KPI_Query`** | *"How many active cases?", "What is our overdue count?", "Show breach rate"* | Answers high-level operational metrics | Calls `Flow_GetOperationalKPIs` |
| **`Topic_Case_Summary`** | *"Summarize case", "Tell me about CR-2026-0014", "Lookup request"* | Generates a 30-second case brief | Calls `Flow_GetCaseDossier` |
| **`Topic_Audit_History`** | *"Explain audit history", "Show timeline for CR-2026-0001", "What happened on this case"* | Reconstructs chronological audit trail | Calls `Flow_GetCaseAuditTrail` |
| **`Topic_SLA_Policy`** | *"What is the SLA for Critical?", "Who is the escalation role for High risk?"* | Explains regulatory turnaround policies | Local Knowledge Node (`SLAPolicy`) |
| **`Topic_Escalation`** | *"I need to speak to a compliance manager", "Talk to human"* | Routes user to human compliance lead | Escalates to Supervisor Queue |

---

### 2.3 Custom Entity Extraction

Copilot Studio extracts structured domain entities from user utterances prior to flow execution:

```yaml
Entities:
  - Name: "ComplianceRequestID"
    PatternRegex: "(?i)CR-\\d{4}-\\d{4}"
    Description: "Standard 12-character ComplyFlow request identifier (e.g., CR-2026-0014)"
    Examples:
      - "CR-2026-0014"
      - "CR-2026-0001"
      - "cr-2026-0095"

  - Name: "RiskTier"
    Type: "ClosedList"
    Values:
      - "Critical" (Synonyms: "Sev 1", "P1", "Immediate")
      - "High"     (Synonyms: "Sev 2", "P2", "Urgent")
      - "Medium"   (Synonyms: "Standard", "Normal")
      - "Low"      (Synonyms: "Minor", "Routine")

  - Name: "ProcessAreaName"
    Type: "ClosedList"
    Values:
      - "AML Operations"
      - "Customer Onboarding"
      - "KYC Operations"
      - "Sanctions"
      - "Policy & Governance"
```

---

### 2.4 Power Automate Connector Actions (Read-Only)

Copilot Studio delegates all data retrieval to governed Power Automate cloud flows using service principal authentication:

```
[ Copilot Studio Conversation ]
               │
               ▼ (Input: RequestID = "CR-2026-0014")
[ Flow_GetCaseDossier (Cloud Flow) ]
   ├── Step 1: Validate RequestID format via Regex
   ├── Step 2: Query SharePoint List (ComplianceRequests) or SQLite via Gateway
   ├── Step 3: Query SharePoint List (RequestAuditLog) for matching RequestID
   ├── Step 4: Assemble JSON payload containing case metadata & audit events
   └── Step 5: Return structured response to Copilot Studio
               │
               ▼
[ Copilot Studio Adaptive Card Rendering ]
```

---

### 2.5 Adaptive Card Presentation Template (Case Summary)

To maintain a consistent, accessible user experience, case summaries are returned via Adaptive Cards:

```json
{
  "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    {
      "type": "Container",
      "style": "emphasis",
      "items": [
        {
          "type": "TextBlock",
          "text": "ComplyFlow Case Dossier: ${RequestID}",
          "weight": "Bolder",
          "size": "Medium",
          "color": "Dark"
        }
      ]
    },
    {
      "type": "FactSet",
      "facts": [
        {"title": "Title:", "value": "${Title}"},
        {"title": "Process Area:", "value": "${ProcessArea}"},
        {"title": "Risk Level:", "value": "${RiskLevel}"},
        {"title": "Current Status:", "value": "${Status}"},
        {"title": "Analyst:", "value": "${AssignedAnalyst}"},
        {"title": "SLA Due Date:", "value": "${TargetDueDateTime}"},
        {"title": "SLA Health:", "value": "${SLAState}"}
      ]
    },
    {
      "type": "TextBlock",
      "text": "[AI Suggested Next Step - Requires Human Verification]:",
      "weight": "Bolder",
      "color": "Accent",
      "size": "Small"
    },
    {
      "type": "TextBlock",
      "text": "${SuggestedNextStep}",
      "wrap": true,
      "size": "Small"
    }
  ]
}
```

---

## 3. Level 3: Governed Enterprise Production Architecture

For enterprise financial institutions subject to FINRA, SEC, FCA, or BaFin regulations, the Level 3 architecture introduces comprehensive security perimeters:

1. **Private Endpoints & Network Isolation:** Azure OpenAI services reside entirely within a private Azure Virtual Network (VNet). Zero traffic traverses the public internet.
2. **Entra ID Token Pass-Through:** User security tokens pass through to the database layer, ensuring analysts cannot view cases outside their authorized operational boundary (e.g., Sanctions analysts cannot view AML investigation files without explicit clearance).
3. **Data Loss Prevention (DLP):** Azure AI Content Safety enforces real-time PII masking and blocks out-of-scope prompts before they reach the model.
4. **Immutable Audit Logging:** Every prompt, retrieved database row, and generated response is written to an immutable Azure Log Analytics workspace with 7-year regulatory retention.
