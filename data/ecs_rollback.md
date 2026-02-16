# ECS Service Rollback Runbook

## Symptoms
- New deployment causing 5xx errors
- Increased latency after release
- Task failures in ECS service

## Immediate Checks
1. Check ALB target health
2. Review CloudWatch logs
3. Compare task definition revisions

## Rollback Steps
1. Go to ECS Console
2. Select Cluster → Service
3. Click “Deployments”
4. Identify last stable revision
5. Update service → select previous task definition
6. Force new deployment

## CLI Rollback

aws ecs update-service \
  --cluster <cluster> \
  --service <service> \
  --task-definition <previous_revision> \
  --force-new-deployment

## Post-Rollback Validation
- Monitor ALB 5xx
- Verify task health
- Confirm latency normalized
