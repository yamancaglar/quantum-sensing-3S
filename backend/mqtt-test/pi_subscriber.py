"""
Runs on the Pi (in ./backend/mqtt-test folder).
Subscribes to fake sensor data topics and inserts them into a local SQLite DB.

Install once: pip install paho-mqtt
Run: python3 pi_subscriber.py
"""

import json
import sqlite3
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

DB_PATH = "blackbox_test.db"
BROKER_HOST = "localhost"  # broker is running on this same Pi
BROKER_PORT = 1883

TOPIC_READING = "quantumsensor/test/reading"

# Tracks which run new measurements should be attached to.
# For this test setup, we just open one run at startup and use it for everything.
current_run_id = None


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            frequency_hz REAL,
            power_dbm REAL,
            label TEXT,
            notes TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES runs(id),
            timestamp TEXT NOT NULL,
            photodiode_value REAL,
            current_value REAL,
            mw_active INTEGER
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_measurements_run_id ON measurements(run_id)")
    conn.commit()
    return conn


def start_test_run(conn, device_id="fake-laptop-device"):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO runs (device_id, started_at, label, notes) VALUES (?, ?, ?, ?)",
        (device_id, now, "MQTT pipeline test", "Auto-created by pi_subscriber.py on startup"),
    )
    conn.commit()
    print(f"Started test run id={cur.lastrowid} at {now}")
    return cur.lastrowid


def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connected to broker (rc={rc}). Subscribing...")
    client.subscribe(TOPIC_READING)


def on_message(client, userdata, msg):
    conn = userdata["conn"]
    run_id = userdata["run_id"]

    try:
        payload = json.loads(msg.payload.decode("utf-8"))
    except json.JSONDecodeError:
        print(f"Skipping non-JSON message on {msg.topic}: {msg.payload}")
        return

    timestamp = payload.get("timestamp", datetime.now(timezone.utc).isoformat())

    conn.execute(
        "INSERT INTO measurements (run_id, timestamp, photodiode_value, current_value, mw_active) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            run_id,
            timestamp,
            payload.get("photodiode_value"),
            payload.get("current_value"),
            payload.get("mw_active", 0),
        ),
    )
    conn.commit()
    print(f"[reading] {timestamp} -> photodiode={payload.get('photodiode_value')} "
          f"current={payload.get('current_value')} mw_active={payload.get('mw_active', 0)}")


def main():
    conn = init_db()
    run_id = start_test_run(conn)

    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.user_data_set({"conn": conn, "run_id": run_id})
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    print("Listening for messages... Ctrl+C to stop.")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStopping. Closing out the run...")
        conn.execute(
            "UPDATE runs SET ended_at = ? WHERE id = ?",
            (datetime.now(timezone.utc).isoformat(), run_id),
        )
        conn.commit()
        conn.close()


if __name__ == "__main__":
    main()
