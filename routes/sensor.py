from datetime import datetime

from flask import Blueprint, jsonify, request

from ai import decide
from config import collection


sensor_bp = Blueprint("sensor", __name__)

system = {
    "auto_mode": True,
}


@sensor_bp.route("/update", methods=["POST"])
def update():
    data = request.json

    moisture = data.get("moisture")
    temperature = data.get("temperature")

    if moisture is None or temperature is None:
        return jsonify({"error": "Invalid data"}), 400

    status = "IDLE"
    if system["auto_mode"]:
        status = decide(moisture, temperature)

    document = {
        "moisture": moisture,
        "temperature": temperature,
        "status": status,
        "auto_mode": system["auto_mode"],
        "manual": False,
        "timestamp": datetime.utcnow(),
    }

    collection.insert_one(document)

    return jsonify({"message": "data received", "status": status})
