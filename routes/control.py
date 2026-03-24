from datetime import datetime

from flask import Blueprint, jsonify, request

from auto_mode_store import get_auto_mode, set_auto_mode
from config import collection


control_bp = Blueprint("control", __name__)


@control_bp.route("/command")
def command():
    # ESP32 polls this endpoint for the latest action.
    latest = collection.find_one(sort=[("timestamp", -1)])

    if not latest:
        return jsonify({"action": "IDLE"})

    return jsonify({"action": latest["status"]})


@control_bp.route("/water", methods=["POST"])
def water():
    # Manual trigger toggles WATERING <-> IDLE using latest state.
    latest = collection.find_one(sort=[("timestamp", -1)])

    if not latest:
        return jsonify({"error": "No data"}), 400

    auto_mode = get_auto_mode()
    next_status = "IDLE" if latest.get("status") == "WATERING" else "WATERING"

    document = {
        "moisture": latest["moisture"],
        "temperature": latest["temperature"],
        "status": next_status,
        "auto_mode": auto_mode,
        "manual": True,
        "timestamp": datetime.utcnow(),
    }

    collection.insert_one(document)

    return jsonify({"message": "manual watering toggled", "status": next_status})


@control_bp.route("/toggle-auto", methods=["POST"])
def toggle_auto():

    print("Received request to toggle auto mode")
    # Frontend passes the desired auto_mode value directly.
    payload = request.get_json(silent=True) or {}
    requested_auto_mode = payload.get("auto_mode")

    if type(requested_auto_mode) is not bool:
        return jsonify({"error": "auto_mode must be boolean"}), 400

    auto_mode = set_auto_mode(requested_auto_mode)

    print(f"Auto mode set to {auto_mode}")

    return jsonify({"auto_mode": auto_mode})

@control_bp.route("/status")
def status():
    # Combined status for UI: latest reading + current auto mode.
    latest = collection.find_one(sort=[("timestamp", -1)])
    auto_mode = get_auto_mode()

    if not latest:
        return jsonify({"error": "No data"}), 400

    return jsonify({
        "moisture": latest["moisture"],
        "temperature": latest["temperature"],
        "status": latest["status"],
        "auto_mode": auto_mode,
        "manual": latest["manual"],
    })
