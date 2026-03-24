from flask import Blueprint, jsonify

from config import collection


data_bp = Blueprint("data", __name__)


@data_bp.route("/data")
def get_data():
    # Return the most recent stored reading.
    latest = collection.find_one(sort=[("timestamp", -1)])

    if latest:
        latest["_id"] = str(latest["_id"])
        return jsonify(latest)

    return jsonify({"error": "No data"})


@data_bp.route("/history")
def history():
    # Return the latest 20 readings for charts/tables.
    data = list(collection.find().sort("timestamp", -1).limit(20))

    for item in data:
        item["_id"] = str(item["_id"])

    return jsonify(data)
