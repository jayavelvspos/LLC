# Session 5 — Wiring into MLOps/CI (~45 min)

**Objective:** containerize the middleware service, give it a real health
check, write a test that runs without hitting a live LLM, and wire it
through a CI pipeline (lint -> test -> build) — the same pipeline shape as
Stage 6, now covering this service too.

**What you'll learn:**
- Dockerizing a FastAPI service and `docker-compose` for app + DB together
- A health check that verifies real dependencies, not just process liveness
- Testing an API without hitting a live LLM (`TestClient` + `monkeypatch`)
- A lint -> test -> build CI pipeline, and why each stage gates the next
- Why deployed images should be versioned, not tagged `:latest`

**Prerequisites:** Sessions 1-4 complete. Docker Compose. `pip install
pytest`.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 4's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Dockerizing the service; health checks; secrets via env vars |
| 10–20 | Testing an API without hitting a live LLM (`TestClient` + a stub) |
| 20–35 | Build the `Dockerfile`, `docker-compose.yml`, and CI config |
| 35–45 | Run the pipeline end-to-end, notes |

---

## Concepts  <!-- step 2 -->

- **`Dockerfile` for a FastAPI service.** Base image with Python, copy
  `requirements.txt` and install first (so Docker's layer cache skips
  reinstalling deps when only your code changes), copy the app code, run
  `uvicorn` as the container's entrypoint.
- **`docker-compose.yml`** runs the app *and* an Oracle XE container
  together with one command — the same schema/data setup from Session 1,
  now fully reproducible for anyone (including CI) instead of a one-off
  local install.
- **Health check endpoint.** `GET /health` that actually checks its
  dependencies (can it reach Oracle?) and returns 200/503 accordingly —
  not just "the process is alive," which tells you nothing about whether it
  can serve real requests. Load balancers, container orchestrators, and CI
  smoke tests all rely on this being honest.
- **Secrets via environment variables**, never hard-coded or committed.
  `API_KEY`, `DB_PASSWORD` come from the environment (`os.environ`,
  `python-dotenv` locally, injected by CI/deployment infra in real
  environments) — the same discipline as Stage 0's `.env` handling, now at
  the service level.
- **Testing without a live model/LLM call.** A test suite that calls a real
  paid API on every run is slow, flaky, and costs money per CI run.
  FastAPI's `TestClient` lets you call your endpoints in-process; combine it
  with dependency overrides (`app.dependency_overrides[...]`) or simple
  monkeypatching to replace `classify_with_llm` with a fixed stub during
  tests, so you're testing your *routing logic*, not the LLM.
- **CI pipeline shape** (same idea as Stage 6, applied to this service):
  lint -> unit/integration tests -> build the Docker image -> (in a real
  deployment) push and deploy. Each stage gates the next — a lint failure or
  test failure should stop the build before it ever produces an image.
- **Versioning.** Tag the built image with something traceable (a git SHA,
  a semantic version) — never `:latest` for anything you actually deploy.
  If this service is serving a Stage 4B model, that model's version (from
  Stage 6's extended MLOps section — its registry entry) should be
  identifiable from the running service too, e.g. via a `/health` or
  `/version` field, so a production issue can be traced back to exactly
  which model and which code were running.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- FastAPI docs — *Deploy with Docker*:
  <https://fastapi.tiangolo.com/deployment/docker/>.
- FastAPI docs — *Testing*:
  <https://fastapi.tiangolo.com/tutorial/testing/> (`TestClient` and
  dependency overrides).

**Video (pick one, ~15 min):**
- Search *"Dockerize FastAPI app tutorial"*.

---

## Track_B link (step 3)

**None.** Pure applied engineering — containers, testing, CI. Note "no
Track_B link" and continue.

---

## Worked example — a testable health check  <!-- step 4 -->

```python
# in middleware_app.py
from fastapi import FastAPI
from fastapi.testclient import TestClient

@app.get("/health")
def health(db=Depends(get_db)):
    try:
        db.cursor().execute("SELECT 1 FROM dual")
        return {"status": "ok"}
    except Exception:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={"status": "unavailable"})
```

