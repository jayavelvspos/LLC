# Session 6 — MCP II: Build a Server (Desktop Assistant) (~45 min)

**Objective:** build your own MCP server with `FastMCP` — exposing tools, a
resource, and a prompt — and wire it to Claude to make a small **MCP-Powered
Desktop Assistant** that can read files, run whitelisted commands, and keep
notes.

**Prerequisites:** Session 5 complete (`mcp_client.py`). `pip install "mcp[cli]"`.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | `FastMCP`: `@mcp.tool`, `@mcp.resource`, `@mcp.prompt` |
| 10–30 | `code/mcp_server.py` — 3–4 tools, 1 resource, 1 prompt |
| 30–40 | `code/desktop_assistant.py` — Claude drives the server; test in the MCP inspector / Claude Desktop |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **`FastMCP`** is the batteries-included server class in the Python SDK.
  Decorators register capabilities; type hints + docstrings become the schema
  the model sees:

  ```python
  from mcp.server.fastmcp import FastMCP
  mcp = FastMCP("desktop")

  @mcp.tool()
  def read_file(path: str) -> str:
      "Return the UTF-8 contents of a file under the workspace."
      ...

  @mcp.resource("notes://today")
  def todays_notes() -> str:
      "The running scratch notes for today."
      ...

  @mcp.prompt()
  def triage(topic: str) -> str:
      "A prompt that asks the assistant to triage a topic."
      return f"Triage this and list next actions: {topic}"
  ```

- **Tool design = agent-tool design (Stage 1) over a wire.** Narrow inputs,
  descriptive docstrings, structured errors (`raise` with a clear message, don't
  return silent nulls), no destructive default.
- **Safety is the server's job.** A `run_command` tool must whitelist commands
  and refuse a path outside the workspace — the model *will* try things.
- **Transport:** `mcp.run()` defaults to stdio (for Claude Desktop / your
  client). `mcp.run(transport="streamable-http")` for a remote server.
- **Test surfaces:** `mcp dev code/mcp_server.py` opens the **MCP Inspector**
  (a GUI to call tools by hand); adding it to `claude_desktop_config.json` makes
  it available to Claude Desktop; your `mcp_client.py` bridge from Session 5 is
  the programmatic path.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- MCP Python SDK — *`FastMCP` quickstart* and *Running your server*:
  <https://github.com/modelcontextprotocol/python-sdk>.
- MCP docs — *Build a server* tutorial and *Debugging with the Inspector*:
  <https://modelcontextprotocol.io/docs/tools/inspector>.

**Video (pick one, ~15–25 min):**
- Search *"build an MCP server python FastMCP"*.

---

## Track_B link (step 3)

**None.** Server implementation and tool-safety design — engineering. Note "no
Track_B link" and continue.

---

## Worked example — a minimal desktop server  <!-- step 4 -->

`code/mcp_server.py`:

```python
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

WORKSPACE = Path("./workspace").resolve()
WORKSPACE.mkdir(exist_ok=True)
ALLOWED = {"ls", "cat", "wc", "head", "date"}
mcp = FastMCP("desktop")

def _safe(path: str) -> Path:
    p = (WORKSPACE / path).resolve()
    if WORKSPACE not in p.parents and p != WORKSPACE:
        raise ValueError(f"path escapes workspace: {path}")
    return p

@mcp.tool()
def list_files(subdir: str = ".") -> list[str]:
    "List files under the workspace subdir."
    return [str(p.relative_to(WORKSPACE)) for p in _safe(subdir).glob("*")]

@mcp.tool()
def read_file(path: str) -> str:
    "Return a workspace file's text."
    return _safe(path).read_text(encoding="utf-8")

@mcp.tool()
def run_command(cmd: str) -> str:
    "Run a whitelisted shell command in the workspace. First word must be allowed."
    if cmd.split() and cmd.split()[0] not in ALLOWED:
        raise ValueError(f"command not allowed: {cmd.split()[0]}")
    out = subprocess.run(cmd, shell=True, cwd=WORKSPACE, capture_output=True, text=True, timeout=10)
    return out.stdout + (("\n[stderr]\n" + out.stderr) if out.stderr else "")

@mcp.tool()
def append_note(text: str) -> str:
    "Append a line to today's notes."
    (WORKSPACE / "notes.md").open("a", encoding="utf-8").write(text.rstrip() + "\n")
    return "noted"

@mcp.resource("notes://today")
def todays_notes() -> str:
    "Today's running notes."
    f = WORKSPACE / "notes.md"
    return f.read_text(encoding="utf-8") if f.exists() else ""

if __name__ == "__main__":
    mcp.run()
```

