# Tests Directory

This directory will contain automated tests verifying data hygiene, SQL query results, and validation script correctness.

---

## 📁 Testing Scope (Planned for Phase 3)

- **Data Quality Tests:** Ensure generated synthetic compliance datasets adhere to schema constraints (non-null IDs, valid enum choices, valid date chronologies where `SubmissionDate <= TargetDueDate`).
- **SLA Calculation Tests:** Verify that SLA breach flags match business logic expectations against target dates.
- **SQL Result Validation:** Validate that analytical SQL queries return expected aggregations against known seed datasets.
