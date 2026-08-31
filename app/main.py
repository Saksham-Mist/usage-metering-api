import os
import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

DB_PATH = Path(__file__).parent / "data" / "usage.db"

app = FastAPI(title="Usage Metering API")


class EventIn(BaseModel):
    api_key: str
    event_type: str
    quantity: float


def check_ingest_secret(x_api_secret: str | None):
    expected = os.environ.get("API_SECRET_KEY")
    if expected and x_api_secret != expected:
        raise HTTPException(status_code=401, detail="invalid or missing X-API-Secret header")


def get_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT NOT NULL,
            event_type TEXT NOT NULL,
            quantity REAL NOT NULL,
            created_at REAL NOT NULL
        )
        """
    )
    return conn


@app.post("/events", status_code=201)
def create_event(event: EventIn, x_api_secret: str | None = Header(default=None)):
    check_ingest_secret(x_api_secret)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO events (api_key, event_type, quantity, created_at) VALUES (?, ?, ?, ?)",
            (event.api_key, event.event_type, event.quantity, time.time()),
        )
        conn.commit()
    finally:
        conn.close()
    return {"status": "recorded"}


@app.get("/usage/{api_key}")
def get_usage(api_key: str):
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT event_type, COUNT(*), SUM(quantity) FROM events WHERE api_key = ? GROUP BY event_type",
            (api_key,),
        ).fetchall()
    finally:
        conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No usage found for this api_key")

    breakdown = [
        {"event_type": event_type, "count": count, "total_quantity": total}
        for event_type, count, total in rows
    ]
    return {
        "api_key": api_key,
        "total_events": sum(b["count"] for b in breakdown),
        "total_quantity": sum(b["total_quantity"] for b in breakdown),
        "breakdown": breakdown,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ready"}


@app.get("/broken")
def broken():
    """Always returns 500. Exists only so the rollback drill can point the readiness probe at a real failing route."""
    raise HTTPException(status_code=500, detail="intentionally broken for rollback drill")
