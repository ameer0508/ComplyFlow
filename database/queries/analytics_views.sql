-- ==============================================================================
-- ComplyFlow - Analytical SQL Views
-- ==============================================================================
-- Description: Core analytical views for process intelligence, SLA tracking,
--              backlog monitoring, and operational bottleneck analysis.
-- Engine:      SQLite (ANSI SQL Compatible)
-- Anchor Date: 2026-09-26 17:00:00 (Simulation Reference Timestamp)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- 1. View: vw_request_performance
-- Granularity: One row per ComplianceRequest
-- Purpose: Exposes individual case attributes with dynamically derived
--          ResolutionTimeHours for closed cases (NULL for open cases).
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_request_performance;

CREATE VIEW vw_request_performance AS
SELECT
    cr.RequestID,
    cr.Title,
    cr.RequestType,
    cr.ProcessArea,
    cr.RiskLevel,
    cr.Priority,
    cr.Status,
    cr.SubmissionDateTime,
    cr.TargetDueDateTime,
    cr.CompletionDateTime,
    cr.SLATargetHours,
    cr.SLABreachFlag,
    cr.ApprovalRequired,
    cr.ApprovedBy,
    cr.ApprovalDate,
    cr.EscalationFlag,
    cr.EscalatedTo,
    cr.AssignedAnalyst,
    cr.ComplianceTeam,
    cr.RequesterDepartment,
    CASE
        WHEN cr.Status = 'Closed' AND cr.CompletionDateTime IS NOT NULL
        THEN ROUND((JULIANDAY(cr.CompletionDateTime) - JULIANDAY(cr.SubmissionDateTime)) * 24.0, 2)
        ELSE NULL
    END AS ResolutionTimeHours
FROM ComplianceRequest cr;


-- ------------------------------------------------------------------------------
-- 2. View: vw_active_backlog
-- Granularity: One row per active/open ComplianceRequest (Status != 'Closed')
-- Purpose: Evaluates current SLA health (Overdue, Approaching Deadline, On Track)
--          based on the 2026-09-26 17:00:00 simulation reference timestamp
--          and risk policy warning thresholds.
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_active_backlog;

CREATE VIEW vw_active_backlog AS
SELECT
    cr.RequestID,
    cr.Title,
    cr.ProcessArea,
    cr.RequestType,
    cr.RiskLevel,
    cr.Priority,
    cr.Status,
    cr.AssignedAnalyst,
    cr.ComplianceTeam,
    cr.SubmissionDateTime,
    cr.TargetDueDateTime,
    sp.SLATargetHours,
    sp.WarningThresholdHours,
    cr.SLABreachFlag,
    cr.EscalationFlag,
    CASE
        WHEN '2026-09-26 17:00:00' > cr.TargetDueDateTime
            THEN 'Overdue'
        WHEN (JULIANDAY(cr.TargetDueDateTime) - JULIANDAY('2026-09-26 17:00:00')) * 24.0 <= sp.WarningThresholdHours
            THEN 'Approaching Deadline'
        ELSE 'On Track'
    END AS SLAState,
    ROUND((JULIANDAY(cr.TargetDueDateTime) - JULIANDAY('2026-09-26 17:00:00')) * 24.0, 1) AS HoursRemaining
FROM ComplianceRequest cr
JOIN SLAPolicy sp ON cr.RiskLevel = sp.RiskLevel
WHERE cr.Status != 'Closed';


-- ------------------------------------------------------------------------------
-- 3. View: vw_process_area_performance
-- Granularity: Aggregated by ProcessArea
-- Purpose: Provides management visibility into volume distribution, SLA breach
--          rates, and average turnaround times across operational areas.
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_process_area_performance;

CREATE VIEW vw_process_area_performance AS
SELECT
    cr.ProcessArea,
    COUNT(*) AS TotalRequests,
    SUM(CASE WHEN cr.Status = 'Closed' THEN 1 ELSE 0 END) AS ClosedRequests,
    SUM(CASE WHEN cr.Status != 'Closed' THEN 1 ELSE 0 END) AS ActiveRequests,
    SUM(CASE WHEN cr.Status = 'Closed' AND cr.SLABreachFlag = 1 THEN 1 ELSE 0 END) AS SLA_Breaches,
    ROUND(
        100.0 * SUM(CASE WHEN cr.Status = 'Closed' AND cr.SLABreachFlag = 1 THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN cr.Status = 'Closed' THEN 1 ELSE 0 END), 0),
        2
    ) AS SLA_BreachRate,
    ROUND(
        AVG(CASE
            WHEN cr.Status = 'Closed' AND cr.CompletionDateTime IS NOT NULL
            THEN (JULIANDAY(cr.CompletionDateTime) - JULIANDAY(cr.SubmissionDateTime)) * 24.0
            ELSE NULL
        END),
        2
    ) AS AverageResolutionTimeHours,
    SUM(CASE WHEN cr.EscalationFlag = 1 THEN 1 ELSE 0 END) AS EscalatedRequests,
    SUM(CASE WHEN cr.ApprovalRequired = 1 THEN 1 ELSE 0 END) AS ApprovalRequiredRequests
