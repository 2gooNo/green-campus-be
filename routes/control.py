from datetime import datetime

from flask import Blueprint, jsonify

from config import collection
from .sensor import system


control_bp = Blueprint("control", __name__)


@control_bp.route("/command")
def command():
    latest = collection.find_one(sort=[("timestamp", -1)])

    if not latest:
        return jsonify({"action": "IDLE"})

    return jsonify({"action": latest["status"]})


@control_bp.route("/water", methods=["POST"])
def water():
    latest = collection.find_one(sort=[("timestamp", -1)])

    if not latest:
        return jsonify({"error": "No data"}), 400

    document = {
        "moisture": latest["moisture"],
        "temperature": latest["temperature"],
        "status": "WATERING",
        "auto_mode": system["auto_mode"],
        "manual": True,
        "timestamp": datetime.utcnow(),
    }

    collection.insert_one(document)

    return jsonify({"message": "manual watering triggered"})


@control_bp.route("/toggle-auto", methods=["POST"])
def toggle_auto():
    system["auto_mode"] = not system["auto_mode"]

    return jsonify({"auto_mode": system["auto_mode"]})
