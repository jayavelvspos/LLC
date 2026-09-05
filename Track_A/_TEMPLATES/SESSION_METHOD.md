# How to run every session (the loop) — TEMPLATE

> **Using this template:** copy this file into a stage folder as
> `_SESSION_METHOD.md`, then fill the two spots marked **«FILL»** below (the
> stage name, and the stage's Track_B footing). Everything else is
> stage-agnostic and should stay as-is so the method is identical across stages.

Use this same 8-step loop for **every** session in **«FILL: stage name»** (and
every other stage). It fits in ~45 minutes *when no Track_B detour is needed* —
a detour (step 3) adds its own timeboxed block. Keep a timer — the boxes exist
to stop you rabbit-holing on step 2 and skipping steps 5–8, which is where the
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

Total: 45 min. *Step 3 is 2 min for the check; if you switch into Track_B, that
detour is a separate timebox (20–30 min) and the Track_A session resumes after.

---

## How to do each step well

### 0 — Recall last session
Skip only for the **first session of the stage**. Otherwise, before opening
anything, answer the **previous** session's Quick test out loud or on paper,
then check yourself. Missed one? Copy it into `notes.md` under "revisit" — you
see it again next session. This 3-minute habit outperforms any single new
concept.

### 1 — Orient
Read this session's **Objective** and its **Done when** checklist. Do not start
until you can say, in one sentence, what "finished" looks like.

### 2 — Learn the concept
Read the session's **Concepts** section, then **one** primary resource from its
**Learning resources** list. One. If a video runs long or drifts, close it — the
session file is the source of truth, the resource is support. Put anything
non-obvious straight into `notes.md`.

### 3 — Locate the Track_B footing
Ask: **does this session's concept rest on a Track_B fundamental?** Read the
session's **Track_B link** section, then pick one:

- **No link** — write "no Track_B link" in `notes.md` and go to step 4.
- **Link exists, but the session still makes sense** — note it in `notes.md` as
  *"revisit in Track_B: <topic>"* and continue. Don't switch on a whim; Track_A
  leads (`../CLAUDE.md`).
- **The session genuinely stops making sense** without the fundamental — switch
  into that `Track_B/Math_stat/...` folder now. Learn only the basics this
  session needs (not the whole topic), timeboxed to 20–30 min, then return to
  step 4. If 30 min isn't enough, that's a real signal: finish the Track_B topic
  properly before resuming this Track_A session.

This *is* the just-in-time mechanism from `../CLAUDE.md` — pull Track_B in when
building here needs it, not on a schedule. The step is also **re-enterable**: if
confusion hits during step 4 or 5, come back here and make the same call.

### 4 — Study the worked example
Open the session's **Worked example**. Before running it, **write down what you
expect the output to be**. Then run it and diff your prediction against reality.
The gap between "what I thought" and "what happened" is the highest-value signal
in the whole loop — note it.

### 5 — Practise: modify, break, build
Two parts:
- **Build the deliverable** for this session (the artefact named in the session
  and in the stage `README.md`). Type it, don't paste — muscle memory matters.
- **Run 2–3 deliberate experiments** on it. Each session suggests specific ones.
  Change one thing, predict the effect, run, confirm. Breaking it on purpose
  teaches the failure modes you'll hit for real later.

### 6 — Connect to real systems
In `notes.md`, write 2–3 sentences answering: **"Where does this show up in a
production AI system?"** The session files give you the framing; this step is
about saying it in *your own words*.

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
     `../CLAUDE.md`, a concept that "doesn't make sense" is the trigger to pull
     the matching `Track_B` topic in *now*.

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

## «FILL» — Track_B footing for this stage

Fill this in when you copy the template into a stage. List the `Track_B/Math_stat`
topics this stage's work leans on, so step 3 has something concrete to check
against. Example shape:

| This stage's concept | Track_B topic | Blocking? |
|---|---|---|
| e.g. retrieval quality / similarity | `01_linear_algebra` (cosine similarity, vector norms) | can block — switch if retrieval makes no sense |
| e.g. routing between sub-agents | `05_decision_and_orchestration_math` (Markov chains, expected value) | usually non-blocking — note and revisit |

If the stage has **no** Track_B footing, say so explicitly here and in each
session's **Track_B link** section — "no link, move on" is a valid, common
outcome (all of Stage 0 is like this).

---

## Why these 8 steps (design rationale)

The loop is a standard learn→model→practice→transfer→recall cycle with three
additions specific to this workspace:

- **Step 0 (spaced recall)** — re-testing last session is what moves knowledge
  to long-term memory; a one-shot Quick test at the end isn't enough.
- **Step 3 (Track_B footing)** — makes the just-in-time Track_A/Track_B switch
  from `../CLAUDE.md` an explicit decision instead of a vague intention.
- **Step 5 (modify/break, not just run)** and **step 4 (predict first)** — force
  active engagement; copying and running an example teaches very little.
- **Step 8 (close with a Track_B flag)** — feeds the every-2-weeks review.
