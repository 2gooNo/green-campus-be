from flask import Flask, jsonify, request
from datetime import datetime
from config import collection
from ai import decide

app = Flask(__name__)

# 📤 ESP32 → data илгээх endpoint
@app.route("/update", methods=["POST"])
def update():
    data = request.json

    moisture = data.get("moisture")
    temperature = data.get("temperature")

    # AI decision
    status = decide(moisture, temperature)

    # MongoDB-д хадгалах
    document = {
        "moisture": moisture,
        "temperature": temperature,
        "status": status,
        "timestamp": datetime.utcnow()
    }

    collection.insert_one(document)

    return jsonify({
        "message": "Data saved",
        "status": status
    })


# 📥 Frontend → latest data авах
@app.route("/data")
def get_data():
    latest = collection.find_one(sort=[("timestamp", -1)])

    if latest:
        latest["_id"] = str(latest["_id"])
        return jsonify(latest)

    return jsonify({"error": "No data found"})


# 📊 Graph-д зориулсан history
@app.route("/history")
def history():
    data = list(collection.find().sort("timestamp", -1).limit(20))

    for d in data:
        d["_id"] = str(d["_id"])

    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)