# API contract (v1)

Base URL: `http://<pi-ip>:5000/api/v1`. All responses are JSON. Errors: `{"error": "<message>"}` with status 400/404.
The UI must use only these endpoints, never the database. Timestamps are ISO-8601 UTC (e.g. `2026-11-24T12:00:00.000Z`).

| Endpoint | Query params | Returns |
|---|---|---|
| `GET /health` | | `{status, db}` |
| `GET /sweeps` | `limit` (1-1000, default 100), `offset`, `since` | `{sweeps: [{id, started_at, freq_start_hz, freq_stop_hz, freq_step_hz, n_points, power_dbm}]}` |
| `GET /sweeps/<id>` | | `{sweep: {...}, points: [{idx, freq_hz, adc_raw, voltage}]}` (404 if unknown) |
| `GET /measurements` | `from`, `to`, `limit` (1-1000, default 100) | `{measurements: [{timestamp, sweep_id, b_mt, f_minus_hz, f_plus_hz, contrast, linewidth_hz, fit_ok}]}` ordered by time |
| `GET /measurements/latest` | | the newest measurement (same fields), 404 if none |

`b_mt` and the frequency fields may be `null` when `fit_ok` is 0.

Example: `curl "http://<pi-ip>:5000/api/v1/measurements?from=2026-11-24T12:00:00Z&limit=10"`
