import json
from datetime import datetime, timezone
import boto3

ecs = boto3.client("ecs")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def handler(event, context):
    cluster = event.get("cluster")
    service = event.get("service")
    prev_td = event.get("previous_task_definition")

    if not cluster or not service or not prev_td:
        return {"ok": False, "skipped": True, "ts": _now(), "reason": "Provide cluster/service/previous_task_definition explicitly."}

    ecs.update_service(cluster=cluster, service=service, taskDefinition=prev_td, forceNewDeployment=True)
    return {"ok": True, "ts": _now(), "cluster": cluster, "service": service, "task_definition": prev_td}
