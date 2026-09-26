-- ==============================================================================
-- ComplyFlow - Business Question Queries
-- ==============================================================================
-- Description: Standard operational and management queries answering key compliance
--              operations, bottleneck, capacity, and SLA performance questions.
-- Engine:      SQLite
-- Anchor Date: 2026-09-26 17:00:00 (Simulation Reference Timestamp)
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- Q1: Active Backlog by Process Area and Status
-- Business Purpose: Identify the distribution of active in-flight work across
--                   operational functions to monitor queue balance.
-- ------------------------------------------------------------------------------
SELECT
    ProcessArea,
    Status,
    COUNT(*) AS ActiveCaseCount
FROM ComplianceRequest
WHERE Status != 'Closed'
GROUP BY ProcessArea, Status
ORDER BY ProcessArea, ActiveCaseCount DESC;


-- ------------------------------------------------------------------------------
-- Q2: Overdue Cases
-- Business Purpose: Isolate active requests that have breached their target
--                   turnaround deadline relative to the reference timestamp.
-- ------------------------------------------------------------------------------
SELECT
    RequestID,
    Title,
    ProcessArea,
    RequestType,
    RiskLevel,
    Status,
    AssignedAnalyst,
    SubmissionDateTime,
    TargetDueDateTime,
    ROUND((JULIANDAY('2026-09-26 17:00:00') - JULIANDAY(TargetDueDateTime)) * 24.0, 1) AS HoursOverdue
FROM ComplianceRequest
WHERE Status != 'Closed'
  AND '2026-09-26 17:00:00' > TargetDueDateTime
ORDER BY HoursOverdue DESC;


-- ------------------------------------------------------------------------------
-- Q3: Approaching Deadlines
-- Business Purpose: Proactively flag active cases that are within their designated
--                   warning threshold (e.g. 6h for Critical, 24h for High/Medium).
-- ------------------------------------------------------------------------------
SELECT
    cr.RequestID,
    cr.Title,
    cr.ProcessArea,
    cr.RiskLevel,
    cr.Status,
    cr.AssignedAnalyst,
    cr.TargetDueDateTime,
    sp.WarningThresholdHours,
    ROUND((JULIANDAY(cr.TargetDueDateTime) - JULIANDAY('2026-09-26 17:00:00')) * 24.0, 1) AS HoursRemaining
FROM ComplianceRequest cr
JOIN SLAPolicy sp ON cr.RiskLevel = sp.RiskLevel
WHERE cr.Status != 'Closed'
  AND '2026-09-26 17:00:00' <= cr.TargetDueDateTime
  AND (JULIANDAY(cr.TargetDueDateTime) - JULIANDAY('2026-09-26 17:00:00')) * 24.0 <= sp.WarningThresholdHours
ORDER BY HoursRemaining ASC;


