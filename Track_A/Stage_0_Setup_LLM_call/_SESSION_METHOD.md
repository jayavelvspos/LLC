# How to run every session (the loop)

Use this same 8-step loop for **every** session in Stage 0 (and reuse it in
later stages). It fits in ~45 minutes *when no Track_B detour is needed* — a
detour (step 3) adds its own timeboxed block. Keep a timer — the point of the
boxes is to stop you rabbit-holing on step 2 and skipping steps 5–8, which is
where the learning actually happens.

| # | Step | Min | Mode | Produces |
|---|------|-----|------|----------|
| 0 | Recall last session | 3 | active | spoken/written answers to the previous session's Quick test |
| 1 | Orient | 2 | — | you can state this session's goal + its "Done when" list |
| 2 | Learn the concept | 8 | passive→active | margin notes in `notes.md` |
| 3 | Locate the Track_B footing | 2* | active | a decision: no link / revisit later / switch now |
| 4 | Study the worked example | 7 | active | a correct output *prediction*, then the real run |
| 5 | Practise: modify, break, build | 12 | active | the session's deliverable script + 2–3 deliberate experiments |
| 6 | Connect to real systems | 4 | active | 2–3 sentences in `notes.md` in your own words |
| 7 | Retrieval check | 5 | active | written answers to this session's Quick test, from memory |
| 8 | Close | 2 | active | ticked checklist + a "surprises / open questions / Track_B?" note |

Total: 45 min. *Step 3 is 2 min for the check; if you switch into Track_B, that
detour is a separate timebox (20–30 min) and the Track_A session resumes after.

---

## How to do each step well

### 0 — Recall last session (skip for Session 1)
Before opening anything, answer the **previous** session's Quick test out loud or
on paper. Check yourself against that file. Missed one? Copy it into
`notes.md` under "revisit" — you'll see it again next session. This 3-minute
habit is worth more than any single new concept.

### 1 — Orient
Read this session's **Objective** and its **Done when** checklist. Do not start
until you can say, in one sentence, what "finished" looks like.

### 2 — Learn the concept
Read the session's **Concepts** section, then **one** primary resource from its
**Learning resources** list (usually one Anthropic course notebook or one docs
page). One. If a video runs long or drifts off-topic, close it — the session
file is the source of truth, the resource is support. Jot anything non-obvious
straight into `notes.md`.

### 3 — Locate the Track_B footing
Ask: **does this session's concept rest on a Track_B fundamental?** Read the
session's **Track_B link** section, then pick one:

- **No link** (most of Stage 0) — write "no Track_B link" in `notes.md` and go
  to step 4.
- **Link exists, but the session still makes sense** — note it in `notes.md` as
  *"revisit in Track_B: <topic>"* and continue. Don't switch on a whim; Track_A
  leads (`../CLAUDE.md`).
- **The session genuinely stops making sense** without the fundamental — switch
  into that `Track_B/Math_stat/...` folder now. Learn only the basics this
  session needs (not the whole topic), timeboxed to 20–30 min, then come back to
  step 4 here. If 30 min isn't enough, that's a real signal: finish the Track_B
  topic properly before resuming this Track_A session.

This *is* the just-in-time mechanism from `../CLAUDE.md` — pull Track_B in when
building here needs it, not on a schedule. The step is also **re-enterable**:
if confusion hits during step 4 or 5, come back here and make the same call.

### 4 — Study the worked example
Open the session's **Worked example**. Before running it, **write down what you
expect the output to be**. Then run it and diff your prediction against reality.
The gap between "what I thought" and "what happened" is the highest-value
signal in the whole loop — note it.

### 5 — Practise: modify, break, build
Two parts:
- **Build the deliverable** for this session (the script named in the session
  and in `README.md`). Type it, don't paste — muscle memory matters here.
- **Run 2–3 deliberate experiments** on it. Each session suggests specific ones
  ("set `max_tokens=4`", "`temperature` 0 vs 1", "use a bad key"). Change one
  thing, predict the effect, run, confirm. Breaking it on purpose teaches the
  failure modes you'll hit for real later.

### 6 — Connect to real systems
In `notes.md`, write 2–3 sentences answering: **"Where does this show up in a
production agent?"** The session files give you the framing; this step is about
saying it in *your own words*. Example for Session 2: *"`stop_reason` is how an
agent loop knows whether to stop or keep going — `tool_use` means run a tool and
loop again, `end_turn` means done."*

### 7 — Retrieval check
Close `notes.md` and every other file. Answer this session's **Quick test** from
memory, in writing. Then reopen and grade yourself. Anything wrong or blank goes
into `notes.md` under "revisit" for step 0 of the next session.

### 8 — Close
- Tick the session's **Done when** checklist. If something isn't ticked, the
  session isn't done — finish it or note exactly what's blocking.
- Add three lines to `notes.md`:
  1. **Surprised me:** …
  2. **Still unclear / open question:** …
  3. **Needs a Track_B deep-dive?** yes/no — and which topic. Per
     `Track_A/CLAUDE.md`, a concept that "doesn't make sense" is the trigger to
     pull the matching `Track_B/Math_stat` topic in *now*, not later.

---

## Standing rules

- **Timebox hard.** Overrunning step 2 is the classic failure. If you're deep in
  a resource at minute 15, stop and move to the example.
- **Active > passive.** Predicting, typing, breaking, and recalling beat reading
  and watching every time. Steps 4, 5, and 7 are non-negotiable.
- **`notes.md` is the deliverable that outlasts the code.** It feeds the
  every-2-weeks review and the Track_B just-in-time trigger.
- **One resource per session.** Bookmark the rest; don't binge.

---

## Mapping to the original 5-point idea

| Your point | Where it lives now |
|---|---|
| 1. Learn the concepts | Step 2 |
| 2. Understand further with example | Step 4 (with a prediction, not just a read) |
| 3. Practise one example | Step 5 (modify/break/build — not just run) |
| 4. Relate to real-time examples | Step 6 (write it in your own words) |
| 5. Quick test Q&A | Step 7 — **plus** Step 0 re-tests it next session |
| *(added)* Orient before starting | Step 1 |
| *(added)* Relate to Track_B fundamentals; switch if needed, then return | Step 3 (re-enterable) |
| *(added)* Close: log surprises + Track_B trigger | Step 8 |
