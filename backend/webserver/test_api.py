import pytest

from app import create_app


@pytest.fixture
def client():
    return create_app().test_client()


def test_health(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200 and r.json["status"] == "ok"


def test_sweeps_pagination(client):
    r = client.get("/api/v1/sweeps?limit=5&offset=2")
    assert [s["id"] for s in r.json["sweeps"]] == [3, 4, 5, 6, 7]


def test_sweep_detail(client):
    r = client.get("/api/v1/sweeps/1")
    assert len(r.json["points"]) == r.json["sweep"]["n_points"] == 141


def test_sweep_404_is_json(client):
    r = client.get("/api/v1/sweeps/99999")
    assert r.status_code == 404 and "error" in r.json


def test_measurements_range(client):
    r = client.get("/api/v1/measurements?from=2026-11-24T12:00:00.000Z&to=2026-11-24T12:00:04.000Z")
    assert len(r.json["measurements"]) == 3


def test_latest(client):
    r = client.get("/api/v1/measurements/latest")
    assert r.json["sweep_id"] == 300


def test_bad_limit(client):
    assert client.get("/api/v1/measurements?limit=abc").status_code == 400
    assert client.get("/api/v1/measurements?limit=0").status_code == 400