-- ------------------------------------------------------------------------------
-- Q4: SLA Performance (Closed Cases)
-- Business Purpose: Compute the overall regulatory SLA compliance rate and
--                   breach percentage across all historically resolved cases.
-- ------------------------------------------------------------------------------
SELECT
    COUNT(*) AS TotalClosedCases,
    SUM(CASE WHEN SLABreachFlag = 0 THEN 1 ELSE 0 END) AS CasesWithinSLA,
    SUM(CASE WHEN SLABreachFlag = 1 THEN 1 ELSE 0 END) AS CasesBreachedSLA,
    ROUND(100.0 * SUM(CASE WHEN SLABreachFlag = 0 THEN 1 ELSE 0 END) / COUNT(*), 2) AS SLAAchievedPercent,
    ROUND(100.0 * SUM(CASE WHEN SLABreachFlag = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS SLABreachPercent
FROM ComplianceRequest
WHERE Status = 'Closed';


-- ------------------------------------------------------------------------------
-- Q5: Process Area Cycle Time & Bottleneck Analysis
-- Business Purpose: Measure average turnaround time and closed case volumes by
--                   operational area to uncover stage delays without subjective bias.
-- ------------------------------------------------------------------------------
SELECT
    ProcessArea,
    COUNT(*) AS ClosedCases,
    ROUND(AVG((JULIANDAY(CompletionDateTime) - JULIANDAY(SubmissionDateTime)) * 24.0), 2) AS AvgResolutionHours,
    ROUND(MIN((JULIANDAY(CompletionDateTime) - JULIANDAY(SubmissionDateTime)) * 24.0), 2) AS MinResolutionHours,
    ROUND(MAX((JULIANDAY(CompletionDateTime) - JULIANDAY(SubmissionDateTime)) * 24.0), 2) AS MaxResolutionHours
FROM ComplianceRequest
WHERE Status = 'Closed'
GROUP BY ProcessArea
ORDER BY AvgResolutionHours DESC;


-- ------------------------------------------------------------------------------
-- Q6: Risk Level SLA Breach Performance
-- Business Purpose: Analyze whether higher-risk tiers experience higher breach
--                   rates due to investigative complexity or tighter SLAs.
-- ------------------------------------------------------------------------------
SELECT
    sp.RiskLevel,
    sp.SLATargetHours,
    COUNT(cr.RequestID) AS ClosedCases,
    SUM(CASE WHEN cr.SLABreachFlag = 1 THEN 1 ELSE 0 END) AS BreachedCases,
    ROUND(
        100.0 * SUM(CASE WHEN cr.SLABreachFlag = 1 THEN 1 ELSE 0 END) / COUNT(cr.RequestID),
        2
    ) AS BreachPercentage
FROM SLAPolicy sp
LEFT JOIN ComplianceRequest cr
    ON sp.RiskLevel = cr.RiskLevel AND cr.Status = 'Closed'
GROUP BY sp.RiskLevel, sp.SLATargetHours
ORDER BY sp.SLATargetHours ASC;


-- ------------------------------------------------------------------------------
-- Q7: Request Type Resolution Performance
-- Business Purpose: Evaluate average turnaround times across specific compliance
--                   workflow types (e.g. KYC vs Sanctions vs AML inquiries).
-- ------------------------------------------------------------------------------
SELECT
    RequestType,
    COUNT(*) AS ClosedCases,
    ROUND(AVG((JULIANDAY(CompletionDateTime) - JULIANDAY(SubmissionDateTime)) * 24.0), 2) AS AvgResolutionHours
FROM ComplianceRequest
WHERE Status = 'Closed'
GROUP BY RequestType
ORDER BY AvgResolutionHours DESC;


-- ------------------------------------------------------------------------------
-- Q8: Escalation Workload by Process Area
-- Business Purpose: Quantify the proportion and volume of requests requiring
--                   managerial intervention or specialist escalation by area.
-- ------------------------------------------------------------------------------
SELECT
    ProcessArea,
    COUNT(*) AS TotalRequests,
    SUM(CASE WHEN EscalationFlag = 1 THEN 1 ELSE 0 END) AS EscalatedCases,
    ROUND(100.0 * SUM(CASE WHEN EscalationFlag = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS EscalationRatePercent
FROM ComplianceRequest
GROUP BY ProcessArea
ORDER BY EscalatedCases DESC;


-- ------------------------------------------------------------------------------
-- Q9: Management Approval Workload by Risk Level
-- Business Purpose: Assess governance demand by determining how many cases require
--                   formal sign-off across risk tiers.
-- ------------------------------------------------------------------------------
SELECT
    RiskLevel,
    COUNT(*) AS TotalRequests,
    SUM(CASE WHEN ApprovalRequired = 1 THEN 1 ELSE 0 END) AS ApprovalRequiredCases,
    ROUND(100.0 * SUM(CASE WHEN ApprovalRequired = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS ApprovalRequiredPercent
FROM ComplianceRequest
GROUP BY RiskLevel
ORDER BY
    CASE RiskLevel
        WHEN 'Critical' THEN 1
        WHEN 'High'     THEN 2
        WHEN 'Medium'   THEN 3
        WHEN 'Low'      THEN 4
    END;


-- ------------------------------------------------------------------------------
-- Q10: Operational Queue Prioritization (Triaged Worklist)
-- Business Purpose: Deliver an actionable work queue for compliance managers and
--                   analysts ordered strictly by operational urgency:
--                   1. SLA Breach Status (Overdue first)
--                   2. Risk Level Severity (Critical -> High -> Medium -> Low)
--                   3. Target Due Timestamp (Earliest deadline first)
-- ------------------------------------------------------------------------------
SELECT
    RequestID,
    Title,
    ProcessArea,
    RequestType,
    RiskLevel,
    Priority,
    Status,
    AssignedAnalyst,
    SubmissionDateTime,
    TargetDueDateTime,
    CASE
        WHEN '2026-09-26 17:00:00' > TargetDueDateTime THEN 'Overdue'
        ELSE 'Within SLA'
    END AS OperationalSLAStatus
FROM ComplianceRequest
WHERE Status != 'Closed'
ORDER BY
    -- 1. Overdue requests first
    CASE WHEN '2026-09-26 17:00:00' > TargetDueDateTime THEN 0 ELSE 1 END ASC,
    -- 2. Risk Level severity
    CASE RiskLevel
        WHEN 'Critical' THEN 1
        WHEN 'High'     THEN 2
        WHEN 'Medium'   THEN 3
        WHEN 'Low'      THEN 4
    END ASC,
    -- 3. Earliest deadline
    TargetDueDateTime ASC;
