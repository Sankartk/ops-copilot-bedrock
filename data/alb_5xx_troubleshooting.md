# ALB 5xx Troubleshooting Runbook

## Symptoms
- Spike in HTTP 5xx errors
- Failed health checks
- Increased response times

## Investigation Steps
1. Check target group health
2. Inspect ECS task logs
3. Review deployment changes
4. Validate security groups

## CloudWatch Metrics
- HTTPCode_ELB_5XX_Count
- TargetResponseTime
- HealthyHostCount

## Common Causes
- Bad container release
- App crash loops
- Health check misconfiguration
- Security group blocks

## Mitigation
- Rollback service
- Increase task count
- Fix health check path