```python
# test_middleware.py
from fastapi.testclient import TestClient
from middleware_app import app, classify_with_llm

def fake_llm(text: str) -> str:
    return "other"

def test_classify_deterministic_path(monkeypatch):
    monkeypatch.setattr("middleware_app.classify_with_llm", fake_llm)
    client = TestClient(app)
    resp = client.post(
        "/tickets/1/classify", headers={"X-API-Key": "dev-secret-key"}
    )
    assert resp.status_code == 200
    assert resp.json()["method"] in {"deterministic", "model", "llm"}

def test_classify_requires_api_key():
    client = TestClient(app)
    resp = client.post("/tickets/1/classify")
    assert resp.status_code == 401
```

**Expected output** (`pytest -v`):

```
test_middleware.py::test_classify_deterministic_path PASSED
test_middleware.py::test_classify_requires_api_key PASSED
```

Read it: neither test made a real network call to an LLM or paid for a
token — `monkeypatch` replaced the LLM function with a fixed stub, so
what's actually under test is your routing/auth/validation logic.

---

## Build: `Dockerfile`, `docker-compose.yml`, CI config  <!-- step 5 -->

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "middleware_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
services:
  oracle:
    image: gvenzl/oracle-xe
    environment:
      ORACLE_PASSWORD: devpass
    ports: ["1521:1521"]
  app:
    build: .
    environment:
      DB_DSN: "oracle:1521/XEPDB1"
      API_KEY: "dev-secret-key"
    ports: ["8000:8000"]
    depends_on: ["oracle"]
```

Add a minimal CI config (GitHub Actions shown; adapt to whatever you use)
that lints, tests, then builds — each step gating the next:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r requirements.txt ruff pytest
      - run: ruff check .
      - run: pytest
      - run: docker build -t middleware:${{ github.sha }} .
```

Experiments:
1. **Run `docker compose up`** and confirm `GET /health` returns `ok` once
   Oracle is ready (it takes a little longer to start than the app —
   observe what happens if you hit `/health` too early).
2. **Break the health check on purpose.** Stop the Oracle container while
   the app keeps running, then hit `/health` again — confirm you get a
   `503`, not a hang or a crash.
3. **Make a lint or test failure block the build.** Introduce an obvious
   lint violation or a failing test and confirm the CI config's `docker
   build` step never runs.

---

## Quick test (step 7 — answer from memory, then check)

1. Why copy `requirements.txt` and install dependencies *before* copying
   the rest of the app code in a `Dockerfile`?
2. What should a real `/health` endpoint check, beyond "is the process
   running"?
3. Why use `monkeypatch`/dependency overrides in tests instead of calling
   the real LLM?
4. What's wrong with tagging every deployed image `:latest`?
5. In a CI pipeline of lint -> test -> build, what should happen if the
   test step fails?

<details><summary>Answers</summary>

1. Docker caches layers; if only your app code changes (not
   `requirements.txt`), the dependency-install layer is reused unchanged
   instead of re-running `pip install` every build.
2. Its actual dependencies — can it reach the database, any other required
   service — so the health check reflects whether it can really serve
   requests, not just that the process hasn't crashed.
3. Speed (no real network round trip), reliability (no flakiness from an
   external service), and cost (no real API charges) — tests should verify
   your code's logic, not a third party's availability.
4. You lose traceability — you can't tell which exact code/model version is
   running in a given environment, which makes debugging a production issue
   and rolling back much harder.
5. The pipeline should stop — the build step should never run, so a broken
   change never becomes a deployable image.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `docker compose up` runs the app and Oracle together, and `/health`
      correctly reports `ok`/`unavailable` based on real DB connectivity.
- [ ] `test_middleware.py` passes without making any real LLM call.
- [ ] A CI config runs lint, then test, then build, in that order, and a
      failure at any step blocks the next.
- [ ] You can explain why images should be versioned, not tagged `:latest`.

## Pitfalls

- **Testing against a real, paid LLM call in CI.** Slow, flaky, costs money
  on every push — stub it.
- **A health check that only returns `{"status": "ok"}` unconditionally.**
  Worse than no health check — it actively lies about the service's real
  ability to serve traffic.
- **Baking secrets into the Docker image or committing them in
  `docker-compose.yml`.** Use environment variables injected at runtime,
  same as Stage 0's `.env` discipline.

## Carries to next stage

Stage 6B is complete. Stage 7 (capstone) composes everything built across
Stages 0-6B into one deployed, measured system — this service is the
exposure layer that system would run behind.
