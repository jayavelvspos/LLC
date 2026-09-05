# Stage 1 — Your First Agent (No Framework)

**Stage goal:** understand what an agent fundamentally is — an LLM call, plus a
loop, plus tools — by building one with the raw `anthropic` SDK and no
framework. The framework (LangGraph) starts in Stage 2; you can't appreciate
what it does for you until you've hand-rolled the loop once.

Five ~45-minute sessions, in order.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [Tool definitions & a single tool call](session_1_tool_definitions_single_call.md) | one manual request → `tool_use` → `tool_result` → final answer |
| 2 | [The agent loop](session_2_the_agent_loop.md) | a `while` loop that runs tools until the model is done, with a max-iteration guard |
| 3 | [Multiple tools & dispatch](session_3_multiple_tools_dispatch.md) | 3 tools, a name→function dispatch table, parallel `tool_use` handled |
| 4 | [Error handling & robustness](session_4_error_handling_robustness.md) | tool failures returned as `is_error`, bad args, timeouts, per-step logging |
| 5 | [Build & harden the CLI agent](session_5_build_cli_agent.md) | `agent.py` — the Stage 1 deliverable |

## Conventions

Same as Stage 0 (see `../Stage_0_Setup_LLM_call/README.md`): Python 3.10+, the
`anthropic` SDK, `claude-opus-5` by default (`claude-haiku-4-5` for cheap
practice runs). Run every session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md).

Reuse the venv and `.env` from Stage 0, or make a fresh one — your call. Keep a
`notes.md` in this folder.

## Working files produced in this stage

```
Stage_1_First_Agent_No_Framework/
  code/
    single_tool.py     # session 1
    agent_loop.py      # session 2
    tools.py           # session 3 — tool defs + dispatch table
    agent.py           # session 5 — the deliverable CLI agent
  notes.md
```

## Done with Stage 1 when

- [ ] `python code/agent.py "a question needing 2+ tool steps"` returns a
      correct answer after chaining tool calls.
- [ ] The loop cannot run forever — there is a hard iteration cap.
- [ ] A tool that raises is reported back to the model as `is_error: true`, and
      the agent recovers instead of crashing.
- [ ] Every step (model turn, tool call, tool result) is logged to a transcript.
- [ ] You can explain, without notes: the `tool_use` / `tool_result` cycle, why
      the loop terminates, and what state the agent carries between turns.
