# Commit plan for PawPal+ Modules 1–3 submission

The rubric requires meaningful commit history. Below is a recommended sequence
of commits to apply on top of your existing branch so the history reads as
real iterative work instead of a single dump.

> **Pre-flight:** make sure your local working tree is clean
> (`git status` should show no uncommitted changes), then drop the
> updated files from this delivery into the repo root in the order below.

## How to apply

```bash
cd <your local clone of ai110-module2show-pawpal-starter>

# Stage 1 — domain layer hardening
cp .../pawpal_system.py ./pawpal_system.py
git add pawpal_system.py
git commit -m "Add input validation and structured logging to domain layer"

# Stage 2 — validation tests
mkdir -p tests
cp .../tests/test_validation.py tests/test_validation.py
git add tests/test_validation.py
git commit -m "Add validation tests for Task, Pet, Owner"

# Stage 3 — central logging
cp .../logging_config.py ./logging_config.py
git add logging_config.py
git commit -m "Add centralized logging config (logs/pawpal.log, rotating)"

# Stage 4 — AI assistant module
cp .../ai_assistant.py ./ai_assistant.py
git add ai_assistant.py
git commit -m "Add AI assistant: explain plan, suggest tasks, care Q&A with vet-redirect guardrail"

# Stage 5 — AI tests
cp .../tests/test_ai_assistant.py tests/test_ai_assistant.py
git add tests/test_ai_assistant.py
git commit -m "Add AI assistant tests (mock provider, guardrails, error fallback)"

# Stage 6 — eval harness with summary stat
mkdir -p eval
cp .../eval/eval_set.json eval/eval_set.json
cp .../eval/run_eval.py   eval/run_eval.py
git add eval/
git commit -m "Add evaluation harness with held-out eval set and summary accuracy stat"

# Stage 7 — wire AI into the UI and demo CLI
cp .../app.py  ./app.py
cp .../main.py ./main.py
git add app.py main.py
git commit -m "Wire AI features into Streamlit UI and demo CLI"

# Stage 8 — config and dependencies
cp .../requirements.txt ./requirements.txt
cp .../.env.example      ./.env.example
cp .../.gitignore        ./.gitignore
git add requirements.txt .env.example .gitignore
git commit -m "Add provider config (.env.example) and update requirements"

# Stage 9 — organize existing diagrams into /assets/
mkdir -p assets
git mv mermaid.png   assets/architecture-mermaid.png || cp .../assets/architecture-mermaid.png assets/
git mv uml_final.png assets/uml-diagram.png          || cp .../assets/uml-diagram.png          assets/
git add assets/
git commit -m "Move diagrams into /assets/ for portfolio organization"

# Stage 10 — walkthrough screenshots + GIF (replaces the Loom requirement)
mkdir -p assets/walkthrough scripts
cp .../assets/walkthrough/*.png  assets/walkthrough/
cp .../assets/walkthrough/walkthrough.gif assets/walkthrough/
cp .../scripts/build_walkthrough.py scripts/
git add assets/walkthrough/ scripts/build_walkthrough.py
git commit -m "Add embedded walkthrough: 6 screenshots + animated GIF for end-to-end demo"

# Stage 11 — documentation
cp .../architecture.mmd ./architecture.mmd
cp .../README.md         ./README.md
cp .../model_card.md     ./model_card.md
git add architecture.mmd README.md model_card.md
git commit -m "Rewrite README with embedded walkthrough, architecture diagram, eval stats; add model_card.md"

# Stage 12 — push
git push origin main
```

## Commit messages at a glance

| # | Commit message |
|---|---|
| 1 | Add input validation and structured logging to domain layer |
| 2 | Add validation tests for Task, Pet, Owner |
| 3 | Add centralized logging config (logs/pawpal.log, rotating) |
| 4 | Add AI assistant: explain plan, suggest tasks, care Q&A with vet-redirect guardrail |
| 5 | Add AI assistant tests (mock provider, guardrails, error fallback) |
| 6 | Add evaluation harness with held-out eval set and summary accuracy stat |
| 7 | Wire AI features into Streamlit UI and demo CLI |
| 8 | Add provider config (.env.example) and update requirements |
| 9 | Move diagrams into /assets/ for portfolio organization |
| 10 | Add embedded walkthrough: 6 screenshots + animated GIF for end-to-end demo |
| 11 | Rewrite README with embedded walkthrough, architecture diagram, eval stats; add model_card.md |

## After all commits

1. Run the suite once more: `python -m pytest tests/ -v && python eval/run_eval.py`
2. Verify the GIF/screenshots render on GitHub (open the repo's README on github.com after pushing)
3. Verify the repo is **public** (Settings → General → Danger Zone → Change visibility to public)
4. Submit the URL: `https://github.com/chinenyeze49-sketch/ai110-module2show-pawpal-starter`
