"""Read-only SQLite access for the API."""
import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    if "db" not in g:
        path = Path(current_app.config["DB_PATH"]).resolve()
        g.db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
