# 0001. Project Architecture and Technology Selection

**Status:** Accepted
**Date:** 2026-09-26
**Context:** Compliance Development Apprentice Portfolio Prototype

---

## Context and Problem Statement

Compliance operations in financial institutions frequently suffer from fragmented email-based request handling, manual tracking in disconnected spreadsheets, missed regulatory SLA deadlines, and lack of operational transparency.

We need an architecture that:
1. Demonstrates realistic business process improvement, workflow automation, and process intelligence.
2. Aligns directly with enterprise compliance tooling commonly utilized in modern institutions.
3. Remains understandable, maintainable, and explainable for a beginner developer during HR and technical interviews.
4. Avoids unnecessary enterprise microservices, complex custom infrastructure, or synthetic complexity.

---

## Decision Drivers

- **Explainability:** The developer must be able to clearly articulate every architectural component, its business justification, and how data moves through the system.
- **Enterprise Relevance:** Alignment with standard low-code and data tools widely adopted by operational compliance and risk teams.
- **Data Protection & Compliance Safety:** Zero risk of exposing real customer data, proprietary business records, or sensitive financial information.
- **Cost & Feasibility:** Capable of being developed locally using open tools before deployment to Microsoft cloud environments.

---

## Considered Technologies & Architectural Choices

### 1. User Interface: Microsoft Power Apps
- **Decision:** Selected Microsoft Power Apps (Canvas App) for request intake and queue management.
- **Rationale:** Power Apps is the enterprise standard for rapid, internal low-code operational tooling. It provides rich form validation, responsive layouts, and native connectivity to Microsoft operational data stores without requiring complex web frameworks (e.g., React/Angular) or custom CSS/HTML frontends.

### 2. Operational Storage: SharePoint Online
- **Decision:** Selected SharePoint Online Lists as the operational records store.
- **Rationale:** SharePoint provides structured, relational-like tabular storage with built-in versioning, item-level auditing, and field-type validation. It integrates seamlessly with Power Apps and Power Automate without the overhead, licensing cost, or administration complexity of enterprise Dataverse or dedicated cloud SQL servers at the initial prototype stage.

### 3. Workflow Engine: Microsoft Power Automate
- **Decision:** Selected Microsoft Power Automate for business logic execution.
- **Rationale:** Power Automate enables transparent, event-driven workflows (e.g., automated email notifications upon submission, scheduled daily SLA countdown audits, and multi-tier approval routing). This eliminates the need to author, host, and monitor custom background cron jobs or daemon scripts.

### 4. Management Reporting: Microsoft Power BI
- **Decision:** Selected Microsoft Power BI for management dashboards.
- **Rationale:** Power BI is the premier business intelligence tool in financial operations. It allows interactive visual analysis of compliance metrics (SLA breach rates, average resolution times, volume by request category) and enables leadership to drill down into operational bottlenecks.

### 5. Data Querying: SQL
- **Decision:** Selected standard SQL as the primary analytical query language.
- **Rationale:** SQL is a foundational, highly transferable data skill already understood by the developer. It is ideal for structured relational data modeling, aggregations, window functions, and calculating operational KPIs (e.g., cycle times, SLA adherence percentages).

### 6. Data Quality & Automation: Python 3.13
- **Decision:** Selected Python for synthetic data generation, automated data cleaning, and schema validation.
- **Rationale:** Python provides an accessible, rich ecosystem for data engineering tasks. Scripts can easily simulate realistic compliance workloads, perform automated sanity checks on date chronologies, and prepare curated tabular extracts for SQL and Power BI ingestion.

### 7. Technical SQL Benchmark: Microsoft AdventureWorks
- **Decision:** Selected Microsoft AdventureWorks strictly as a reference database for technical SQL practice.
- **Rationale:** AdventureWorks provides a well-documented, complex relational schema suitable for demonstrating advanced SQL techniques (multi-table joins, subqueries, CTEs) and advanced Power BI modeling without risking proprietary data leaks. It is kept completely isolated from the compliance workflow.

### 8. Operational Data: Synthetic Compliance Operations Dataset
- **Decision:** Selected a custom, synthetic compliance dataset for ComplyFlow rather than attempting to adapt AdventureWorks for compliance.
- **Rationale:** Realistic compliance operational concepts (KYC reviews, PEP screening, AML transaction monitoring, sanctions waivers, SLA target dates) require specific domain attributes that AdventureWorks lacks. Generating a synthetic dataset ensures complete compliance safety, zero PII concerns, and full control over scenario modeling.

---

## Consequences

### Positive Consequences
- Every technology directly serves a defined business and portfolio objective.
- The system is modular: data pipelines and SQL analytics can be developed and validated completely offline.
- Demonstrates full-lifecycle business transformation: from intake through automation to executive reporting.
- High credibility in apprentice/junior interviews due to realistic enterprise tooling choices.

### Negative / Trade-Off Consequences
- Dual-data model (AdventureWorks for SQL benchmarks vs. Synthetic dataset for ComplyFlow) requires strict documentation to prevent confusion.
- Cloud deployment of Power Platform components requires access to an appropriate Microsoft 365 / Power Apps environment.
