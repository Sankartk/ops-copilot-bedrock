# File: data/ecs_deployment_rollback.md

# ECS Deployment Rollback Runbook

## Scope

Use when:

* New deployment causes failures
* 5xx errors spike post-release
* Tasks fail health checks
* Crash loops detected

---

## Symptoms

* Increased HTTP 5xx
* Tasks in STOPPED state
* OOMKilled containers
* Application startup failures

---

## Immediate Actions

1. Identify current task definition revision
2. Identify last stable revision
3. Review deployment history
4. Compare environment variables

---

## Diagnostics

### View Service Deployments

```bash
aws ecs describe-services \
  --cluster <cluster_name> \
  --services <service_name>
```

Check:

* runningCount
* pendingCount
* failed deployments

---

### Inspect Stopped Tasks

```bash
aws ecs describe-tasks \
  --cluster <cluster_name> \
  --tasks <task_id>
```

Look for:

* exitCode
* stoppedReason
* health status

---

## Rollback Procedure

```bash
aws ecs update-service \
  --cluster <cluster_name> \
  --service <service_name> \
  --task-definition <previous_revision> \
  --force-new-deployment
```

---

## Post-Rollback Verification

* Confirm steady state
* Validate CloudWatch metrics normalize
* Run smoke tests
* Monitor for 15–30 minutes

---

## Runbook Signals

**Metrics**

* CPUUtilization
* MemoryUtilization
* HTTPCode_ELB_5XX_Count

**Logs**

* ECS task logs
* Container logs

**Dashboards**

* ECS service dashboard
* CloudWatch metrics dashboard
