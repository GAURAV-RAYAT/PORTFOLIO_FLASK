from datetime import datetime
import requests

from config import Config
from database import get_collection
from utils.mail_helper import send_monitoring_alert_email


def parse_monitor_targets():
    """Parse monitoring targets from comma-separated env configuration."""
    raw_targets = Config.MONITOR_TARGETS or ""
    return [item.strip() for item in raw_targets.split(",") if item.strip()]


def get_latest_status(target_url):
    """Fetch latest monitoring status document for a target."""
    collection = get_collection("monitoring_status")
    if collection is None:
        return None
    return collection.find_one({"target_url": target_url})


def upsert_status(target_url, consecutive_failures, last_state, last_reason, status_code=None):
    """Persist latest status snapshot per target."""
    collection = get_collection("monitoring_status")
    if collection is None:
        return
    collection.update_one(
        {"target_url": target_url},
        {
            "$set": {
                "target_url": target_url,
                "consecutive_failures": consecutive_failures,
                "last_state": last_state,
                "last_reason": last_reason,
                "status_code": status_code,
                "updated_at": datetime.utcnow(),
            }
        },
        upsert=True,
    )


def save_monitoring_event(target_url, state, status_code=None, reason=""):
    """Store each monitoring check event."""
    collection = get_collection("monitoring_events")
    if collection is None:
        return
    collection.insert_one(
        {
            "target_url": target_url,
            "state": state,
            "status_code": status_code,
            "reason": reason,
            "checked_at": datetime.utcnow(),
        }
    )


def check_target(target_url):
    """Run one health check for a target URL."""
    timeout = Config.MONITOR_TIMEOUT_SECONDS
    try:
        response = requests.get(target_url, timeout=timeout)
        if 200 <= response.status_code < 400:
            return {
                "success": True,
                "status_code": response.status_code,
                "reason": "OK",
            }
        return {
            "success": False,
            "status_code": response.status_code,
            "reason": f"Unexpected HTTP status {response.status_code}",
        }
    except Exception as e:
        return {
            "success": False,
            "status_code": None,
            "reason": str(e),
        }


def run_monitoring_cycle():
    """Run one complete monitoring pass and trigger alerts when needed."""
    targets = parse_monitor_targets()
    threshold = Config.MONITOR_FAILURE_THRESHOLD
    results = []

    for target in targets:
        current = check_target(target)
        previous = get_latest_status(target) or {}
        prev_failures = int(previous.get("consecutive_failures", 0))
        prev_state = previous.get("last_state", "healthy")

        if current["success"]:
            state = "healthy"
            failures = 0
            if prev_state == "failing":
                send_monitoring_alert_email(
                    target_url=target,
                    status_code=current["status_code"],
                    reason="Endpoint recovered.",
                    recovery=True,
                )
        else:
            failures = prev_failures + 1
            state = "failing" if failures >= threshold else "degraded"
            if failures == threshold:
                send_monitoring_alert_email(
                    target_url=target,
                    status_code=current["status_code"],
                    reason=current["reason"],
                    recovery=False,
                )

        save_monitoring_event(
            target_url=target,
            state=state,
            status_code=current["status_code"],
            reason=current["reason"],
        )
        upsert_status(
            target_url=target,
            consecutive_failures=failures,
            last_state=state,
            last_reason=current["reason"],
            status_code=current["status_code"],
        )

        results.append(
            {
                "target_url": target,
                "state": state,
                "status_code": current["status_code"],
                "reason": current["reason"],
                "consecutive_failures": failures,
            }
        )

    return results
