import argparse
import json
import random
import time
from datetime import datetime
from urllib import error, request


class SoilModel:
    def __init__(
        self,
        moisture_start=55.0,
        temperature_start=26.0,
        dry_rate_per_sec=0.06,
        water_rate_per_sec=1.1,
        temp_base=26.0,
        temp_noise=0.25,
    ):
        self.moisture = moisture_start
        self.temperature = temperature_start
        self.dry_rate_per_sec = dry_rate_per_sec
        self.water_rate_per_sec = water_rate_per_sec
        self.temp_base = temp_base
        self.temp_noise = temp_noise
        self._last = time.time()

    def step(self, is_watering: bool):
        now = time.time()
        dt = max(0.0, now - self._last)
        self._last = now

        if is_watering:
            self.moisture += self.water_rate_per_sec * dt
        else:
            self.moisture -= self.dry_rate_per_sec * dt

        self.moisture = max(5.0, min(95.0, self.moisture))

        # Simulate small ambient temperature drift/noise.
        self.temperature += (self.temp_base - self.temperature) * 0.02
        self.temperature += random.uniform(-self.temp_noise, self.temp_noise)
        self.temperature = max(15.0, min(42.0, self.temperature))

        return {
            "moisture": round(self.moisture, 2),
            "temperature": round(self.temperature, 2),
        }


def _http_json(method: str, url: str, payload=None, timeout=5):
    data = None
    headers = {"Content-Type": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = request.Request(url=url, data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        if not raw:
            return {}
        return json.loads(raw)


def send_update(base_url: str, payload: dict):
    return _http_json("POST", f"{base_url}/update", payload=payload)


def get_action(base_url: str):
    try:
        data = _http_json("GET", f"{base_url}/command")
        return str(data.get("action", "IDLE")).upper()
    except Exception:
        return "IDLE"


def main():
    parser = argparse.ArgumentParser(description="Continuous ESP32 fake sensor simulator")
    parser.add_argument("--base-url", default="http://127.0.0.1:5000", help="Flask API base URL")
    parser.add_argument("--interval", type=float, default=3.0, help="Seconds between sensor pushes")
    parser.add_argument("--start-moisture", type=float, default=55.0, help="Initial moisture")
    parser.add_argument("--start-temp", type=float, default=26.0, help="Initial temperature")
    parser.add_argument("--dry-rate", type=float, default=0.06, help="Moisture decrease per second when idle")
    parser.add_argument("--water-rate", type=float, default=1.1, help="Moisture increase per second when watering")

    args = parser.parse_args()

    model = SoilModel(
        moisture_start=args.start_moisture,
        temperature_start=args.start_temp,
        dry_rate_per_sec=args.dry_rate,
        water_rate_per_sec=args.water_rate,
    )

    print("Starting fake ESP32 stream. Press Ctrl+C to stop.")
    print(f"Base URL: {args.base_url} | interval: {args.interval}s")

    while True:
        action = get_action(args.base_url)
        is_watering = action == "WATERING"

        reading = model.step(is_watering=is_watering)

        try:
            result = send_update(args.base_url, reading)
            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"action={action:<8} "
                f"moisture={reading['moisture']:>5} "
                f"temp={reading['temperature']:>5} "
                f"server_status={result.get('status', '-')}")
        except error.URLError as exc:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] connection error: {exc}")
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] unexpected error: {exc}")

        time.sleep(max(0.2, args.interval))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped fake ESP32 stream.")
