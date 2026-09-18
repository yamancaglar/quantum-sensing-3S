# MQTT Pipeline Test

A proof-of-concept validating the full data path: **device -> MQTT broker -> subscriber -> SQLite**, using fake sensor data instead of the real black box (at the time of this test, I was not able to run the black box). 
Built to de-risk the software side while hardware details were still being sorted out.

## What's here

- `fake_publisher.py` - simulates the black box. Publishes fake photodiode + current readings once per second to the MQTT broker, toggling `mw_active` on/off every 5 seconds.
- `pi_subscriber.py` - the real backend logic. Subscribes to the readings topic, inserts each one into a local SQLite database (`blackbox_test.db`, created automatically on first run).

## Setup

Both scripts need `paho-mqtt` installed. Use a virtual environment (required on Linux, recommended on Windows):

```bash
python3 -m venv venv
source venv/bin/activate       # bash/zsh
# or: source venv/bin/activate.fish   # fish shell < required for my laptop, nice to have in the file
pip install paho-mqtt
```

## Running it

**On the Pi** (runs the MQTT broker + subscriber):

```bash
python3 pi_subscriber.py
```

This creates `blackbox_test.db` in this folder and starts listening.

**On your laptop** (or wherever, as long as it can reach the Pi):

Edit `BROKER_HOST` in `fake_publisher.py` to match the Pi's IP address on your network, then:

```bash
python3 fake_publisher.py
```

You should see matching log lines on both sides as data flows through.

## Checking the data

```bash
sqlite3 blackbox_test.db "SELECT * FROM measurements LIMIT 10;"
```

Each row should have `photodiode_value`, `current_value`, and `mw_active` populated together - you should see the photodiode value dip when `mw_active` flips to `1`.

## Notes

- `blackbox_test.db` is gitignored - it's test data, not something to commit.
- Requires a Mosquitto (or other MQTT) broker running and reachable on the target host - see `docker/mosquitto/` for the broker config, or install it directly with `sudo apt install mosquitto` on the Pi.
- This is throwaway test tooling, not production code. Once real hardware data is available, this gets replaced by the actual firmware -> MQTT -> backend path, following or iterating the same schema proven here.
