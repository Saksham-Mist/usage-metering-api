# Usage Metering API — CI/CD Pipeline

A FastAPI service that ingests per-API-key usage events and reports aggregated usage, built as an end-to-end CI/CD exercise: multi-stage Docker build, GitHub Actions pipeline (lint, test, build, Trivy scan, push, deploy), and a Kubernetes deployment with health probes, rolling updates, and automatic rollback.

## Running locally

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Or via Docker:
```bash
docker build -t usage-metering .
docker run -p 8000:8000 usage-metering
```

## Endpoints

- `POST /events` — ingest a usage event (`api_key`, `event_type`, `quantity`). Requires an `X-API-Secret` header matching `API_SECRET_KEY` when that env var is set.
- `GET /usage/{api_key}` — aggregated usage for a key.
- `GET /health` — liveness check.
- `GET /ready` — readiness check (verifies the database is reachable).

## CI/CD pipeline

On every push to `main`, [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs four jobs in order:

1. **lint-and-test** — `ruff check .`, then `pytest`.
2. **build-and-push** — builds the multi-stage Docker image, scans it with Trivy (fails on any CRITICAL CVE), and only then pushes to GHCR, tagged with the commit SHA.
3. **deploy** — spins up an ephemeral `kind` cluster inside the runner, applies the Kubernetes manifests, and verifies a live rolling update drops zero requests by curling `/health` continuously through a forced `kubectl rollout restart`.

Each stage gates the next — a lint failure never reaches build, a critical CVE never reaches push, and a failed deploy never gets reported as green.

## Runbook: what happens when a deploy fails

The Deployment's rolling-update strategy is `maxUnavailable: 0, maxSurge: 1` — Kubernetes will only add new pods, never remove an old one, until a replacement is confirmed healthy via the readiness probe (`/ready`). Concretely, when a bad version is deployed:

1. New pods are created alongside the existing healthy ones.
2. If a new pod's readiness probe never succeeds (bad code, broken dependency, misconfigured probe), that pod is never marked `Ready`.
3. Because `maxUnavailable: 0`, Kubernetes will **not** terminate any old, healthy pod to make room — the old version keeps serving 100% of traffic through the Service the entire time. There is no user-facing downtime from the failed rollout itself.
4. The pipeline's deploy job runs `kubectl rollout status --timeout=120s`. If the rollout hasn't completed within that window, the job treats it as failed and automatically runs `kubectl rollout undo`, which reverts the Deployment to the last successful revision (deleting the stuck/broken pods).
5. The job exits non-zero even after a successful rollback — a rollback is a recovery, not a success; the bad commit still needs to be fixed before it can ship again.

This is exercised directly and repeatably by [`.github/workflows/rollback-drill.yml`](.github/workflows/rollback-drill.yml) (manually triggered via `workflow_dispatch`), which deploys a known-good baseline, then deliberately deploys a version with the readiness probe pointed at `/broken` (an endpoint that always returns 500), confirms the old pods keep serving traffic throughout, confirms the rollout stalls, and confirms the automatic rollback restores a healthy deployment.

Verified live in [Run #1](../../actions): while the broken pod sat stuck at `0/1` ready, both old pods stayed `Running` and `GET /health` returned `HTTP 200` the whole time; `kubectl rollout status --timeout=60s` timed out as expected, `kubectl rollout undo` restored the last healthy revision, and `/health` returned `HTTP 200` again afterward.
