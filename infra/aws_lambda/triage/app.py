import json
import uuid
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def handler(event, context):
    execution_id = getattr(context, "aws_request_id", None) or str(uuid.uuid4())

    detail = event.get("detail", {}) or {}
    state = detail.get("state", {}) or {}

    incident = {
        "alarm": detail.get("alarmName", "unknown-alarm"),
        "state_value": state.get("value", "UNKNOWN"),
        "state_reason": state.get("reason", ""),
        "event_time": event.get("time"),
        "account": event.get("account"),
        "region": event.get("region"),
    }

    alarm = (incident["alarm"] or "").lower()
    if "ecs" in alarm or "rollback" in alarm or "deploy" in alarm:
        recommendation = {"action": "ECS_ROLLBACK", "why": "Signals suggest deploy regression; propose rollback behind approval."}
    else:
        recommendation = {"action": "TRIAGE_ONLY", "why": "Conservative default triage."}

    approval_message = {
        "time": _now(),
        "execution_id": execution_id,
        "incident": incident,
        "recommendation": recommendation,
        "how_to_approve": "Use the APPROVE/REJECT links below (token is time-limited by Step Functions).",
    }

    return {"incident": incident, "recommendation": recommendation, "approval_message": json.dumps(approval_message, indent=2)}
