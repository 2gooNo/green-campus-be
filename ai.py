def decide(moisture, temperature):
    if moisture < 30 and temperature > 20:
        return "WATERING"
    return "IDLE"