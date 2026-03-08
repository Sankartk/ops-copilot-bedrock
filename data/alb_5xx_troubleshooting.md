# File: data/alb_5xx.md

# ALB HTTP 5xx Spike Runbook

## Scope

This runbook applies when:

* HTTPCode_ELB_5XX_Count increases
* TargetResponseTime increases
* HealthyHostCount drops
* Applications report intermittent 5xx errors

---

## Symptoms

* Spike in ALB 5xx errors
* Failed health checks
* Increased latency
* Deployment recently occurred
* Partial service outage

---

## Immediate Triage

1. Check CloudWatch metrics:

   * HTTPCode_ELB_5XX_Count
   * TargetResponseTime
   * HealthyHostCount
   * RequestCount

2. Verify target group health:

   * Confirm all targets are healthy
   * Validate health check path and port
   * Confirm success codes are correct

3. Inspect ECS task logs:

   * Application exceptions
   * Crash loops
   * OOMKilled events
   * Startup failures

4. Review recent deployments:

   * Identify last successful task definition revision
   * Check configuration or environment variable changes

---

## Diagnostics

### Validate Target Group Health

```bash
aws elbv2 describe-target-health --target-group-arn <target_group_arn>
```

---

### Inspect ECS Tasks

```bash
aws ecs describe-tasks --cluster <cluster_name> --tasks <task_id>
```

Check:

* stoppedReason
* exitCode
* container health status

---

## Mitigation (Safe Actions)

Rollback to last stable revision:

```bash
aws ecs update-service \
  --cluster <cluster_name> \
  --service <service_name> \
  --task-definition <previous_revision> \
  --force-new-deployment
```

Additional actions:

* Increase task count temporarily
* Fix misconfigured health checks

---

## Common Root Causes

* Bad container release
* Application exception on startup
* Missing environment variable
* Security group blocking traffic
* Incorrect health check endpoint

---

## Runbook Signals

**Metrics**

* HTTPCode_ELB_5XX_Count
* TargetResponseTime
* HealthyHostCount

**Logs**

* ECS task logs
* Application logs
* ALB access logs

**Dashboards**

* CloudWatch ALB dashboard
* ECS service dashboard
