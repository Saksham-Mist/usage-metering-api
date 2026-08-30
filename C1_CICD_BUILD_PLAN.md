# C1 — End-to-End CI/CD Pipeline for a Containerised Application

Source: The Resume Project Vault 2026, Track C, Project C1.

## Rules for whoever (human or Claude Code) executes this file
- Do NOT skip ahead to the finished pipeline. Each step must be completed and verified working before the next starts.
- After each step, stop and ask the user to confirm they understand what just happened before continuing.
- At each numbered step, also update `SKILL.md` in the repo root (create it from the vault template if it doesn't exist) — the mapped section is noted per step.
- Do not silently "fix" a broken step by rewriting it into the next step's solution. The breakage is part of the deliverable.

## Stack
GitHub Actions, Docker, Docker Hub or GHCR, Kubernetes (kind/Minikube), Trivy, SonarQube (optional).

## Core features (build all of it; if you cut something, say so explicitly in the README)
- Multi-stage Dockerfile producing a small final image (record before/after size)
- Pipeline stages: lint, unit test, build, scan, push, deploy
- Container vulnerability scanning with Trivy that fails the build on critical CVEs
- Image tagging by commit SHA, never only `latest`
- Secrets handled through GitHub Secrets, never committed
- Kubernetes deployment with readiness and liveness probes
- Rolling update strategy with automatic rollback on failed health check
- Branch protection so `main` can only be merged through a passing pipeline

## Build order — follow exactly, in order

### Step 1
Take an existing application (or scaffold a small one — a simple Express or FastAPI API with 2-3 routes is enough). Write a **naive, single-stage Dockerfile**. Build it. Run `docker images` and record the image size. This number goes in SKILL.md section 6 as the "before" value.

### Step 2
Rewrite the Dockerfile as a **multi-stage build** with a slim or distroless base image. Record the new size. This delta is a resume number — SKILL.md section 6, "after" value.

### Step 3
Create the GitHub Actions workflow (`.github/workflows/ci.yml`) with **lint and test stages only**. Get it green before touching anything else. No build, no push, no deploy yet.

### Step 4
Add the **build-and-push stage**. Tag images with the commit SHA (e.g. `ghcr.io/<owner>/<repo>:${{ github.sha }}`), never `latest` alone. Push to GHCR (or Docker Hub).

### Step 5
Add **Trivy scanning** between build and push. Configure it to fail the pipeline on critical CVEs. Then deliberately introduce a vulnerable dependency (e.g. downgrade a package to a version with a known CVE) and confirm the pipeline actually blocks it. Remove the vulnerable dependency afterward. Record this incident in SKILL.md section 7 (things that broke).

### Step 6
Write the **Kubernetes manifests**: Deployment, Service, ConfigMap, Secret, plus readiness/liveness probes and resource requests/limits.

### Step 7
Add the **deploy stage** targeting a local `kind` cluster (or a free-tier managed cluster). Verify a rolling update happens with **no dropped requests** — run a `curl` loop against the service during the deploy and confirm zero failures.

### Step 8
**Break the health check on purpose** (e.g. point the readiness probe at a route that returns 500) and confirm the automatic rollback triggers. Screenshot the rollback in action. Write a runbook in the README describing exactly what happens when a deploy fails. Record this in SKILL.md section 7.

### Final
Enable branch protection on `main` requiring the CI workflow to pass before merge. Fill SKILL.md sections 4, 6, 7, 8, 9, 10 honestly, then write the resume bullet (section format: strong verb + what you built + [tech in brackets] + the hard technical thing you handled + a measured result).

## Skill file entries (SKILL.md section 5 — check these off with real evidence, not assumptions)
- [ ] CI/CD pipeline design and stage ordering
- [ ] Docker multi-stage builds and image optimisation
- [ ] Supply-chain security scanning
- [ ] Kubernetes deployments, probes and rolling updates
- [ ] Secrets management in pipelines
- [ ] Rollback and failure-recovery procedures

## You must be able to answer these before this goes on your resume
1. Why is tagging images `latest` dangerous in a deployment pipeline?
2. What is the difference between a readiness probe and a liveness probe, and what breaks if you swap them?
3. A deploy goes out and error rates spike. Walk me through your rollback, step by step.

## Reference resources (credit in SKILL.md section 12 if used)
- DevOps Exercises — github.com/bregman-arie/devops-exercises
- DevOps Resources — github.com/bregman-arie/devops-resources
- Developer Roadmap DevOps track — roadmap.sh/devops

## Model resume bullet (adapt numbers to what you actually measured — never inflate)
"Built a GitHub Actions CI/CD pipeline with lint, test, Trivy vulnerability scanning, multi-stage Docker builds and automated Kubernetes deployment; reduced image size from X to Y and implemented probe-based automatic rollback verified under a live traffic loop."
