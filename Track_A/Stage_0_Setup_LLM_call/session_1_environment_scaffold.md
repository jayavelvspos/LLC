# Session 1 — Environment & Project Scaffold (~45 min)

**Objective:** a clean, reproducible Python environment with the Anthropic SDK
installed and a `.env` layout ready. No API calls this session — just the ground
to stand on.

**Prerequisites:** Python 3.10+ installed (`python --version`), a terminal, and
an editor.

**Method:** run this session with the 7-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). The sections below feed that loop.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Create project folder + virtual environment |
| 10–25 | Install `anthropic` and `python-dotenv`, pin `requirements.txt` |
| 25–40 | Set up `.env`, `.env.example`, `.gitignore` |
| 40–45 | Verify import, write `notes.md` stub |

---

## Steps

### 1. Folder + venv (0–10)

```powershell
cd D:\AI\Track_A\Stage_0_Setup_LLM_call
mkdir code
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Your prompt should now show `(.venv)`. If PowerShell blocks activation, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

### 2. Install + pin (10–25)

```powershell
python -m pip install --upgrade pip
pip install anthropic python-dotenv
pip freeze > requirements.txt
```

Open `requirements.txt` and confirm `anthropic==...` and `python-dotenv==...`
are listed with versions. Pinned versions are what makes the env reproducible.

### 3. Secrets layout (25–40)

Create `.env` (real key goes here next session — leave the value blank for now):

```
ANTHROPIC_API_KEY=
```

Create `.env.example` (committed, no secret):

```
ANTHROPIC_API_KEY=sk-ant-...replace-me...
```

Create `.gitignore`:

```
.venv/
.env
__pycache__/
*.pyc
```

Rule: `.env` is **never** committed. `.env.example` documents what keys are
needed. Anyone cloning the repo copies `.env.example` to `.env` and fills it in.

### 4. Verify + notes (40–45)

```powershell
python -c "import anthropic, dotenv; print(anthropic.__version__)"
```

Prints a version string with no error = SDK is importable.

Create `notes.md` with one line: `## Stage 0 notes` — you'll add surprises,
questions, and cost observations here as you go. This feeds the every-2-weeks
review in `Track_A/CLAUDE.md`.

---

## Learning resources

**Primary (official, stable):**
- Anthropic — *Anthropic API fundamentals* course, notebook **"Getting the SDK
  set up" / ch. 1**: <https://github.com/anthropics/courses> → folder
  `anthropic_api_fundamentals`. Covers API key creation and SDK install exactly
  at this session's level.
- Anthropic docs — *Get started* / *Initial setup*:
  <https://docs.anthropic.com/en/docs/get-started> (also served at
  docs.claude.com).

**Video (pick one, ~15–25 min):**
- **Corey Schafer** — search YouTube for *"Corey Schafer virtualenv"* (his
  "Python Tutorial: virtualenv and why you should use virtual environments").
  The clearest explanation of what a venv is and why it matters.
- Search *"python-dotenv tutorial"* — any 5–10 min walkthrough of loading a
  `.env` file is enough.

**Reference:**
- `anthropic` SDK README: <https://github.com/anthropics/anthropic-sdk-python>

---

## Track_B link (step 3)

**None.** This session is pure tooling — venvs, package installs, secret files.
There is no `Track_B/Math_stat` fundamental underneath it. Write "no Track_B
link" in `notes.md` and continue.

For context: the first real Track_A ↔ Track_B intersection is **Stage 4 (RAG) →
`Track_B/Math_stat/01_linear_algebra`** (cosine similarity). Nothing in Stage 0
requires a detour.

---

## Worked example — prove the environment is sane

`code/check_env.py` (throwaway, delete after):

```python
import sys, importlib
print("python:", sys.version.split()[0])
for pkg in ("anthropic", "dotenv"):
    m = importlib.import_module(pkg)
    print(f"{pkg}:", getattr(m, "__version__", "(no __version__)"))
```

Run:

```powershell
python code\check_env.py
```

**Expected output** (versions will differ):

```
python: 3.12.4
anthropic: 0.42.0
dotenv: (no __version__)
```

If `python:` shows a version outside 3.10–3.13, or either import raises
`ModuleNotFoundError`, your venv isn't the active interpreter — fix that before
Session 2.

---

## Quick test (step 6 — answer from memory, then check)

1. What does a virtual environment isolate, and why does that give you
   reproducibility?
2. Why is `.env` git-ignored while `.env.example` is committed?
3. You installed `anthropic`, but `import anthropic` fails. Most likely cause?
4. Which command captures your current dependency versions into a file?
5. What's the minimum Python version for this track, and how do you check it?

<details><summary>Answers</summary>

1. It isolates project-specific packages **and their exact versions** from
   system Python and other projects. Combined with pinned `requirements.txt`,
   anyone can recreate the identical dependency set → identical behavior.
2. `.env` holds the real API key — committing it leaks a credential.
   `.env.example` carries only placeholders, documenting which keys a fresh
   clone must supply.
3. The active interpreter is system Python, not the venv — the terminal or
   editor isn't using `.venv`. Re-activate it.
4. `pip freeze > requirements.txt`.
5. 3.10+; `python --version`.

</details>

---

## Done when

- [ ] `.venv` activates and `(.venv)` shows in the prompt.
- [ ] `requirements.txt` exists with pinned versions.
- [ ] `.env`, `.env.example`, `.gitignore` exist; `.gitignore` excludes `.env`.
- [ ] `import anthropic` succeeds and prints a version.

## Pitfalls

- **Wrong interpreter:** if `import anthropic` fails right after install, your
  editor/terminal is probably using system Python, not `.venv`. Re-check that
  the venv is activated.
- **Committing `.env`:** if this repo ever gets a git remote, a leaked key is a
  real incident. The `.gitignore` entry is not optional.

## Carries to next session

An activated venv and an empty `ANTHROPIC_API_KEY` line in `.env` waiting for a
real value.
