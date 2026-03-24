def decide(moisture, temperature):
    # Water only when soil is dry and temperature is warm enough.
    if moisture < 30 and temperature > 20:
        return "WATERING"
    return "IDLE"