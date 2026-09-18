"""
Runs on a publisher device, for the purpose of this test, on Yaman Caglar's laptop.
Simulates the black box publishing photodiode + current readings over MQTT.

Install once: pip install paho-mqtt
Run: python3 fake_publisher.py
"""

import json
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

BROKER_HOST = "10.42.0.141"  # the Pi's IP on the shared ethernet link, hardcoded for testing purposes
BROKER_PORT = 1883

TOPIC_READING = "quantumsensor/test/reading"

PUBLISH_INTERVAL_SECONDS = 1.0


def make_reading(mw_active: bool) -> dict:
    # Baseline ~124 nW (matches the report's real readings), with a dip when MW is "active"
    baseline = 124.0
    noise = random.uniform(-0.3, 0.3)
    dip = -2.0 if mw_active else 0.0
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "photodiode_value": round(baseline + dip + noise, 2),
        "current_value": round(random.uniform(0.04, 0.06), 4),  # fake amps
        "mw_active": int(mw_active),
    }


def main():
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    print(f"Publishing fake data to {BROKER_HOST}:{BROKER_PORT} every {PUBLISH_INTERVAL_SECONDS}s. Ctrl+C to stop.")

    tick = 0
    try:
        while True:
            # toggle mw_active every 5 seconds, just to simulate switching behavior
            mw_active = (tick // 5) % 2 == 1

            reading = make_reading(mw_active)

            client.publish(TOPIC_READING, json.dumps(reading), qos=1)

            print(f"Published: photodiode={reading['photodiode_value']} "
                  f"(mw_active={mw_active}) current={reading['current_value']}")

            tick += 1
            time.sleep(PUBLISH_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
