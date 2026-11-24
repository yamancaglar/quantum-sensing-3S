"""API routes. The UI talks only to these; it never touches the database."""
from flask import Blueprint, abort, jsonify, request

from db import get_db

bp = Blueprint("api", __name__, url_prefix="/api/v1")

MEAS_COLS = "timestamp, sweep_id, b_mt, f_minus_hz, f_plus_hz, contrast, linewidth_hz, fit_ok"
MAX_LIMIT = 1000


def _int_arg(name, default, lo=0, hi=None):
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        val = int(raw)
    except ValueError:
        abort(400, description=f"'{name}' must be an integer")
    if val < lo or (hi is not None and val > hi):
        abort(400, description=f"'{name}' out of range")
    return val


def _rows(cur):
    return [dict(r) for r in cur.fetchall()]


@bp.get("/health")
def health():
    get_db().execute("SELECT 1").fetchone()
    return jsonify(status="ok", db="reachable")


@bp.get("/sweeps")
def list_sweeps():
    limit = _int_arg("limit", 100, 1, MAX_LIMIT)
    offset = _int_arg("offset", 0)
    since = request.args.get("since")
    sql, args = "SELECT * FROM sweeps", []
    if since:
        sql += " WHERE started_at >= ?"
        args.append(since)
    sql += " ORDER BY started_at LIMIT ? OFFSET ?"
    args += [limit, offset]
    return jsonify(sweeps=_rows(get_db().execute(sql, args)))


@bp.get("/sweeps/<int:sweep_id>")
def get_sweep(sweep_id):
    db = get_db()
    sweep = db.execute("SELECT * FROM sweeps WHERE id = ?", (sweep_id,)).fetchone()
    if sweep is None:
        abort(404, description="sweep not found")
    points = db.execute(
        "SELECT idx, freq_hz, adc_raw, voltage FROM sweep_points "
        "WHERE sweep_id = ? ORDER BY idx", (sweep_id,))
    return jsonify(sweep=dict(sweep), points=_rows(points))


@bp.get("/measurements")
def list_measurements():
    limit = _int_arg("limit", 100, 1, MAX_LIMIT)
    clauses, args = [], []
    if request.args.get("from"):
        clauses.append("timestamp >= ?")
        args.append(request.args["from"])
    if request.args.get("to"):
        clauses.append("timestamp <= ?")
        args.append(request.args["to"])
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = f"SELECT {MEAS_COLS} FROM measurements{where} ORDER BY timestamp LIMIT ?"
    return jsonify(measurements=_rows(get_db().execute(sql, args + [limit])))


@bp.get("/measurements/latest")
def latest_measurement():
    row = get_db().execute(
        f"SELECT {MEAS_COLS} FROM measurements ORDER BY timestamp DESC LIMIT 1"
    ).fetchone()
    if row is None:
        abort(404, description="no measurements yet")
    return jsonify(dict(row))
