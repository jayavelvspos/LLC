# Session 7 — Low-Code Orchestration: n8n & Langflow (~45 min)

**Objective:** build a real multi-step automation in **n8n** (a scheduled/
triggered business pipeline that calls an LLM), skim **Langflow** for visual
LangChain flows, and be able to say when a visual tool beats code and when it
doesn't.

**What you'll learn:**
- n8n nodes and building a scheduled/triggered LLM-calling pipeline
- Langflow's visual LangChain flows, at a skim level
- Where a visual tool wins over code, and where code wins

**Prerequisites:** Sessions 1–6 complete. Docker (both tools run locally in a
container).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | What low-code orchestrators are for; n8n vs Langflow |
| 10–35 | Build an n8n workflow: trigger → fetch → LLM → branch → output |
| 35–43 | Open the same idea in Langflow; note the difference |
| 43–45 | Notes + export `n8n_flow.json` |

---

## Concepts  <!-- step 2 -->

- **n8n** — a general workflow automation tool (Zapier-style, self-hostable).
  **Nodes** = triggers (webhook, cron, email, DB change) + actions (HTTP,
  Postgres, Slack, an AI/LLM node, a Code node). You wire nodes on a canvas;
  data flows as JSON items between them. Strong at **integrations and
  scheduling**, weak at complex branching logic and versioning.
- **Langflow** — a visual builder specifically for **LangChain/LangGraph**
  flows: drag prompt / model / retriever / agent components, connect them,
  export to Python or run as an API. Closer to what you built in Sessions 1–2,
  with a GUI.
- **Where visual wins:** connecting many SaaS systems, business users owning the
  flow, quick internal automations, cron'd jobs, demos. **Where code wins:**
  non-trivial control flow, testing, code review, version control, reuse,
  anything that needs an eval suite (Stage 6).
- **Common pattern:** prototype/glue in n8n; when a step gets hairy, call out to
  a code service (your LCEL chain or MCP server) via an HTTP node. The two
  aren't rivals — n8n handles triggers and I/O, your code handles reasoning.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- n8n docs — *Quickstart* + *AI / LangChain nodes*:
  <https://docs.n8n.io/>.
- Langflow docs — *Get started* and *Export / API*:
  <https://docs.langflow.org/>.

**Video (pick one, ~15–30 min):**
- Search *"n8n AI workflow tutorial"* — pick one that uses the HTTP + AI nodes,
  not a pure no-code SaaS chain.

---

## Track_B link (step 3)

**None.** Visual orchestration tooling — engineering and product choice, no
maths. Note "no Track_B link" and continue.

---

## Worked example — an n8n triage pipeline  <!-- step 4 -->

Run n8n locally:

```bash
docker run -it --rm -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
```

Build this workflow at `http://localhost:5678` (the **n8n Business Automation
Pipeline** example):

```
[Cron: every 15 min]
      -> [HTTP Request: GET open items from an issue tracker / RSS / sheet]
      -> [Split In Batches]
      -> [AI node: classify each item -> {team, severity, one-line summary}]
      -> [IF severity == "high"]
             true  -> [Slack: post to #oncall]
             false -> [Append Row: log to a Google Sheet / Postgres]
```

**Expected behaviour:**

```
run 1: 6 items fetched -> 1 high (posted to Slack), 5 logged
run 2 (15 min later): 2 new items -> 0 high, 2 logged
```

Read it: n8n owns the *trigger*, the *fetch*, the *fan-out over items*, the
*branch*, and the *delivery* — the boring plumbing. The only "AI" is one node
classifying each item. That division is the whole point: glue in n8n, judgment
in one model call.

---

## Build  <!-- step 5 -->

Build the workflow above (use any source you can GET — an RSS feed is fine).
Experiments:
1. **Call your own code.** Replace the AI node with an **HTTP Request** node
   that POSTs the item to a tiny FastAPI wrapper around your Session 1 LCEL
   `Ticket` chain. Same result, but now the reasoning step is versioned,
   testable code. Note what you gained and lost.
2. **Break a branch.** Point the Slack node at a bad webhook. Watch n8n's
   execution log show the failed node and the item it failed on. Compare that
   debugging experience to reading a LangSmith trace.
3. **Export.** Save the workflow as `code/n8n_flow.json`. Open it in a text
   editor — note it's just JSON (diffable, but not really code-reviewable).
4. **Langflow contrast.** Spin up Langflow, drag a `Prompt → ChatAnthropic →
   Parser` flow, run it. Write 3 sentences: for *your* work, when would you
   reach for Langflow over writing the LCEL chain from Session 1?

---

## Quick test (step 7 — answer from memory, then check)

1. What is an n8n "node", and what flows between nodes?
2. What is Langflow specifically a visual builder *for*?
3. Name two things visual orchestrators are good at and two things code is
   better at.
4. What's the "glue in n8n, judgment in code" pattern, and how do you connect
   the two?
5. Why is an exported n8n workflow diffable but not really reviewable?

<details><summary>Answers</summary>

1. A node is a trigger or an action (HTTP, DB, Slack, AI, Code…); JSON data
   items flow along the connections between nodes.
2. Building LangChain / LangGraph flows visually (prompt, model, retriever,
   agent components).
3. Good at: SaaS integrations, scheduling/triggers, business-user ownership,
   quick internal automations. Code better at: complex control flow, testing,
   version control, reuse, eval suites.
4. n8n handles triggers, fetching, fan-out, branching, delivery; a code service
   (LCEL chain / MCP server) does the reasoning — connected via an HTTP Request
   node.
5. It's JSON so a VCS can diff it, but the diff is node IDs and coordinates, not
   readable logic — hard to reason about in review.

</details>

---

## Done when  <!-- step 8 -->

- [ ] An n8n workflow runs on a trigger, calls an LLM (or your code) per item,
      branches, and delivers output two ways.
- [ ] One version calls your own versioned code via HTTP.
- [ ] You've opened the same shape in Langflow and written when you'd choose it.
- [ ] You can state the visual-vs-code tradeoff from memory.

## Pitfalls

- **Business logic buried in a canvas** — anything non-trivial belongs in
  reviewed code the flow *calls*.
- **Secrets in nodes** — use n8n credentials, not literal keys in HTTP nodes.
- **No error branch** — add a failure path (retry / alert), or a silent failure
  eats items.
- **Treating Langflow output as production code** — it's a prototyping and
  demo surface; graduate to hand-written chains for anything you must maintain.

## Carries to next stage

You've seen the full orchestration spectrum: raw SDK (Stage 1) → LCEL/LangGraph
(Stage 2, 5B) → multi-agent frameworks (Stage 5) → low-code (here). **Stage 6**
takes whichever you choose and makes it production-grade: tracing, evals, CI,
reliability, guardrails, deployment.
