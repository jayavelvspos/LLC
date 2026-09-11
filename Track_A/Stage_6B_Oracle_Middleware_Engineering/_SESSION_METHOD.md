# How to run every session (the loop) — Stage 6B

Use this same 8-step loop for **every** session in **Stage 6B — Oracle DB &
Python Middleware Engineering** (and every other stage). It fits in ~45
minutes *when no Track_B detour is needed*. Keep a timer — the boxes exist to
stop you rabbit-holing on step 2 and skipping steps 5–8, which is where the
learning actually happens.

| # | Step | Min | Mode | Produces |
|---|------|-----|------|----------|
| 0 | Recall last session | 3 | active | spoken/written answers to the previous session's Quick test |
| 1 | Orient | 2 | — | you can state this session's goal + its "Done when" list |
| 2 | Learn the concept | 8 | passive→active | margin notes in `notes.md` |
| 3 | Locate the Track_B footing | 2* | active | a decision: no link / revisit later / switch now |
| 4 | Study the worked example | 7 | active | a correct output *prediction*, then the real run |
| 5 | Practise: modify, break, build | 12 | active | the session's deliverable + 2–3 deliberate experiments |
| 6 | Connect to real systems | 4 | active | 2–3 sentences in `notes.md` in your own words |
| 7 | Retrieval check | 5 | active | written answers to this session's Quick test, from memory |
| 8 | Close | 2 | active | ticked checklist + a "surprises / open questions / Track_B?" note |

Total: 45 min. *Step 3 is 2 min for the check; a Track_B switch is a separate
20–30 min timebox and the session resumes after. This stage has no Track_B
footing, so step 3 should almost always be quick.

---

## How to do each step well

### 0 — Recall last session
Skip only for Session 1. Otherwise answer the **previous** session's Quick test
from memory, then check yourself. Missed one? Copy it into `notes.md` under
"revisit".

### 1 — Orient
Read this session's **Objective**, its **What you'll learn** bullet list, and
**Done when**. Don't start until you can say in one sentence what "finished"
looks like.

### 2 — Learn the concept
Read the **Concepts** section, then **one** primary resource. One. The session
file is the source of truth; the resource is support.

### 3 — Locate the Track_B footing
Read the session's **Track_B link** section. This stage is pure applied
engineering — expect "no link" most of the time and move straight to step 4.

### 4 — Study the worked example
Write your predicted output **first**, then run it and diff. The gap is the
signal.

### 5 — Practise: modify, break, build
Build the named deliverable (type it), then run 2–3 deliberate experiments —
change one thing, predict, run, confirm. In this stage, "break it" should
include at least one deliberate failure case (bad credentials, malformed
input, a slow/unreachable dependency) — that's the point of the hardening
sessions.

### 6 — Connect to real systems
2–3 sentences in `notes.md`: where does this show up in a production AI system,
in your own words?

### 7 — Retrieval check
Close everything. Answer the **Quick test** from memory in writing. Grade
yourself. Wrong/blank → `notes.md` "revisit".

### 8 — Close
Tick **Done when**. Add three lines to `notes.md`: Surprised me / Still unclear /
Needs a Track_B deep-dive (which topic).

---

## Standing rules

- **Timebox hard.** Overrunning step 2 is the classic failure.
- **Active > passive.** Steps 4, 5, 7 are non-negotiable.
- **`notes.md` is the deliverable that outlasts the code.**
- **One resource per session.**

---

## Track_B footing for this stage

**No Track_B footing.** This stage is pure applied engineering — Oracle SQL,
FastAPI, auth/validation/retries/caching/logging. If a session ever surfaces a
math question (e.g. cache hit-rate tuning, query cost estimation), note it as
a light, non-blocking pull to `Track_B/Math_stat`, but don't expect to switch
out of this stage.
