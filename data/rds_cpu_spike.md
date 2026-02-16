# RDS CPU Spike Runbook

## Symptoms
- CPU > 80%
- Slow queries
- Application timeouts

## Immediate Actions
1. Check Performance Insights
2. Identify top SQL queries
3. Review recent schema changes

## Diagnostics

SELECT pid, query, state
FROM pg_stat_activity
ORDER BY query_start DESC;

## Mitigation
- Kill long-running queries
- Scale instance class
- Add read replicas
- Optimize indexes

## Long-term Fix
- Query optimization
- Connection pooling
- Autoscaling read replicas
