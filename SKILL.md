---
project: Usage Metering API — CI/CD Pipeline
track: devops
level: <beginner | intermediate | advanced>
started: 2026-08-30
shipped: <YYYY-MM-DD>
repo: <github url>
live: <deployed url or demo video url>
---

# 1. What this project is
<Two sentences. Explain it to a non-technical friend, then to an engineer.>

# 2. Problem it solves
<Why would anyone run this? If the honest answer is "it was a tutorial", change the project until there is a real answer.>

# 3. Architecture
<Paste an ASCII or image diagram. Every box must be something you can explain.>

Components:
- <component> -> <responsibility> -> <why this technology and not the alternative>

# 4. Key decisions and trade-offs
| Decision | Options I considered | What I chose | Why | What I gave up |
|---|---|---|---|---|
|  |  |  |  |  |

# 5. Skills demonstrated
- [ ] CI/CD pipeline design and stage ordering
      evidence:
- [x] Docker multi-stage builds and image optimisation
      evidence: [Dockerfile](Dockerfile) — builder stage installs deps via `pip install --user`, runtime stage is `python:3.12-slim` with only `/root/.local` and `app/` copied in. Cut image size from 1.69 GB to 231 MB.
- [ ] Supply-chain security scanning
      evidence:
- [ ] Kubernetes deployments, probes and rolling updates
      evidence:
- [ ] Secrets management in pipelines
      evidence:
- [ ] Rollback and failure-recovery procedures
      evidence:

# 6. Numbers I measured
| Metric | Before | After | How I measured it |
|---|---|---|---|
| Docker image size | 1.69 GB (`python:3.12` single-stage) | 231 MB (`python:3.12-slim` multi-stage) — an 86% reduction | Step 1: `docker build -t usage-metering:naive -f Dockerfile .`. Step 2: rewrote Dockerfile as a builder + runtime multi-stage build, `docker build -t usage-metering:multistage -f Dockerfile .`. Compared with `docker images \| Select-String usage-metering`. |

# 7. Things that broke and how I fixed them
<Filled in as real incidents happen — Step 5 (Trivy blocking a deliberately introduced CVE) and Step 8 (deliberate health-check break triggering rollback) will land here.>

1. Symptom: <what I saw>
   Cause: <what it actually was>
   Fix: <what I changed>
   Lesson: <what I now do by default>

# 8. What I would do differently at 100x scale
<Three bullets. This is the question senior interviewers always ask.>

# 9. Interview answers I have rehearsed
Q: Why is tagging images `latest` dangerous in a deployment pipeline?
A:

Q: What is the difference between a readiness probe and a liveness probe, and what breaks if you swap them?
A:

Q: A deploy goes out and error rates spike. Walk me through your rollback, step by step.
A:

# 10. Honest limitations
<What this project does NOT do. Saying this out loud in an interview builds more trust than pretending it is production-grade.>

# 11. How to run it
```bash
git clone <repo> && cd <repo>
cp .env.example .env      # fill in the values listed below
docker compose up --build # open http://localhost:3000
```
Required environment variables: <list them>

# 12. Credits
<Any tutorial, repository or article you learned from. Always credit. Copying is fine; uncredited copying is not.>
