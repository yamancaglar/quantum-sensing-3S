# Webserver

Flask app serving a read-only JSON API over the SQLite database. See [API.md](API.md) for endpoints.
Currently reads `backend/mock.db` (mock data from `feature/dummy-data`; `*.db` is gitignored, copy it in manually).

## Setup (Raspberry Pi)
```
cd backend/webserver
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # optional; DB_PATH defaults to ../mock.db
```

## Run
```
DB_PATH=../mock.db .venv/bin/flask --app app run --host 0.0.0.0 --port 5000
```

## Test
```
.venv/bin/python -m pytest -q
```
