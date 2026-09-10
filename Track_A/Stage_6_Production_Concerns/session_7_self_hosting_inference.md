# Session 7 — Self-Hosting Inference: Ollama, vLLM, Docker (~45 min)

**Objective:** run an open-weights model locally with **Ollama** and understand
**vLLM** as the production serving option; call both through their
OpenAI-compatible endpoints; and decide *which* calls in your system (if any)
should go to a self-hosted model instead of the Anthropic API.

**Prerequisites:** Sessions 1–6 complete (you have `service.py` and the eval
suite). Docker; ~8 GB free RAM for a small model.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Why (and why not) self-host; Ollama vs vLLM |
| 10–25 | Run a model in Ollama; call it via the OpenAI-compatible API |
| 25–40 | Route one sub-task in your system to the local model; eval it |
| 40–45 | Notes — the decision table |

---

## Concepts  <!-- step 2 -->

- **Why self-host:** data never leaves your infra (privacy/compliance),
  predictable cost at high volume, no per-token bill, no rate limits, offline
  capability. **Why not:** you own the GPUs, the ops, the model quality gap, and
  the scaling headache; a frontier model via API is usually cheaper *and* better
  until volume is large.
- **Ollama** — the easy button. `ollama run llama3.1` pulls and serves a
  quantised model on your machine (CPU or GPU) with an OpenAI-compatible API at
  `http://localhost:11434/v1`. Great for dev, prototyping, small local tools,
  and privacy-sensitive low-volume work.
- **vLLM** — the production server. High-throughput batched inference
  (PagedAttention, continuous batching) behind an OpenAI-compatible API; runs in
  Docker on a GPU box or K8s. This is what you'd actually deploy if self-hosting
  at scale.
- **OpenAI-compatible = a drop-in swap.** Point the OpenAI SDK (or LangChain's
  `ChatOpenAI` / `langchain-openai`) at the local `base_url`. Your chain code
  doesn't change; only the client target and model name do.
- **Hybrid routing** is the realistic pattern: keep judgment-heavy steps
  (supervisor, final writer, the evaluator) on Claude; move high-volume,
  low-stakes steps (classification, cheap summarisation, PII pre-screen) to a
  local model. Decide per step, backed by the eval — not globally.
- **The eval is the gate.** Swapping a step to a local model is a change; run
  Session 2's suite and see whether quality holds before you keep it.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- Ollama docs — *Quickstart* and *OpenAI compatibility*:
  <https://github.com/ollama/ollama/blob/main/docs/openai.md>.
- vLLM docs — *OpenAI-compatible server* and *Deploying with Docker*:
  <https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html>.

**Video (pick one, ~15–25 min):**
- Search *"vLLM vs Ollama"* or *"self-host LLM OpenAI compatible API"* — focus on
  the throughput/ops difference, not the model-download steps.

---

## Track_B link (step 3)

**None.** Model serving infrastructure — GPUs, batching, containers. The
*decision* (local vs API for a given step) is a cost/quality tradeoff you settle
with the eval, same as Stage 0 Session 5. Note "no Track_B link" and continue.

---

## Worked example — same chain, local model  <!-- step 4 -->

```bash
# one-time
ollama pull llama3.1:8b
ollama serve            # serves http://localhost:11434
```

`code/local_infer.py`:

```python
from langchain_openai import ChatOpenAI

local = ChatOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",                       # ignored, but required by the client
    model="llama3.1:8b",
    temperature=0,
)

# reuse Stage 5B Session 1's classification prompt, unchanged
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages([
    ("system", "Reply with exactly one word: bug, billing, feature, or other."),
    ("human", "{msg}"),
])
chain = prompt | local

for m in ["charged twice this month", "add dark mode please", "export crashes on Safari"]:
    print(m, "->", chain.invoke({"msg": m}).content.strip())
```

**Expected output** (shape):

```
charged twice this month -> billing
add dark mode please -> feature
export crashes on Safari -> bug
```

Read it: the chain is byte-for-byte the same as the Claude version — only the
client target changed. For a tight classification prompt an 8B local model is
often fine; for the research *brief* it usually isn't. That gap is the decision.

---

## Build: `code/local_infer.py` + a routed step  <!-- step 5 -->

1. **Run it.** Get Ollama serving and the classification chain passing on a
   handful of inputs.
2. **Route one real step.** In `service.py` / `research.py`, send the
   *classification* or *PII pre-screen* step to the local model, keep everything
   else on Claude. Run Session 2's eval suite. Did `mean_score` hold? Did
   latency improve? Did `$/request` drop?
3. **Break-even.** Estimate: at what monthly request volume would a $X/mo GPU
   box for vLLM beat the API cost of that step? (Rough is fine — it's an
   order-of-magnitude call.)
4. **vLLM (read/optional).** Skim the vLLM Docker run command; note what changes
   vs Ollama (GPU required, throughput, `--max-model-len`, K8s). Don't stand it
   up unless you have a GPU.

---

## Quick test (step 7 — answer from memory, then check)

1. Two reasons to self-host, and two reasons not to.
2. Ollama vs vLLM — what is each for?
3. What does "OpenAI-compatible endpoint" let you do to existing chain code?
4. What's the hybrid routing pattern, and how do you decide per step?
5. What has to happen before you keep a step on a local model?

<details><summary>Answers</summary>

1. For: data stays in your infra, predictable cost at volume, no rate limits,
   offline. Against: you own GPUs + ops, quality gap vs frontier, scaling is
   hard (API is usually cheaper and better until volume is large).
2. Ollama = easy local serving for dev / small tools / privacy-sensitive
   low-volume; vLLM = high-throughput production serving on GPUs.
3. Swap `base_url` + model name (and use `ChatOpenAI`); the prompt/chain logic
   is unchanged.
4. Judgment-heavy steps stay on Claude; high-volume low-stakes steps go local.
   Decide per step using the eval, not globally.
5. Run the eval suite (Session 2) and confirm quality holds — swapping a step is
   a change like any other.

</details>

---

## Done when  <!-- step 8 -->

- [ ] A model runs locally in Ollama and answers via its OpenAI-compatible API.
- [ ] One step of your system is routed to the local model and the eval suite
      still passes (or you reverted it because it didn't).
- [ ] You have a rough break-even volume for self-hosting that step.
- [ ] You can explain the Ollama/vLLM split and the hybrid routing pattern from
      memory.

## Pitfalls

- **Assuming local == free** — GPU boxes, electricity, and ops time are real;
  do the break-even.
- **Swapping a judgment step to an 8B model** — classification is fine; the
  final brief / evaluator usually regresses. Check the eval.
- **No eval before/after** — you can't claim it's "good enough" without the
  number.
- **Ollama in prod** — it's a dev tool; use vLLM (or the API) for real traffic.

## Carries forward

You now know the full model-sourcing spectrum: frontier API (default) →
managed cloud (Bedrock/Vertex) → self-hosted (vLLM) → local (Ollama), and how to
route between them per step with the eval as the gate. That completes the
Stage 6 production toolkit; the roadmap's **Stage 7** capstone puts the whole
stack to work on one hard problem.
