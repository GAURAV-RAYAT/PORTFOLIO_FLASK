from flask import Blueprint, jsonify
from datetime import datetime

from config import Config
from database import get_client
from utils.monitoring_agent import run_monitoring_cycle

bp = Blueprint("monitoring", __name__)


@bp.route("/api/health", methods=["GET"])
def health_check():
    """Basic health endpoint for uptime monitoring."""
    return jsonify(
        {
            "status": "ok",
            "service": "gauravrayat.me",
            "database_connected": get_client() is not None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    ), 200


@bp.route("/api/monitoring/run", methods=["POST"])
def run_monitoring_now():
    """
    Manual endpoint to run one monitoring cycle.
    Recommended usage: external cron/webhook trigger.
    """
    from flask import request

    # Fail-closed: if token not configured, deny all requests
    if not Config.MONITOR_RUN_TOKEN:
        return jsonify({"ok": False, "error": "Monitoring run token not configured"}), 503
    incoming_token = request.headers.get("X-Monitor-Token")
    if incoming_token != Config.MONITOR_RUN_TOKEN:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    results = run_monitoring_cycle()
    return jsonify({"ok": True, "results": results}), 200
