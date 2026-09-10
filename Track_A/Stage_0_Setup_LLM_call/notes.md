## Stage 0 notes

Running log — surprises, "revisit" items, and Track_B deep-dive flags. Feeds the
every-2-weeks review in `../CLAUDE.md`.

### revisit

- **(S1 quick test Q1)** A venv isolates **installed packages + their exact
  versions**; reproducibility = that **plus pinned `requirements.txt`**. (S2
  recall: still stated only the payoff "identical behavior", not the mechanism.)
- **(S2 quick test Q3)** `Anthropic()` reads the **`ANTHROPIC_API_KEY` environment
  variable**. Chain: `.env` → `load_dotenv()` puts it in the process env →
  client reads the env var. The `import` line is irrelevant to *where the key
  comes from*.
- **(S2 quick test Q4)** `resp.usage` holds **`input_tokens`** and
  **`output_tokens`** (+ cache counters). Session 5 = tokens × per-token price →
  dollar cost.
- **(S2 quick test Q5)** `max_tokens` is **required** (API rejects the request
  without it). If exceeded: output truncated mid-text, `stop_reason == "max_tokens"`.

- **(S3 quick test Q3)** `messages` ordering: first message must be `role:
  "user"`, roles **alternate** user/assistant — no two `user` turns back to back.
- **(S3 quick test Q4)** `temperature=0` ≈ deterministic/repeatable (saw "1
  distinct answer out of 2"); `temperature=1` varies ("2 distinct"). Separate
  fact: this SDK dropped `temperature` from `messages.create()` — pass via
  `extra_body={"temperature": t}`, and only models that still support sampling
  honor it (Haiku 4.5 does; Opus 5 / Sonnet 5 do not).
- **(S3 quick test Q5)** `stop_sequences`: generation halts at the **first
  occurrence** of the string; `stop_reason` becomes `"stop_sequence"`.
  `input_tokens` climbs each turn because every call resends the whole growing
  history.
- **Meta:** recall answers have been half-complete for 3 sessions — mechanism
  given, "what it does / why" skipped. Fix: before pasting, check both halves
  are answered.

**Resolved:** S1 Q2 (both halves given in S2 recall), S1 Q3 (wrong interpreter —
correct in S2 recall), S1 Q5 (`python --version` + 3.10+ — correct in S2 recall).

### per session

#### Session 1 — Environment & project scaffold (2026-09-06)

- **Done:** `.venv` (Python 3.11.9), `anthropic==1.4.0` + `python-dotenv==1.2.3`
  pinned, `.env` (blank) / `.env.example` / `.gitignore` created, `import
  anthropic` verified. All "Done when" boxes ticked.
- **Track_B link:** none — pure tooling.
- **Surprised me:** PowerShell 5.1's `>` redirection writes **UTF-16**, so
  `pip freeze > requirements.txt` produced a UTF-16 file. Use
  `pip freeze | Out-File -Encoding utf8 requirements.txt`. Also `python`/`python3`
  on this machine are Microsoft Store stubs — use `py` (or the activated venv).
- **Still unclear / open question:** none for this session.
- **Needs a Track_B deep-dive?** No.

#### Session 2 — API key & first authenticated call (2026-09-06)

- **Done:** `$5` API credit added; standard API key (Default workspace) in
  `.env` (loads: 108 chars, `sk-ant-api…`). Built `code/hello_claude.py` and
  `code/inspect_response.py`. Saw `stop_reason` both ways (`max_tokens` when
  capped, `end_turn` when given room). Forced an `AuthenticationError` with a
  bogus key. All "Done when" boxes ticked.
- **Track_B link:** none — HTTP + response object fields, not math.
- **Connect to real systems:** an agent loop branches on `resp.stop_reason`
  after every model call — `tool_use` → run the tool, append the result, call
  again; `end_turn` → stop and return the answer. It's the loop's exit condition.
- **Surprised me:**
  1. `resp.content` on `claude-opus-5` is `['thinking', 'text']` — thinking is
     **on by default**. `content[0]` is a `ThinkingBlock` (has `.thinking`, not
     `.text`), so `content[0].text` crashed. Fix: filter by `type`, never index
     by position: `next(b.text for b in resp.content if b.type == "text")`.
  2. Thinking tokens count against `max_tokens`. `max_tokens=60` truncated
     before any answer text; bumped course practice calls to `max_tokens=1024`.
  3. The session docs' worked example (`content[0].text`, `max_tokens=60`)
     predates default-on thinking — adjust as I go.
- **Still unclear / open question:** none.
- **Needs a Track_B deep-dive?** No.

#### Session 3 — Messages API: roles & parameters (2026-09-06)

- **Done:** Built `code/params_demo.py` and `code/roles_demo.py`. Saw: `system`
  steering style (TERSE vs VERBOSE), `temperature` 0 vs 1 (1 vs 2 distinct
  answers, via `extra_body` on Haiku), multi-turn recall ("42" carried because
  the list was resent), `stop_sequences` cutting at the first comma. Ran the
  3-turn `roles_demo.py`; turn 2 built on turn 1. Saw `input_tokens` rise
  60 → 282 across turns.
- **Track_B link:** light, non-blocking. *Revisit in Track_B: probability
  distributions & how temperature reshapes them.*
- **Connect to real systems:** (step 6 skipped — fill in.)
- **Surprised me:**
  1. `anthropic==1.4.0` `messages.create()` has **no `temperature` param at
     all** — `TypeError` before any request. Current SDK/model line dropped
     tunable sampling; reach it via `extra_body` and only on models that keep it.
  2. `system=None` passed explicitly → `400 "system: Input should be a valid
     array"`. Optional params must be **omitted**, not passed as `None`.
  3. In `roles_demo.py`, turn 1 showed `out=1024` (hit cap) but turn 2
     `input_tokens` only rose to 282 — most of turn 1's output was **thinking
     tokens**, and only the visible `text` block gets appended to history.
- **Still unclear / open question:** none flagged.
- **Needs a Track_B deep-dive?** No — noted for later.

#### Session 4 — Streaming + the Stage 0 build (2026-09-06)

- **Done:** Built `code/stream_vs_block.py` and `code/stream_prompt.py` (the
  Stage 0 deliverable). `stream_prompt.py` takes a CLI arg or prompts
  interactively, streams the reply live, then prints `stop_reason` + token
  counts. Saw streaming show first text much sooner than the blocking dead-stare;
  same total time and cost.
- **Track_B link:** none — transport / terminal buffering, no math.
- **Streaming vs blocking:** identical output and cost; only delivery differs.
  `stream.text_stream` yields text deltas (not thinking); `get_final_message()`
  is called inside the `with` block after the loop for `.usage` / `.stop_reason`.
  `end=""` suppresses print's newline, `flush=True` defeats terminal buffering.
- **Quick test:** both-halves habit landed — 4/5 fully complete. Sharpen: text
  comes from `stream.text_stream` specifically; `get_final_message()` must be
  inside the `with`.
- **Recall (step 0):** skipped again — meta gap still open (see revisit).
- **Needs a Track_B deep-dive?** No.
