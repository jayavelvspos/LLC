# Track A — Stage templates

Reusable structure so every stage runs the same way. Stage 0
(`../Stage_0_Setup_LLM_call/`) is the worked reference implementation.

## Files

| File | Copy to | As |
|------|---------|----|
| `SESSION_METHOD.md` | the stage folder | `_SESSION_METHOD.md` |
| `session_file.md` | the stage folder, once per session | `session_<n>_<slug>.md` |

(There's no stage-`README.md` template yet — copy `../Stage_0_Setup_LLM_call/README.md`
and adapt it: session table, conventions, working-files map, "Done with Stage" checklist.)

## Spinning up a new stage

1. `mkdir Stage_<n>_<Name>` under `Track_A/`, with a `code/` subfolder.
2. Copy `SESSION_METHOD.md` → `Stage_<n>_<Name>/_SESSION_METHOD.md`. Fill the two
   **«FILL»** spots: the stage name, and the **Track_B footing** table (which
   `Track_B/Math_stat` topics this stage leans on, and whether each can block).
3. Split the stage's learning path into ~45-minute sessions. Copy
   `session_file.md` once per session and fill every `<…>`.
4. Copy and adapt a stage `README.md` from Stage 0.
5. Add a `notes.md` stub in the stage folder (`## Stage <n> notes`).

## Conventions that must stay identical across stages

- The **8-step loop** in `_SESSION_METHOD.md` — don't edit the steps per stage;
  only the «FILL» spots change.
- Every session file has, in this order: Objective · Prerequisites · Method
  pointer · Timebox · Concepts · Learning resources · **Track_B link** · Worked
  example (+ Expected output) · Build · Quick test (+ answers) · Done when ·
  Pitfalls · Carries to next session.
- `notes.md` is the running log per stage — surprises, "revisit" items, and the
  Track_B deep-dive flags that feed the every-2-weeks review in `../CLAUDE.md`.
- One learning resource per session. Videos referenced as *channel + search
  query*, not fragile URLs.
