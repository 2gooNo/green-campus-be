def _temperature_adjustment(temperature):
    # Hot weather should trigger earlier watering; cool weather can wait longer.
    if temperature >= 34:
        return (8, 6)
    if temperature >= 30:
        return (5, 4)
    if temperature >= 27:
        return (2, 2)
    if temperature <= 12:
        return (-4, -3)
    if temperature <= 18:
        return (-2, -1)
    return (0, 0)


def decide(moisture, temperature, previous_status="IDLE", trend_per_min=None):
    """Return WATERING or IDLE using a stateful, weather-aware policy.

    - Hysteresis: separate start/stop moisture thresholds.
    - Temperature-aware: hot weather raises thresholds, cool weather lowers them.
    - Trend-aware: if moisture is dropping quickly, start watering earlier.
    """
    base_start = 30
    base_stop = 55

    start_adj, stop_adj = _temperature_adjustment(temperature)
    start_threshold = base_start + start_adj
    stop_threshold = base_stop + stop_adj

    # If moisture is dropping quickly, anticipate stress and start a bit earlier.
    if trend_per_min is not None and trend_per_min <= -2.5:
        start_threshold += 3

    # Keep watering until we reach the upper threshold (hysteresis).
    if previous_status == "WATERING":
        if moisture >= stop_threshold:
            return "IDLE"
        return "WATERING"

    # Emergency protection for very hot conditions.
    if temperature >= 38 and moisture < 45:
        return "WATERING"

    if moisture <= start_threshold:
        return "WATERING"

    return "IDLE"