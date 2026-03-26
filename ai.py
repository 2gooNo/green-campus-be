def decide(moisture, temperature):
    # Water only when soil is dry.
    if moisture < 30:
        return "WATERING"
    return "IDLE"