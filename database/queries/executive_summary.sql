-- ==============================================================================
-- ComplyFlow - Executive KPI Summary
-- ==============================================================================
-- Description: Compact, high-level operational compliance KPI summary designed
--              for management dashboards and executive reporting.
-- Engine:      SQLite
-- Anchor Date: 2026-09-26 17:00:00 (Simulation Reference Timestamp)
-- ==============================================================================

WITH SummaryMetrics AS (
    SELECT
        COUNT(*) AS TotalRequests,
        SUM(CASE WHEN cr.Status = 'Closed' THEN 1 ELSE 0 END) AS ClosedRequests,
        SUM(CASE WHEN cr.Status != 'Closed' THEN 1 ELSE 0 END) AS ActiveRequests,
        SUM(CASE WHEN cr.Status = 'Closed' AND cr.SLABreachFlag = 1 THEN 1 ELSE 0 END) AS ClosedBreachedRequests,
        ROUND(
            100.0 * SUM(CASE WHEN cr.Status = 'Closed' AND cr.SLABreachFlag = 1 THEN 1 ELSE 0 END) /
            NULLIF(SUM(CASE WHEN cr.Status = 'Closed' THEN 1 ELSE 0 END), 0),
            2
        ) AS SLABreachRatePercent,
        ROUND(
            AVG(CASE
                WHEN cr.Status = 'Closed' AND cr.CompletionDateTime IS NOT NULL
                THEN (JULIANDAY(cr.CompletionDateTime) - JULIANDAY(cr.SubmissionDateTime)) * 24.0
                ELSE NULL
            END),
            2
        ) AS AverageResolutionTimeHours,
        SUM(CASE WHEN cr.EscalationFlag = 1 THEN 1 ELSE 0 END) AS EscalatedRequests,
        SUM(CASE WHEN cr.ApprovalRequired = 1 THEN 1 ELSE 0 END) AS ApprovalRequiredRequests,
        SUM(CASE
            WHEN cr.Status != 'Closed' AND '2026-09-26 17:00:00' > cr.TargetDueDateTime
            THEN 1 ELSE 0
        END) AS CurrentlyOverdueRequests,
        SUM(CASE
            WHEN cr.Status != 'Closed'
             AND '2026-09-26 17:00:00' <= cr.TargetDueDateTime
             AND (JULIANDAY(cr.TargetDueDateTime) - JULIANDAY('2026-09-26 17:00:00')) * 24.0 <= sp.WarningThresholdHours
            THEN 1 ELSE 0
        END) AS ApproachingDeadlineRequests
    FROM ComplianceRequest cr
    JOIN SLAPolicy sp ON cr.RiskLevel = sp.RiskLevel
)
SELECT
    TotalRequests,
    ClosedRequests,
    ActiveRequests,
    SLABreachRatePercent,
    AverageResolutionTimeHours,
    EscalatedRequests,
    ApprovalRequiredRequests,
    CurrentlyOverdueRequests,
    ApproachingDeadlineRequests
FROM SummaryMetrics;
