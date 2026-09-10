# Session 3 — FastAPI Middleware Architecture (~45 min)

**Objective:** build a FastAPI service with a real routing endpoint that
pulls a ticket from Oracle, then decides — deterministic rule, trained
model, or LLM call — how to classify it, using the hybrid pattern from
Stage 1B as an actual live HTTP service.

**Prerequisites:** Sessions 1-2 complete (`db.py`, `query_perf.py`). Stage
1B's `fast_path_rules.py`. `pip install fastapi uvicorn`.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 2's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | FastAPI basics: path operations, Pydantic models, dependency injection |
| 10–35 | Build `code/middleware_app.py` |
| 35–45 | Run it, call it, notes |

---

## Concepts  <!-- step 2 -->

- **Path operations.** `@app.get("/tickets/{id}")` maps an HTTP
  method + URL pattern to a Python function. Path parameters (`{id}`) are
  type-annotated and validated automatically — `id: int` rejects
  `/tickets/abc` before your function body even runs.
- **Pydantic response/request models.** Define a `class TicketOut(BaseModel):
  id: int; subject: str; category: str` and return it (or a list of them) —
  FastAPI serializes it to JSON and, critically, documents the exact
  response shape (visible at `/docs` automatically). This is the boundary
  where Oracle's raw row dicts (Session 1) become a typed API contract.
- **Dependency injection (`Depends`).** A function like `get_db()` that
  yields a connection can be declared once and requested by any route via
  `db=Depends(get_db)` — FastAPI calls it per-request and handles
  setup/teardown (open a connection, close it after the response). This
  keeps connection management out of every route body.
- **The routing decision, as a real endpoint.** `POST /tickets/{id}/classify`
  implements the exact four-stage hybrid pattern from Stage 1B, now serving
  real traffic:
  1. **Validate** — the path parameter is already validated by FastAPI;
     confirm the ticket exists (404 if not).
  2. **Short-circuit** — run Stage 1B's scorer on the ticket body. Above
     threshold, return immediately, no model involved.
  3. **Model** — below threshold, call a Stage 4B model (the scikit-learn
     baseline or the LoRA classifier) for a confident, cheap classification.
  4. **LLM fallback** — if even that model is unsure (or you're using a
     confidence threshold there too), fall through to an LLM call as the
     last resort.
- **Sync vs. async route handlers.** `python-oracledb`'s standard driver
  calls are synchronous (blocking). A `def` route (not `async def`) lets
  FastAPI run it in a thread pool automatically, so one slow DB call
  doesn't block the whole server. Use `async def` only once every call
  inside it is genuinely async (an async DB driver, `httpx.AsyncClient`,
  etc.) — mixing sync blocking calls inside `async def` blocks everything.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- FastAPI docs — *Tutorial: First Steps*, *Path Parameters*, *Dependencies*:
  <https://fastapi.tiangolo.com/tutorial/> (the first four or five pages).

**Video (pick one, ~15–20 min):**
- Search *"FastAPI tutorial for beginners"* — any recent one covering path
  operations, Pydantic models, and `Depends`.

---

## Track_B link (step 3)

**None.** FastAPI architecture is applied engineering. Note "no Track_B
link" and continue.

---

## Worked example — the classify endpoint  <!-- step 4 -->

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from db import get_connection, get_ticket_by_id
from fast_path_rules import score_refund, THRESHOLD

app = FastAPI()

def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

class ClassifyResult(BaseModel):
    ticket_id: int
    category: str
    method: str   # "deterministic" | "model" | "llm"

def classify_with_model(text: str) -> tuple[str, float]:
    # stand-in for Stage 4B's baseline/LoRA classifier
    return "other", 0.4

def classify_with_llm(text: str) -> str:
    # stand-in for a Stage 0/1 client.messages.create call
    return "other"

@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int, db=Depends(get_db)):
    ticket = get_ticket_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="ticket not found")
    return ticket

