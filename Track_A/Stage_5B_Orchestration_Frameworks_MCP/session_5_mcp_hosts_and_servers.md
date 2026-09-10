# Session 5 — MCP I: Hosts, Servers, Transports (~45 min)

**Objective:** understand what the Model Context Protocol is, connect a client to
an **existing** MCP server, list and call its tools, and bridge those tools into
a Claude tool-use loop.

**Prerequisites:** Sessions 1–4 complete. Stage 1 (the agent loop / tool-use
cycle). `pip install mcp`; `npx` available (the reference servers are Node).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | MCP vocabulary: host, client, server, capabilities, transports |
| 10–25 | `code/mcp_client.py` — connect to the filesystem server, list + call tools |
| 25–40 | Bridge MCP tools into a Claude `messages.create` tool-use loop |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **MCP** is an open protocol for giving LLM apps context and tools through a
  uniform interface — "USB-C for AI tools". Write a tool server once; any MCP
  host can use it.
- **Roles:**
  - **Host** — the LLM application (Claude Desktop, an IDE, *your* agent).
  - **Client** — lives inside the host; keeps one connection to one server.
  - **Server** — exposes capabilities. Three kinds:
    - **Tools** — functions the model may call (side effects allowed).
    - **Resources** — read-only data the host can pull in (files, rows, docs).
    - **Prompts** — parameterised message templates / workflows the user can pick.
- **Transports:** **stdio** (host launches the server as a subprocess, talks
  over stdin/stdout — local tools) and **Streamable HTTP / SSE** (a remote
  server over HTTP). Same protocol messages either way.
- **Handshake:** `initialize` → capability negotiation → then
  `tools/list`, `tools/call`, `resources/list`, `resources/read`, etc.
- **Bridging to a model:** MCP tool schemas map almost 1:1 onto the Anthropic
  `tools=[...]` format. Your loop: model asks for a tool → you `session.call_tool`
  → feed the result back as a `tool_result` → repeat. (The Anthropic API also
  has a native MCP connector; the manual bridge is the instructive version.)

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- MCP docs — *Introduction* and *Core concepts* (architecture, transports):
  <https://modelcontextprotocol.io/>.
- MCP Python SDK README — `ClientSession`, `stdio_client`:
  <https://github.com/modelcontextprotocol/python-sdk>.
- Reference servers list (filesystem, fetch, git, …):
  <https://github.com/modelcontextprotocol/servers>.

**Video (pick one, ~15–25 min):**
- Search *"Model Context Protocol explained"* — focus on host/client/server and
  the stdio vs HTTP transports.

---

## Track_B link (step 3)

**None.** MCP is a wire protocol and a client/server architecture — pure
engineering. Note "no Track_B link" and continue.

---

## Worked example — talk to the filesystem server  <!-- step 4 -->

`code/mcp_client.py`:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", "."],  # serves the cwd
)

async def main():
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = (await session.list_tools()).tools
            print("tools:", [t.name for t in tools])

            res = await session.call_tool("list_directory", {"path": "."})
            print(res.content[0].text[:300])

asyncio.run(main())
```

**Expected output** (shape):

```
tools: ['read_file', 'read_multiple_files', 'write_file', 'edit_file',
        'create_directory', 'list_directory', 'move_file', 'search_files',
        'get_file_info', 'list_allowed_directories']
[DIR]  code
[FILE] README.md
[FILE] notes.md
...
```

Read it: the client launched the Node server as a subprocess over **stdio**,
negotiated capabilities, and called a tool by name with a JSON argument — the
same `tools/list` + `tools/call` you'd get from any MCP host.

---

## Build: `code/mcp_client.py`  <!-- step 5 -->

Extend the client into a mini agent:
1. **Schema bridge.** Convert each MCP tool to the Anthropic tool format
   (`{"name", "description", "input_schema": t.inputSchema}`) and pass them to
   `client.messages.create(..., tools=bridged)`.
2. **Tool-use loop.** When the model returns `stop_reason == "tool_use"`, call
   `session.call_tool(block.name, block.input)`, append a `tool_result`, and
   loop until `end_turn`. Ask it: *"How many Python files are under `code/` and
   what's the largest?"*
3. **Second server.** Add `@modelcontextprotocol/server-fetch` (or `-git`) as a
   second `ClientSession`. Merge both tool lists. Ask a question that needs one
   tool from each server.

---

## Quick test (step 7 — answer from memory, then check)

1. Define host, client, and server in MCP.
2. Name the three kinds of capability a server can expose.
3. The two transports, and when you'd use each.
4. Which two protocol calls list and invoke a tool?
5. How does an MCP tool get used by Claude via the Messages API?

<details><summary>Answers</summary>

1. Host = the LLM app; client = the in-host connector holding one connection;
   server = the process exposing tools/resources/prompts.
2. Tools (callable functions), resources (read-only data), prompts (templated
   workflows).
3. **stdio** — local, host spawns the server as a subprocess; **Streamable
   HTTP/SSE** — remote server over HTTP.
4. `tools/list` and `tools/call`.
5. Bridge the MCP tool schema into the Anthropic `tools=[...]` format; on
   `stop_reason == "tool_use"` call `session.call_tool`, return the output as a
   `tool_result`, loop.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `mcp_client.py` connects to a reference MCP server and lists its tools.
- [ ] Claude answers a question by calling ≥2 MCP tools through your bridge loop.
- [ ] You've connected two servers at once and used a tool from each.
- [ ] You can explain host/client/server and the two transports from memory.

## Pitfalls

- **`npx` not found / server not installed** — the reference servers are Node
  packages; `-y` lets `npx` fetch them on first run.
- **Filesystem server path** — it only serves the directories you pass as args;
  a tool call outside them errors by design.
- **Forgetting `await session.initialize()`** — every other call fails until the
  handshake completes.
- **stdio server writing logs to stdout** — corrupts the protocol stream;
  servers must log to stderr.

## Carries to next session

You can consume MCP servers. Session 6 has you **build** one with `FastMCP` and
wire it to Claude as the *MCP-Powered Desktop Assistant*.
