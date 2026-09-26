# Database & SQL Queries

This directory will store all database DDL schemas, seed scripts, and analytical SQL queries.

---

## 📁 Structure (Planned for Phase 3)

```
database/
├── schema.sql              # Relational schema for compliance requests and audit log
├── seed.sql                # Synthetic seed data for local testing
└── queries/                # Operational SQL queries
    ├── sla_tracking.sql        # Identifying overdue requests and upcoming deadlines
    ├── bottleneck_analysis.sql # Calculating stage duration and queue delays
    └── analyst_workload.sql    # Volume distribution and capacity metrics
```

All SQL scripts will be documented and kept ANSI-SQL / SQLite compatible for zero-friction local execution.
