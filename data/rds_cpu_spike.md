# File: data/rds_cpu.md

# RDS CPU Spike Runbook

## Scope

Use this runbook when:

* CPUUtilization > 80% sustained
* Application latency increases
* Slow queries observed
* Database connections spike

---

## Symptoms

* CPUUtilization > 80%
* Slow queries
* Increased DatabaseConnections
* Application timeouts
* High DB load (Performance Insights)

---

## Immediate Actions

1. Check CloudWatch metrics:

   * CPUUtilization
   * DatabaseConnections
   * FreeableMemory
   * ReadIOPS / WriteIOPS

2. Review Performance Insights:

   * Top SQL queries by load
   * Wait events
   * DB load vs vCPU

3. Validate connection usage:

   * Connection spikes
   * Pool misconfiguration
   * Idle connections not released

---

## Diagnostics

### PostgreSQL / Aurora PostgreSQL

```sql
SELECT pid,
       now() - query_start AS duration,
       state,
       query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start ASC;
```

Check connection count:

```sql
SELECT count(*) FROM pg_stat_activity;
```

---

### MySQL / Aurora MySQL

```sql
SHOW PROCESSLIST;
```

---

## Mitigation (Safe Actions)

Perform only if CPU remains high:

* Terminate long-running queries:

```sql
SELECT pg_terminate_backend(pid);
```

* Optimize heavy queries
* Add missing indexes
* Scale instance class
* Add read replicas

---

## Use Caution

* Do NOT stop the DB instance
* Avoid blindly increasing max_connections
* Avoid parameter changes without testing

---

## Long-Term Fix

* Implement RDS Proxy / PgBouncer
* Optimize ORM queries
* Autoscale read replicas
* Implement query timeouts
* Review schema design

---

## Runbook Signals

**Metrics**

* CPUUtilization
* DatabaseConnections
* DBLoad

**Logs**

* Slow query logs
* DB timeout logs

**Dashboards**

* CloudWatch RDS dashboard
* Performance Insights dashboard
