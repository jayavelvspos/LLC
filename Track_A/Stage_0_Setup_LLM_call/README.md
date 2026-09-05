# Stage 0 — Setup & First LLM Call

**Stage goal:** environment ready, one raw API call working, and a script that
sends a prompt and prints a streamed response — with token, cost, and latency
awareness.

Split into five ~45-minute sessions. Do them in order; each builds on the last.
Total: ~3.75 hours.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [Environment & project scaffold](session_1_environment_scaffold.md) | venv + deps + `.env` layout, nothing calls the API yet |
| 2 | [API key & first authenticated call](session_2_api_key_first_call.md) | `hello_claude.py` prints a real response |
| 3 | [Messages API: roles & parameters](session_3_messages_api_roles_params.md) | `roles_demo.py` — scripted multi-turn conversation |
| 4 | [Streaming + the Stage 0 build](session_4_streaming_build.md) | `stream_prompt.py` — prompt in, streamed output |
| 5 | [Token counting, cost & latency](session_5_tokens_cost_latency.md) | `stream_prompt.py` also reports tokens, $, and timing |

## How to run a session

Every session follows the same 8-step, ~45-minute loop — defined once in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md):

0. Recall last session's Quick test → 1. Orient → 2. Learn the concept →
3. **Locate the Track_B footing** (no link / revisit later / switch into Track_B
now, then return) → 4. Study the worked example (predict, then run) →
5. Practise: modify / break / build the deliverable → 6. Connect to a real
system, in your own words → 7. Retrieval check (this session's Quick test, from
memory) → 8. Close: tick "Done when", log surprises + any Track_B trigger.

Each session file is laid out to feed that loop: **Concepts** (step 2),
**Learning resources** (one per session, step 2), **Track_B link** (step 3),
**Worked example** with expected output (step 4), **Build** + experiments
(step 5), **Quick test** (step 7), **Done when** (step 8).

Step 3 is a 2-minute checkpoint for most of Stage 0 (the sessions say "no
Track_B link"); it becomes a real decision point from Stage 4 on, where Track_A
work leans on `Track_B/Math_stat`.

## Conventions for this stage

- **Language:** Python 3.10+ (Track A is Python throughout).
- **SDK:** the official `anthropic` package. No framework yet — that starts in
  Stage 2 (LangGraph).
- **Models (as of 2026):**

  | Model | ID | Input $/1M | Output $/1M |
  |-------|----|-----------|-------------|
  | Claude Opus 5 | `claude-opus-5` | $5.00 | $25.00 |
  | Claude Sonnet 5 | `claude-sonnet-5` | $2.00 | $10.00 |
  | Claude Haiku 4.5 | `claude-haiku-4-5` | $1.00 | $5.00 |

  Use `claude-opus-5` as the default. For a stage full of throwaway practice
  calls, `claude-haiku-4-5` costs ~5x less and is fine for "does this run" —
  your call. Whatever you pick, know why.

## Learning resources

Each session file has its own **Learning resources** section (official docs +
one video/course pointer) and a **Worked example** with expected output. The
backbone for the whole stage:

- **Anthropic — *Anthropic API fundamentals* course** (free, notebooks):
  <https://github.com/anthropics/courses> → folder `anthropic_api_fundamentals`.
  This single course covers Sessions 1–4 almost one-to-one. Do it alongside
  these files.
- **Anthropic docs**: <https://docs.anthropic.com> (also at docs.claude.com).
- **Anthropic Cookbook** (runnable recipes):
  <https://github.com/anthropics/anthropic-cookbook>.

**About video / paid-course recommendations:** exact YouTube URLs and titles go
stale, so each session names a *channel + search query* rather than a fragile
link. If you own Udemy courses you want mapped to these sessions, don't share
your login — instead paste each course's curriculum (section/lecture list, which
Udemy shows publicly) or the course URL, and the specific lectures will be
slotted into the matching session.

## Working files produced in this stage

```
Stage_0_Setup_LLM_call/
  code/
    hello_claude.py        # session 2
    roles_demo.py          # session 3
    stream_prompt.py       # session 4, extended in session 5
    costs.py               # session 5 — cost/latency helpers
  .env                     # NOT committed
  .env.example             # committed
  requirements.txt
  notes.md                 # your own running notes / surprises
```

## Done with Stage 0 when

- [ ] A fresh `python -m venv` + `pip install -r requirements.txt` reproduces the env.
- [ ] `.env` holds the key; `.env` is git-ignored; `.env.example` is committed.
- [ ] `stream_prompt.py "some question"` streams an answer to the terminal.
- [ ] The same script prints input/output tokens, estimated USD cost, time to
      first token, and total wall time.
- [ ] You can explain, without notes: what `system` / `user` / `assistant` roles
      are, what `max_tokens` and `temperature` do, and why streaming matters.