@app.post("/tickets/{ticket_id}/classify", response_model=ClassifyResult)
def classify_ticket(ticket_id: int, db=Depends(get_db)):
    ticket = get_ticket_by_id(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="ticket not found")

    score = score_refund(ticket["body"])
    if score >= THRESHOLD:
        return ClassifyResult(ticket_id=ticket_id, category="billing", method="deterministic")

    category, confidence = classify_with_model(ticket["body"])
    if confidence >= 0.7:
        return ClassifyResult(ticket_id=ticket_id, category=category, method="model")

    category = classify_with_llm(ticket["body"])
    return ClassifyResult(ticket_id=ticket_id, category=category, method="llm")
```

Run it: `uvicorn middleware_app:app --reload`, then `GET
http://localhost:8000/docs` for the interactive API explorer FastAPI
generates for free from your type hints.

**Expected output** (calling `POST /tickets/1/classify` on a refund-worded
ticket):

```json
{"ticket_id": 1, "category": "billing", "method": "deterministic"}
```

Read it: the response's `method` field tells you *which* stage of the
pipeline actually answered — exactly the visibility you need to reason about
cost/latency once this is serving real traffic.

---

## Build: `code/middleware_app.py`  <!-- step 5 -->

Build the app above wired to your real `db.py`. Add a `GET /tickets` list
endpoint using Session 2's pagination function (query params `offset`,
`limit`). Replace the `classify_with_model` stub with a real call into your
Stage 4B code (the scikit-learn baseline is simplest to wire in first).

Experiments:
1. **Hit `/docs`.** Confirm the interactive schema shows your `ClassifyResult`
   model's exact fields and types, generated with zero extra code.
2. **Force each path.** Craft one ticket that hits `deterministic`, one that
   falls to `model`, and one that falls all the way to `llm`. Confirm the
   `method` field reflects each correctly.
3. **Break type validation.** Call `/tickets/abc/classify` (non-integer) and
   read FastAPI's automatic 422 error — no code of yours ran.

---

## Quick test (step 7 — answer from memory, then check)

1. What does `Depends(get_db)` give you that manually opening a connection
   in every route doesn't?
2. What does a Pydantic response model give you beyond "the JSON that gets
   returned"?
3. Why should a route calling a blocking DB driver be `def`, not
   `async def`?
4. In the classify endpoint, what determines whether a request reaches the
   LLM at all?
5. What happened when you called `/tickets/abc/classify` and why didn't
   your function body run?

<details><summary>Answers</summary>

1. Automatic per-request setup/teardown (open then close the connection),
   defined once and reused by any route that declares the dependency,
   instead of duplicated connection-handling code in every route.
2. A documented, validated response contract — FastAPI serializes to it and
   auto-generates the `/docs` schema from its field types.
3. `python-oracledb`'s standard calls block; FastAPI runs a sync `def` route
   in a thread pool so one slow call doesn't block the event loop. Putting
   a blocking call inside `async def` blocks the whole server instead.
4. Neither the deterministic scorer nor the Stage 4B model was confident
   enough (both fell below their thresholds) — the LLM is the last resort,
   not the default.
5. A 422 validation error — FastAPI validated the path parameter against
   its `int` type annotation and rejected the request before your function
   ever ran.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `middleware_app.py` runs and serves `GET /tickets`, `GET
      /tickets/{id}`, and `POST /tickets/{id}/classify`.
- [ ] You've forced a request down each of the three classification paths
      and confirmed the response correctly reports which one ran.
- [ ] You've seen FastAPI's auto-generated `/docs` reflect your Pydantic
      models.
- [ ] You can explain why the DB dependency and blocking calls are handled
      the way they are.

## Pitfalls

- **Putting a blocking DB/model call inside `async def` "because async
  sounds faster."** It's slower here — it blocks the entire event loop
  instead of running in a thread pool.
- **Returning raw dicts instead of a response model.** Works, but throws
  away validation and the auto-generated API contract that `/docs` and API
  consumers rely on.
- **Forgetting to close the DB connection.** The `finally: conn.close()` in
  `get_db()` matters — without it, connections leak under load.

## Carries to next session

This endpoint works but trusts every caller completely — no auth, no rate
limiting, no timeout on the fallback paths, no caching, no structured logs.
Session 4 hardens exactly this service.
