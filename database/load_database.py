"""
ComplyFlow - Database Loader
============================
Creates and loads the local SQLite database (database/complyflow.db) using the
existing validated synthetic datasets in data/raw/:
1. sla_policies.csv       -> SLAPolicy
2. compliance_requests.csv -> ComplianceRequest
3. request_audit_log.csv  -> RequestAuditLog

Also executes database/queries/analytics_views.sql to establish the analytical views.
Does NOT generate new data; strictly loads existing Phase 2B CSVs.
"""

import csv
import sqlite3
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "complyflow.db"
DATA_DIR = PROJECT_ROOT / "data" / "raw"
VIEWS_SQL_PATH = PROJECT_ROOT / "database" / "queries" / "analytics_views.sql"

REQ_CSV = DATA_DIR / "compliance_requests.csv"
AUDIT_CSV = DATA_DIR / "request_audit_log.csv"
SLA_CSV = DATA_DIR / "sla_policies.csv"


def load_database():
    print("==================================================")
    print("ComplyFlow SQLite Database Loader")
    print("==================================================")

    # 1. Verify CSV files exist
    for f in [REQ_CSV, AUDIT_CSV, SLA_CSV]:
        if not f.exists():
            raise FileNotFoundError(f"Required raw dataset missing: {f}")

    # Ensure database directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # 2. Connect to SQLite (creates file if not present)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable Foreign Key enforcement in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 3. Create Schema Tables
    print(f"Connecting to database: {DB_PATH.name}")

    # Drop existing tables cleanly in dependency order
    cursor.execute("DROP TABLE IF EXISTS RequestAuditLog;")
    cursor.execute("DROP TABLE IF EXISTS ComplianceRequest;")
    cursor.execute("DROP TABLE IF EXISTS SLAPolicy;")

    # Table 1: SLAPolicy
    cursor.execute("""
        CREATE TABLE SLAPolicy (
            RiskLevel TEXT PRIMARY KEY,
            SLATargetHours INTEGER NOT NULL,
            WarningThresholdHours INTEGER NOT NULL,
            ApprovalMandatory INTEGER NOT NULL,
            DefaultEscalationRole TEXT NOT NULL
        );
    """)

    # Table 2: ComplianceRequest
    cursor.execute("""
        CREATE TABLE ComplianceRequest (
            RequestID TEXT PRIMARY KEY,
            Title TEXT NOT NULL,
            RequestType TEXT NOT NULL,
            ProcessArea TEXT NOT NULL,
            RiskLevel TEXT NOT NULL,
            Priority TEXT NOT NULL,
            Status TEXT NOT NULL,
            Description TEXT NOT NULL,
            RequesterName TEXT NOT NULL,
            RequesterEmail TEXT NOT NULL,
            RequesterDepartment TEXT NOT NULL,
            AssignedAnalyst TEXT,
            AssignedAnalystEmail TEXT,
            ComplianceTeam TEXT NOT NULL,
            SubmissionDateTime TEXT NOT NULL,
            TargetDueDateTime TEXT NOT NULL,
            CompletionDateTime TEXT,
            SLATargetHours INTEGER NOT NULL,
            SLABreachFlag INTEGER NOT NULL,
            ApprovalRequired INTEGER NOT NULL,
            ApprovedBy TEXT,
            ApprovalDate TEXT,
            EscalationFlag INTEGER NOT NULL,
            EscalatedTo TEXT,
            EscalationReason TEXT,
            ClosureNotes TEXT,
            CreatedDate TEXT NOT NULL,
            ModifiedDate TEXT NOT NULL,
            FOREIGN KEY (RiskLevel) REFERENCES SLAPolicy (RiskLevel)
        );
    """)

    # Table 3: RequestAuditLog
    cursor.execute("""
        CREATE TABLE RequestAuditLog (
            AuditID INTEGER PRIMARY KEY,
            RequestID TEXT NOT NULL,
            Timestamp TEXT NOT NULL,
            ActionType TEXT NOT NULL,
            PerformedBy TEXT NOT NULL,
            OldStatus TEXT,
            NewStatus TEXT NOT NULL,
            Comments TEXT,
            FOREIGN KEY (RequestID) REFERENCES ComplianceRequest (RequestID)
        );
    """)

    # 4. Load Data from CSVs
    # A. SLAPolicy
    with open(SLA_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        sla_rows = [
            (
                row["RiskLevel"],
                int(row["SLATargetHours"]),
                int(row["WarningThresholdHours"]),
                int(row["ApprovalMandatory"]),
                row["DefaultEscalationRole"]
            )
            for row in reader
        ]
    cursor.executemany("""
        INSERT INTO SLAPolicy (
            RiskLevel, SLATargetHours, WarningThresholdHours,
            ApprovalMandatory, DefaultEscalationRole
        ) VALUES (?, ?, ?, ?, ?);
    """, sla_rows)

    # B. ComplianceRequest
    with open(REQ_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        req_rows = [
            (
                row["RequestID"],
                row["Title"],
                row["RequestType"],
                row["ProcessArea"],
                row["RiskLevel"],
                row["Priority"],
                row["Status"],
                row["Description"],
                row["RequesterName"],
                row["RequesterEmail"],
                row["RequesterDepartment"],
                row["AssignedAnalyst"] or None,
                row["AssignedAnalystEmail"] or None,
                row["ComplianceTeam"],
                row["SubmissionDateTime"],
                row["TargetDueDateTime"],
                row["CompletionDateTime"] or None,
                int(row["SLATargetHours"]),
                int(row["SLABreachFlag"]),
                int(row["ApprovalRequired"]),
                row["ApprovedBy"] or None,
                row["ApprovalDate"] or None,
                int(row["EscalationFlag"]),
                row["EscalatedTo"] or None,
                row["EscalationReason"] or None,
                row["ClosureNotes"] or None,
                row["CreatedDate"],
                row["ModifiedDate"]
            )
            for row in reader
        ]
    cursor.executemany("""
        INSERT INTO ComplianceRequest (
            RequestID, Title, RequestType, ProcessArea, RiskLevel,
            Priority, Status, Description, RequesterName, RequesterEmail,
            RequesterDepartment, AssignedAnalyst, AssignedAnalystEmail,
            ComplianceTeam, SubmissionDateTime, TargetDueDateTime,
            CompletionDateTime, SLATargetHours, SLABreachFlag,
            ApprovalRequired, ApprovedBy, ApprovalDate, EscalationFlag,
            EscalatedTo, EscalationReason, ClosureNotes, CreatedDate,
            ModifiedDate
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, req_rows)

    # C. RequestAuditLog
    with open(AUDIT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        audit_rows = [
            (
                int(row["AuditID"]),
                row["RequestID"],
                row["Timestamp"],
                row["ActionType"],
                row["PerformedBy"],
                row["OldStatus"] or None,
                row["NewStatus"],
                row["Comments"] or None
            )
            for row in reader
        ]
    cursor.executemany("""
        INSERT INTO RequestAuditLog (
            AuditID, RequestID, Timestamp, ActionType, PerformedBy,
            OldStatus, NewStatus, Comments
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, audit_rows)

    # 5. Execute Analytical Views Script
    if VIEWS_SQL_PATH.exists():
        with open(VIEWS_SQL_PATH, "r", encoding="utf-8") as f:
            views_script = f.read()
        cursor.executescript(views_script)
        print("Analytical views created successfully.")

    conn.commit()
    conn.close()

    print("\n[SUCCESS] Database loaded successfully:")
    print(f"  - Database:          {DB_PATH}")
    print(f"  - SLAPolicy:         {len(sla_rows)} rows")
    print(f"  - ComplianceRequest: {len(req_rows)} rows")
    print(f"  - RequestAuditLog:   {len(audit_rows)} rows")


if __name__ == "__main__":
    load_database()
