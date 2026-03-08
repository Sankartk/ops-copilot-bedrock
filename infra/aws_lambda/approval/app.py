import json
import boto3
from datetime import datetime, timezone

sf = boto3.client("stepfunctions")


def _resp(code: int, body: dict):
    return {"statusCode": code, "headers": {"content-type": "application/json"}, "body": json.dumps(body)}


def handler(event, context):
    qs = event.get("queryStringParameters") or {}
    token = qs.get("token") or qs.get("taskToken")
    decision = (qs.get("decision") or "").upper()
    reason = qs.get("reason") or ""

    if not token:
        return _resp(400, {"ok": False, "error": "Missing token query param (?token=...)"})
    if decision not in ("APPROVE", "REJECT"):
        return _resp(400, {"ok": False, "error": "decision must be APPROVE or REJECT"})

    ts = datetime.now(timezone.utc).isoformat()

    if decision == "APPROVE":
        sf.send_task_success(taskToken=token, output=json.dumps({"decision": "APPROVE", "reason": reason, "ts": ts}))
        return _resp(200, {"ok": True, "decision": "APPROVE", "ts": ts})

    sf.send_task_failure(taskToken=token, error="REJECTED", cause=json.dumps({"decision": "REJECT", "reason": reason, "ts": ts}))
    return _resp(200, {"ok": True, "decision": "REJECT", "ts": ts})
