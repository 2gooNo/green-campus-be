from datetime import datetime

from flask import Blueprint, jsonify, request

from ai import decide
from auto_mode_store import get_auto_mode
from config import collection


sensor_bp = Blueprint("sensor", __name__)


@sensor_bp.route("/update", methods=["POST"])
def update():
    # Sensor payload from ESP32.
    data = request.json

    moisture = data.get("moisture")
    temperature = data.get("temperature")

    if moisture is None or temperature is None:
        return jsonify({"error": "Invalid data"}), 400

    # Auto mode is persisted in DB, not in-memory.
    auto_mode = get_auto_mode()

    status = "IDLE"
    if auto_mode:
        status = decide(moisture, temperature)

    document = {
        # Store incoming reading with computed actuator status.
        "moisture": moisture,
        "temperature": temperature,
        "status": status,
        "auto_mode": auto_mode,
        "manual": False,
        "timestamp": datetime.utcnow(),
    }

    collection.insert_one(document)

    return jsonify({"message": "data received", "status": status})