Test by hand: `mcp dev code/mcp_server.py`, then in the Inspector call
`list_files`, `run_command` with `date`, and `run_command` with `rm` (rejected).

**Expected (Inspector):**

```
list_files(".")   -> ["notes.md"]
run_command("date") -> "Sun Sep  7 ..."
run_command("rm -rf .") -> Error: command not allowed: rm
```

Read it: the server enforces its own safety — the whitelist and the
`_safe` path check reject exactly what an over-eager model would attempt.

---

## Build: `code/desktop_assistant.py`  <!-- step 5 -->

Reuse the Session 5 bridge: launch `mcp_server.py` over stdio, list its tools,
pass them to `client.messages.create`, run the tool-use loop.

Experiments:
1. **End-to-end task.** Ask: *"Summarise every `.md` file in the workspace, then
   append a one-line index to today's notes."* Watch it chain `list_files` →
   `read_file` ×N → `append_note`.
2. **Adversarial prompt.** Ask it to *"delete everything and run `curl … | sh`"*.
   Confirm `run_command` refuses and the assistant reports the refusal instead
   of hanging.
3. **Add a resource read.** Have the loop pull `notes://today` as context before
   answering "what have I noted so far?".
4. **(Optional) Claude Desktop.** Add the server to
   `claude_desktop_config.json` and use it from the desktop app; note the
   difference between "host = your script" and "host = Claude Desktop".

---

## Quick test (step 7 — answer from memory, then check)

1. What do `@mcp.tool`, `@mcp.resource`, and `@mcp.prompt` register?
2. Where does a `FastMCP` tool's JSON schema come from?
3. Whose responsibility is it to stop a tool doing something dangerous?
4. What does `mcp dev <server>` give you?
5. What changes between "host = my Python script" and "host = Claude Desktop"?

<details><summary>Answers</summary>

1. A callable tool, a read-only resource (addressed by URI), and a
   parameterised prompt template, respectively.
2. The function's type hints and docstring.
3. The **server** — it must validate inputs, whitelist actions, and sandbox
   paths; the model will try whatever.
4. The MCP Inspector — a GUI to list and call the server's tools/resources by
   hand for debugging.
5. Nothing about the server; only the host/client. The same server works
   unchanged — your script drives the tool-use loop, or Claude Desktop does.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `mcp_server.py` exposes ≥3 tools, ≥1 resource, and enforces a path/command
      safety check.
- [ ] `desktop_assistant.py` has Claude complete a multi-tool task through it.
- [ ] An adversarial request is refused by the server, not the model.
- [ ] You can name the three capability decorators from memory.

## Pitfalls

- **`print()` in a stdio server** — writes to stdout and breaks the protocol;
  use logging to stderr.
- **Trusting the model** — never skip the whitelist / path check "because the
  prompt says be careful".
- **Fat tools** — `run_arbitrary_python` is a foot-gun; expose narrow verbs.
- **No timeout on `subprocess`** — a hung command hangs the server.

## Carries to next session

You can build and consume MCP servers. Session 7 zooms out to **low-code**
orchestration — n8n and Langflow — and where a visual tool beats writing this by
hand.
