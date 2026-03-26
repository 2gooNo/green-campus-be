from datetime import datetime

from flask import Blueprint, jsonify, request

from ai import decide
from auto_mode_store import get_auto_mode
from config import collection


sensor_bp = Blueprint("sensor", __name__)


def _trend_per_min(previous_moisture, previous_timestamp, current_moisture, now_utc):
    if previous_moisture is None or previous_timestamp is None:
        return None

    elapsed_min = (now_utc - previous_timestamp).total_seconds() / 60.0
    if elapsed_min <= 0:
        return None

    return (current_moisture - previous_moisture) / elapsed_min


@sensor_bp.route("/update", methods=["POST"])
def update():
    # Sensor payload from ESP32.
    data = request.json

    moisture = data.get("moisture")
    temperature = data.get("temperature")

    print(f"Received sensor update: moisture={moisture}, temperature={temperature}")

    if moisture is None or temperature is None:
        return jsonify({"error": "Invalid data"}), 400

    now_utc = datetime.utcnow()

    # Auto mode is persisted in DB, not in-memory.
    auto_mode = get_auto_mode()

    # Get the latest reading to check if manual override is active.
    latest = collection.find_one(sort=[("timestamp", -1)])
    is_manual = latest.get("manual", False) if latest else False

    # Only recalculate if not in manual mode.
    status = "IDLE"
    if is_manual:
        status = latest.get("status", "IDLE")  # Keep the manual status.
    elif auto_mode:
        previous_status = latest.get("status", "IDLE") if latest else "IDLE"
        moisture_trend = _trend_per_min(
            latest.get("moisture") if latest else None,
            latest.get("timestamp") if latest else None,
            moisture,
            now_utc,
        )
        status = decide(
            moisture,
            temperature,
            previous_status=previous_status,
            trend_per_min=moisture_trend,
        )

    document = {
        # Store incoming reading with computed actuator status.
        "moisture": moisture,
        "temperature": temperature,
        "status": status,
        "auto_mode": auto_mode,
        "manual": is_manual,  # Preserve manual flag.
        "timestamp": now_utc,
    }

    collection.insert_one(document)

    return jsonify({"message": "data received", "status": status})
