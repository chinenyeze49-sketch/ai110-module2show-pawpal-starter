#!/usr/bin/env bash
# One-shot script to commit all PawPal+ updates and push to GitHub.
# Run this from VS Code's bash terminal:    bash PUSH.sh
# After it finishes, verify on https://github.com/chinenyeze49-sketch/ai110-module2show-pawpal-starter

set -e

echo "=== Cleaning up stale files (safe — these were sandbox test artifacts) ==="
rm -f .git/index.lock .git/_testfile _writetest _newfile.txt
rm -f mermaid.png uml_final.png    # now lived under assets/, removing root copies
echo "OK"

echo ""
echo "=== Running tests + eval one final time ==="
python -m pytest tests/ -q
python eval/run_eval.py >/dev/null 2>&1 && echo "Eval: PASS" || echo "Eval: FAIL (check manually)"

echo ""
echo "=== Configuring commit identity ==="
git config user.name  "$(git log -1 --format='%an')"
git config user.email "$(git log -1 --format='%ae')"
git config core.autocrlf false

echo ""
echo "=== Discarding line-ending-only diffs on existing tracked files ==="
git checkout -- .gitignore reflection.md data.json 2>/dev/null || true

echo ""
echo "=== Making 11 commits ==="

git add pawpal_system.py
git commit -m "Add input validation and structured logging to domain layer"

git add tests/test_validation.py
git commit -m "Add validation tests for Task, Pet, Owner"

git add logging_config.py
git commit -m "Add centralized logging config (logs/pawpal.log, rotating)"

git add ai_assistant.py
git commit -m "Add AI assistant: explain plan, suggest tasks, care Q&A with vet-redirect guardrail"

git add tests/test_ai_assistant.py
git commit -m "Add AI assistant tests (mock provider, guardrails, error fallback)"

git add eval/
git commit -m "Add evaluation harness with held-out eval set and summary accuracy stat"

git add app.py main.py
git commit -m "Wire AI features into Streamlit UI and demo CLI"

git add requirements.txt .env.example .gitignore
git commit -m "Add provider config (.env.example) and update requirements"

git add assets/architecture-mermaid.png assets/uml-diagram.png
git rm -f mermaid.png uml_final.png 2>/dev/null || true
git commit -m "Move diagrams into /assets/ for portfolio organization"

git add assets/walkthrough/ scripts/build_walkthrough.py
git commit -m "Add embedded walkthrough: 6 screenshots + animated GIF for end-to-end demo"

git add architecture.mmd README.md model_card.md COMMIT_PLAN.md SUBMISSION_CHECKLIST.md
# Catch any remaining changes (e.g. test_pawpal.py line-ending normalization)
git add -A
git commit -m "Rewrite README with embedded walkthrough, architecture diagram, eval stats; add model_card.md"

echo ""
echo "=== Recent commits ==="
git log --oneline -12

echo ""
echo "=== Pushing to GitHub ==="
git push origin main

echo ""
echo "DONE!"
echo "Open: https://github.com/chinenyeze49-sketch/ai110-module2show-pawpal-starter"
echo "Verify the README's walkthrough GIF renders, then submit the URL."
