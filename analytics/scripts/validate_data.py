"""
ComplyFlow - Data Quality & Integrity Validator
===============================================
Validates synthetic compliance operational datasets against the approved Phase 2A domain rules:
- Row counts and uniqueness
- Required field non-null constraints
- Controlled enum choices
- Chronological date ordering
- SLA calculation accuracy
- Lifecycle and approval constraints
- Foreign key integrity and audit chronology

Returns exit code 0 on success, non-zero on failure.
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "raw"

REQUESTS_FILE = DATA_DIR / "compliance_requests.csv"
AUDIT_FILE = DATA_DIR / "request_audit_log.csv"
POLICIES_FILE = DATA_DIR / "sla_policies.csv"

# Allowed Domain Values
ALLOWED_REQUEST_TYPES = {
    "KYC Review",
    "PEP Review",
    "AML Transaction Inquiry",
    "Sanctions Review",
    "Policy Exception",
}

ALLOWED_PROCESS_AREAS = {
    "Customer Onboarding",
    "AML Operations",
    "KYC Operations",
    "Sanctions",
    "Policy & Governance",
}

ALLOWED_RISK_LEVELS = {"Low", "Medium", "High", "Critical"}
ALLOWED_PRIORITIES = {"Low", "Medium", "High", "Critical"}

ALLOWED_STATUSES = {
    "Draft",
    "Submitted",
    "Under Review",
    "Pending Approval",
    "Escalated",
    "Approved",
    "Rejected",
    "Closed",
}

ALLOWED_AUDIT_ACTIONS = {
    "Created",
    "Submitted",
    "Assigned",
    "Status Changed",
    "Escalated",
    "Approval Requested",
    "Approved",
    "Rejected",
    "Closed",
}

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


def parse_dt(dt_str):
    if not dt_str or dt_str.strip() == "":
        return None
    return datetime.strptime(dt_str.strip(), "%Y-%m-%d %H:%M:%S")


def run_validation():
    errors = []
    warnings = []

    print("==================================================")
    print("ComplyFlow Data Quality & Integrity Validator")
    print("==================================================")

    # -------------------------------------------------------------
    # 1. Verify File Existence
    # -------------------------------------------------------------
    for f in [REQUESTS_FILE, AUDIT_FILE, POLICIES_FILE]:
        if not f.exists():
            errors.append(f"Missing required data file: {f.name}")

    if errors:
        for err in errors:
            print(f"[FAIL] {err}")
        sys.exit(1)

    # -------------------------------------------------------------
    # 2. Validate SLAPolicy Dataset
    # -------------------------------------------------------------
    with open(POLICIES_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    if len(reader) != 4:
        errors.append(f"SLAPolicy row count mismatch: Expected 4, found {len(reader)}")

    seen_risk_policies = set()
    for row in reader:
        r_level = row.get("RiskLevel")
        seen_risk_policies.add(r_level)
        if r_level not in ALLOWED_RISK_LEVELS:
            errors.append(f"SLAPolicy invalid RiskLevel: {r_level}")

        sla_hrs = int(row.get("SLATargetHours", 0))
        if sla_hrs != EXPECTED_SLA_HOURS.get(r_level):
            errors.append(f"SLAPolicy incorrect SLATargetHours for {r_level}: expected {EXPECTED_SLA_HOURS.get(r_level)}, found {sla_hrs}")

        warn_hrs = int(row.get("WarningThresholdHours", 0))
        if warn_hrs != EXPECTED_WARNING_HOURS.get(r_level):
            errors.append(f"SLAPolicy incorrect WarningThresholdHours for {r_level}: expected {EXPECTED_WARNING_HOURS.get(r_level)}, found {warn_hrs}")

    if seen_risk_policies != ALLOWED_RISK_LEVELS:
        errors.append(f"SLAPolicy missing tiers: {ALLOWED_RISK_LEVELS - seen_risk_policies}")

    # -------------------------------------------------------------
    # 3. Validate ComplianceRequest Dataset
    # -------------------------------------------------------------
    with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
        requests = list(csv.DictReader(f))

    if len(requests) != 150:
        errors.append(f"ComplianceRequest row count mismatch: Expected 150, found {len(requests)}")

    seen_req_ids = set()
    status_counts = {}
    process_area_counts = {}
    risk_level_counts = {}

    required_request_fields = [
        "RequestID", "Title", "RequestType", "ProcessArea", "RiskLevel",
        "Priority", "Status", "Description", "RequesterName", "RequesterEmail",
        "RequesterDepartment", "SubmissionDateTime", "TargetDueDateTime",
        "SLATargetHours", "SLABreachFlag", "ApprovalRequired", "CreatedDate",
        "ModifiedDate"
    ]

    for idx, row in enumerate(requests, 1):
        req_id = row.get("RequestID", "").strip()

        # Uniqueness & format
        if not req_id:
            errors.append(f"Row {idx}: RequestID is missing.")
            continue
        if req_id in seen_req_ids:
            errors.append(f"Duplicate RequestID found: {req_id}")
        seen_req_ids.add(req_id)

        if not (req_id.startswith("CR-2026-") and len(req_id) == 12):
            errors.append(f"RequestID {req_id} does not match expected format CR-2026-XXXX")

        # Required fields non-null
        for field in required_request_fields:
            if not row.get(field) or row.get(field).strip() == "":
                errors.append(f"{req_id}: Required field '{field}' is missing or empty.")

        # Categorical choices
        req_type = row.get("RequestType")
        if req_type not in ALLOWED_REQUEST_TYPES:
            errors.append(f"{req_id}: Invalid RequestType '{req_type}'")

        p_area = row.get("ProcessArea")
        if p_area not in ALLOWED_PROCESS_AREAS:
            errors.append(f"{req_id}: Invalid ProcessArea '{p_area}'")
        process_area_counts[p_area] = process_area_counts.get(p_area, 0) + 1

        risk = row.get("RiskLevel")
        if risk not in ALLOWED_RISK_LEVELS:
            errors.append(f"{req_id}: Invalid RiskLevel '{risk}'")
        risk_level_counts[risk] = risk_level_counts.get(risk, 0) + 1

        prio = row.get("Priority")
        if prio not in ALLOWED_PRIORITIES:
            errors.append(f"{req_id}: Invalid Priority '{prio}'")

        status = row.get("Status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{req_id}: Invalid Status '{status}'")
        status_counts[status] = status_counts.get(status, 0) + 1

        # Dates & Chronology
        created_dt = parse_dt(row.get("CreatedDate"))
        submission_dt = parse_dt(row.get("SubmissionDateTime"))
        target_due_dt = parse_dt(row.get("TargetDueDateTime"))
        completion_dt = parse_dt(row.get("CompletionDateTime"))
        approval_dt = parse_dt(row.get("ApprovalDate"))

        if not created_dt or not submission_dt or not target_due_dt:
            errors.append(f"{req_id}: Missing core timestamps.")
            continue

        if submission_dt < created_dt:
            errors.append(f"{req_id}: SubmissionDateTime ({submission_dt}) precedes CreatedDate ({created_dt})")

        # SLA calculation accuracy
        sla_hrs = int(row.get("SLATargetHours", 0))
        expected_hrs = EXPECTED_SLA_HOURS.get(risk, 0)
        if sla_hrs != expected_hrs:
            errors.append(f"{req_id}: SLATargetHours ({sla_hrs}) does not match risk policy for {risk} ({expected_hrs})")

        expected_due_dt = submission_dt + (target_due_dt - submission_dt)
        actual_delta_hours = (target_due_dt - submission_dt).total_seconds() / 3600.0
        if round(actual_delta_hours) != sla_hrs:
            errors.append(f"{req_id}: TargetDueDateTime delta ({actual_delta_hours}h) does not equal SLATargetHours ({sla_hrs}h)")

        # Status & Completion rules
        if status == "Closed":
            if not completion_dt:
                errors.append(f"{req_id}: Closed status requires CompletionDateTime.")
            elif completion_dt < submission_dt:
                errors.append(f"{req_id}: CompletionDateTime ({completion_dt}) precedes SubmissionDateTime ({submission_dt})")

            # SLA Breach consistency for closed
            actual_breach = 1 if completion_dt > target_due_dt else 0
            flagged_breach = int(row.get("SLABreachFlag", 0))
            if actual_breach != flagged_breach:
                errors.append(f"{req_id}: Closed case SLABreachFlag mismatch. Actual breach={actual_breach}, Flag={flagged_breach}")
        else:
            # Open cases must not have completion date
            if completion_dt:
                errors.append(f"{req_id}: Open case (Status={status}) has CompletionDateTime populated ({completion_dt})")

        # Analyst assignment guard
        analyst = row.get("AssignedAnalyst", "").strip()
        if status in ["Under Review", "Pending Approval", "Escalated", "Approved", "Rejected", "Closed"]:
            if not analyst:
                errors.append(f"{req_id}: Status '{status}' requires an AssignedAnalyst.")

        # Approval rules
        appr_req = int(row.get("ApprovalRequired", 0))
        if risk in ["High", "Critical"] and appr_req != 1:
            errors.append(f"{req_id}: High/Critical risk requires ApprovalRequired=1.")

        if appr_req == 1 and status == "Closed" and "rejection" not in row.get("ClosureNotes", "").lower():
            if not row.get("ApprovedBy"):
                errors.append(f"{req_id}: Approved high-risk case missing ApprovedBy.")
            if not approval_dt:
                errors.append(f"{req_id}: Approved high-risk case missing ApprovalDate.")

        # Escalation rules
        esc_flag = int(row.get("EscalationFlag", 0))
        if status == "Escalated" and esc_flag != 1:
            errors.append(f"{req_id}: Status is 'Escalated' but EscalationFlag is not 1.")

    # -------------------------------------------------------------
    # 4. Validate RequestAuditLog Dataset
    # -------------------------------------------------------------
    with open(AUDIT_FILE, "r", encoding="utf-8") as f:
        audits = list(csv.DictReader(f))

    if len(audits) == 0:
        errors.append("RequestAuditLog is empty.")

    seen_audit_ids = set()
    audit_by_request = {}

    for idx, a_row in enumerate(audits, 1):
        a_id = a_row.get("AuditID", "").strip()
        if not a_id:
            errors.append(f"Audit Row {idx}: Missing AuditID.")
            continue
        if a_id in seen_audit_ids:
            errors.append(f"Duplicate AuditID found: {a_id}")
        seen_audit_ids.add(a_id)

        req_fk = a_row.get("RequestID", "").strip()
        if req_fk not in seen_req_ids:
            errors.append(f"Audit {a_id}: Foreign key violation - RequestID '{req_fk}' not in ComplianceRequest.")

        action = a_row.get("ActionType")
        if action not in ALLOWED_AUDIT_ACTIONS:
            errors.append(f"Audit {a_id}: Invalid ActionType '{action}'")

        a_dt = parse_dt(a_row.get("Timestamp"))
        if not a_dt:
            errors.append(f"Audit {a_id}: Missing or invalid Timestamp.")
            continue

        if req_fk not in audit_by_request:
            audit_by_request[req_fk] = []
        audit_by_request[req_fk].append((a_id, a_dt, a_row))

    # Validate chronological ordering of audit logs per request
    for r_id, a_list in audit_by_request.items():
        prev_dt = None
        for a_id, a_dt, a_row in a_list:
            if prev_dt and a_dt < prev_dt:
                errors.append(f"{r_id} Audit {a_id}: Timestamp {a_dt} is earlier than previous audit event {prev_dt}")
            prev_dt = a_dt

    # -------------------------------------------------------------
    # 5. Summary & Verdict
    # -------------------------------------------------------------
    print("\n--- Distribution Summary ---")
    print(f"Total Requests: {len(requests)}")
    print(f"Total Audit Events: {len(audits)}")
    print("\nBy Status:")
    for st, c in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  - {st:<18}: {c:>3} ({c/len(requests)*100:.1f}%)")

    print("\nBy Process Area:")
    for pa, c in sorted(process_area_counts.items(), key=lambda x: -x[1]):
        print(f"  - {pa:<22}: {c:>3} ({c/len(requests)*100:.1f}%)")

    print("\nBy Risk Level:")
    for rl, c in sorted(risk_level_counts.items(), key=lambda x: -x[1]):
        print(f"  - {rl:<12}: {c:>3} ({c/len(requests)*100:.1f}%)")

    print("\n----------------------------")
    if errors:
        print(f"\n[FAILED] Validation encountered {len(errors)} error(s):")
        for err in errors[:25]:  # print first 25 errors
            print(f"  • {err}")
        if len(errors) > 25:
            print(f"  ... and {len(errors) - 25} more errors.")
        sys.exit(1)
    else:
        print("\n[PASSED] All data quality, SLA, and lifecycle integrity checks passed successfully with 0 errors!")
        sys.exit(0)


if __name__ == "__main__":
    run_validation()
