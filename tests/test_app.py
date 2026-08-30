import pytest
from fastapi.testclient import TestClient

import app.main as main_module


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main_module, "DB_PATH", tmp_path / "usage.db")
    return TestClient(main_module.app)


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_ready(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ready"}


def test_ingest_and_aggregate(client):
    resp = client.post(
        "/events",
        json={"api_key": "abc123", "event_type": "api_call", "quantity": 5},
    )
    assert resp.status_code == 201

    resp = client.post(
        "/events",
        json={"api_key": "abc123", "event_type": "api_call", "quantity": 3},
    )
    assert resp.status_code == 201

    resp = client.get("/usage/abc123")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_events"] == 2
    assert body["total_quantity"] == 8
    assert body["breakdown"][0]["event_type"] == "api_call"


def test_usage_not_found(client):
    resp = client.get("/usage/does-not-exist")
    assert resp.status_code == 404
