from flask import Flask, jsonify, request

app = Flask(__name__)

state = {
    "moisture": 40,
    "temperature": 25,
    "status": "IDLE"
}

def decide(moisture, temperature):

    print(f"Deciding with moisture: {moisture}, temperature: {temperature}")
    if moisture < 30 and temperature > 20:
        return "WATERING"
    return "IDLE"

# ESP32 энд data явуулна
@app.route("/update", methods=["POST"])
def update():
    data = request.json

    state["moisture"] = data["moisture"]
    state["temperature"] = data["temperature"]

    # AI ажиллуулна
    state["status"] = decide(
        state["moisture"],
        state["temperature"]
    )

    return jsonify({"message": "updated"})

# Frontend эндээс авна
@app.route("/data")
def get_data():
    return jsonify(state)

if __name__ == "__main__":
    app.run(debug=True)