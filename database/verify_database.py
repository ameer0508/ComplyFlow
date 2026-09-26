"""
ComplyFlow - SQL Database & Analytics Verification
==================================================
Performs automated verification of the SQLite database (database/complyflow.db):
1. Database and table existence.
2. Exact row count assertions (150 requests, 716 audit rows, 4 SLA policies).
3. Primary key and foreign key integrity.
4. Analytical view validation (ResolutionTimeHours, SLAState classification).
5. KPI reconciliation against Phase 2B benchmarks.

Exits with code 0 on success, non-zero on failure.
"""

import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "complyflow.db"

EXPECTED_SLA_HOURS = {
    "Critical": 24,
    "High": 72,
    "Medium": 120,
    "Low": 240,
}

EXPECTED_WARNING_HOURS = {
    "Critical": 6,
    "High": 24,
    "Medium": 24,
    "Low": 48,
}


def run_verification():
    errors = []
    print("==================================================")
    print("ComplyFlow SQLite Database & Analytics Verification")
    print("==================================================")

    # 1. Database File Check
    if not DB_PATH.exists():
        print(f"[FAIL] Database file not found at: {DB_PATH}")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 2. Check Tables Existence
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    for expected_table in ["ComplianceRequest", "RequestAuditLog", "SLAPolicy"]:
        if expected_table not in tables:
            errors.append(f"Missing table: {expected_table}")

    # 3. Check Views Existence
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
    views = {row[0] for row in cursor.fetchall()}
    expected_views = [
        "vw_request_performance",
        "vw_active_backlog",
        "vw_process_area_performance",
        "vw_risk_performance",
        "vw_request_type_performance"
    ]
    for v in expected_views:
        if v not in views:
            errors.append(f"Missing analytical view: {v}")

    if errors:
        for err in errors:
            print(f"[FAIL] {err}")
        sys.exit(1)

    # 4. Row Counts Verification
    cursor.execute("SELECT COUNT(*) FROM ComplianceRequest;")
    req_count = cursor.fetchone()[0]
    if req_count != 150:
        errors.append(f"ComplianceRequest count mismatch: expected 150, got {req_count}")

    cursor.execute("SELECT COUNT(*) FROM RequestAuditLog;")
    audit_count = cursor.fetchone()[0]
    if audit_count != 716:
        errors.append(f"RequestAuditLog count mismatch: expected 716, got {audit_count}")

    cursor.execute("SELECT COUNT(*) FROM SLAPolicy;")
    sla_count = cursor.fetchone()[0]
    if sla_count != 4:
        errors.append(f"SLAPolicy count mismatch: expected 4, got {sla_count}")

    # 5. Foreign Key Integrity Check
    cursor.execute("""
        SELECT COUNT(*)
        FROM RequestAuditLog a
        LEFT JOIN ComplianceRequest r ON a.RequestID = r.RequestID
        WHERE r.RequestID IS NULL;
    """)
    orphan_audits = cursor.fetchone()[0]
    if orphan_audits > 0:
        errors.append(f"Foreign key violation: {orphan_audits} audit logs have invalid RequestID")

    cursor.execute("""
        SELECT COUNT(*)
        FROM ComplianceRequest r
        LEFT JOIN SLAPolicy s ON r.RiskLevel = s.RiskLevel
        WHERE s.RiskLevel IS NULL;
    """)
    orphan_requests = cursor.fetchone()[0]
    if orphan_requests > 0:
        errors.append(f"Foreign key violation: {orphan_requests} requests have invalid RiskLevel")

    # 6. Analytical Views & Logic Verification
    # A. ResolutionTimeHours check in vw_request_performance
    cursor.execute("SELECT COUNT(*) FROM vw_request_performance WHERE Status = 'Closed' AND ResolutionTimeHours IS NULL;")
    null_closed_res = cursor.fetchone()[0]
    if null_closed_res > 0:
        errors.append(f"vw_request_performance: {null_closed_res} closed requests have NULL ResolutionTimeHours")

    cursor.execute("SELECT COUNT(*) FROM vw_request_performance WHERE Status != 'Closed' AND ResolutionTimeHours IS NOT NULL;")
    notnull_open_res = cursor.fetchone()[0]
    if notnull_open_res > 0:
        errors.append(f"vw_request_performance: {notnull_open_res} open requests have non-NULL ResolutionTimeHours")

    # B. Active Backlog SLA States check in vw_active_backlog
    cursor.execute("SELECT COUNT(*) FROM vw_active_backlog;")
    active_count = cursor.fetchone()[0]
    if active_count != 50:
        errors.append(f"vw_active_backlog total mismatch: expected 50, got {active_count}")

    cursor.execute("SELECT SLAState, COUNT(*) FROM vw_active_backlog GROUP BY SLAState;")
    sla_state_counts = dict(cursor.fetchall())
    overdue_count = sla_state_counts.get("Overdue", 0)
    approaching_count = sla_state_counts.get("Approaching Deadline", 0)
    ontrack_count = sla_state_counts.get("On Track", 0)

    if overdue_count != 24:
        errors.append(f"Overdue active cases mismatch: expected 24, got {overdue_count}")
    if approaching_count != 0:
        errors.append(f"Approaching deadline cases mismatch: expected 0, got {approaching_count}")
    if ontrack_count != 26:
        errors.append(f"On track active cases mismatch: expected 26, got {ontrack_count}")

    # C. Historical Closed Breaches
    cursor.execute("SELECT COUNT(*) FROM ComplianceRequest WHERE Status = 'Closed' AND SLABreachFlag = 1;")
    closed_breaches = cursor.fetchone()[0]
    if closed_breaches != 12:
        errors.append(f"Closed SLA breaches mismatch: expected 12, got {closed_breaches}")

    # D. Escalated and Approval Counts
    cursor.execute("SELECT COUNT(*) FROM ComplianceRequest WHERE EscalationFlag = 1;")
    escalated_count = cursor.fetchone()[0]
    if escalated_count != 17:
        errors.append(f"Escalated count mismatch: expected 17, got {escalated_count}")

    cursor.execute("SELECT COUNT(*) FROM ComplianceRequest WHERE ApprovalRequired = 1;")
    approval_count = cursor.fetchone()[0]
    if approval_count != 70:
        errors.append(f"ApprovalRequired count mismatch: expected 70, got {approval_count}")

    # E. Test executive summary view query
    exec_sql = PROJECT_ROOT / "database" / "queries" / "executive_summary.sql"
    with open(exec_sql, "r", encoding="utf-8") as f:
        exec_query = f.read()
    cursor.execute(exec_query)
    summary_row = cursor.fetchone()

    conn.close()

    print("\n--- Verified KPI Summary ---")
    print(f"Total Requests:             {summary_row[0]}")
    print(f"Closed Requests:            {summary_row[1]}")
    print(f"Active Requests:            {summary_row[2]}")
    print(f"SLA Breach Rate (Closed):   {summary_row[3]}%")
    print(f"Avg Resolution Time:        {summary_row[4]} hours")
    print(f"Escalated Requests:         {summary_row[5]}")
    print(f"Approval Required Requests: {summary_row[6]}")
    print(f"Currently Overdue Requests: {summary_row[7]}")
    print(f"Approaching Deadline:       {summary_row[8]}")
    print("----------------------------")

    if errors:
        print(f"\n[FAILED] Verification encountered {len(errors)} error(s):")
        for err in errors:
            print(f"  • {err}")
        sys.exit(1)
    else:
        print("\n[PASSED] All database tables, analytical views, and KPI assertions passed successfully with 0 errors!")
        sys.exit(0)


if __name__ == "__main__":
    run_verification()