FROM ComplianceRequest cr
GROUP BY cr.ProcessArea;


-- ------------------------------------------------------------------------------
-- 4. View: vw_risk_performance
-- Granularity: Aggregated by RiskLevel
-- Purpose: Demonstrates how case volume, SLA compliance, cycle times, and
--          approval mandates behave across risk tiers.
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_risk_performance;

CREATE VIEW vw_risk_performance AS
SELECT
    sp.RiskLevel,
    sp.SLATargetHours,
    sp.ApprovalMandatory,
    COUNT(cr.RequestID) AS TotalRequests,
    SUM(CASE WHEN cr.Status = 'Closed' THEN 1 ELSE 0 END) AS ClosedRequests,
    SUM(CASE WHEN cr.Status != 'Closed' THEN 1 ELSE 0 END) AS ActiveRequests,
    SUM(CASE WHEN cr.Status = 'Closed' AND cr.SLABreachFlag = 1 THEN 1 ELSE 0 END) AS SLA_Breaches,
    ROUND(
        100.0 * SUM(CASE WHEN cr.Status = 'Closed' AND cr.SLABreachFlag = 1 THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN cr.Status = 'Closed' THEN 1 ELSE 0 END), 0),
        2
    ) AS SLA_BreachRate,
    ROUND(
        AVG(CASE
            WHEN cr.Status = 'Closed' AND cr.CompletionDateTime IS NOT NULL
            THEN (JULIANDAY(cr.CompletionDateTime) - JULIANDAY(cr.SubmissionDateTime)) * 24.0
            ELSE NULL
        END),
        2
    ) AS AverageResolutionTimeHours,
    SUM(CASE WHEN cr.EscalationFlag = 1 THEN 1 ELSE 0 END) AS EscalatedRequests,
    SUM(CASE WHEN cr.ApprovalRequired = 1 THEN 1 ELSE 0 END) AS ApprovalRequiredRequests
FROM SLAPolicy sp
LEFT JOIN ComplianceRequest cr ON sp.RiskLevel = cr.RiskLevel
GROUP BY sp.RiskLevel, sp.SLATargetHours, sp.ApprovalMandatory
ORDER BY sp.SLATargetHours ASC;


-- ------------------------------------------------------------------------------
-- 5. View: vw_request_type_performance
-- Granularity: Aggregated by RequestType
-- Purpose: Evaluates operational throughput and turnaround times by specific
--          compliance workflow category.
-- ------------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_request_type_performance;

CREATE VIEW vw_request_type_performance AS
SELECT
    cr.RequestType,
    COUNT(*) AS TotalRequests,
    SUM(CASE WHEN cr.Status = 'Closed' THEN 1 ELSE 0 END) AS ClosedRequests,
    SUM(CASE WHEN cr.Status != 'Closed' THEN 1 ELSE 0 END) AS ActiveRequests,
    SUM(CASE WHEN cr.Status = 'Closed' AND cr.SLABreachFlag = 1 THEN 1 ELSE 0 END) AS SLA_Breaches,
    ROUND(
        100.0 * SUM(CASE WHEN cr.Status = 'Closed' AND cr.SLABreachFlag = 1 THEN 1 ELSE 0 END) /
        NULLIF(SUM(CASE WHEN cr.Status = 'Closed' THEN 1 ELSE 0 END), 0),
        2
    ) AS SLA_BreachRate,
    ROUND(
        AVG(CASE
            WHEN cr.Status = 'Closed' AND cr.CompletionDateTime IS NOT NULL
            THEN (JULIANDAY(cr.CompletionDateTime) - JULIANDAY(cr.SubmissionDateTime)) * 24.0
            ELSE NULL
        END),
        2
    ) AS AverageResolutionTimeHours
FROM ComplianceRequest cr
GROUP BY cr.RequestType;
