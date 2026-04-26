# Submission checklist — PawPal+

Mapped 1:1 against the project spec's "Submitting Your Project" section.

| # | Spec requirement | Status | Evidence |
|---|---|---|---|
| 1 | Code is pushed to the correct GitHub repository | ⬜ Apply COMMIT_PLAN.md | `chinenyeze49-sketch/ai110-module2show-pawpal-starter` |
| 2 | Repo is public | ⬜ Verify in GitHub repo Settings → General → Danger Zone | — |
| 3 | Required files: `README.md`, `model_card.md`, architecture diagram | ✅ | `README.md`, `model_card.md`, `architecture.mmd` (also embedded in README) |
| 4 | Organized assets (`/assets/` folder with screenshots) | ✅ | `assets/architecture-mermaid.png`, `assets/uml-diagram.png`, `assets/walkthrough/*.png` |
| 5 | Commit history with meaningful messages | ⬜ Apply COMMIT_PLAN.md | 11-commit sequence in `COMMIT_PLAN.md` |
| 6 | Standardized documentation (README mentions base project, model_card answers reflection questions) | ✅ | README links to base project; `model_card.md` answers all 4 reflection questions |
| 7 | **Demo walkthrough included (Loom URL OR GIF/screenshot walkthrough showing 2–3 inputs + AI responses)** | ✅ | **Animated GIF + 6 screenshots embedded in README — covers end-to-end run, all 3 AI features, guardrail, and eval results** |
| 8 | Final changes committed and pushed before deadline | ⬜ Final step | — |

---

## Rubric coverage (Functionality / Architecture / Documentation / Reliability / Reflection)

| Rubric section | Where it's satisfied |
|---|---|
| **0. Project environment** | Public fork at `chinenyeze49-sketch/ai110-module2show-pawpal-starter`, README documents setup |
| **1. Functionality — does something useful** | Pet care planner: track tasks, generate daily plan, AI-explain plan |
| **1. AI feature (RAG/agent/etc.)** | `ai_assistant.py` — three features: plan explanation, task-suggestion agent, care Q&A; pluggable providers |
| **1. 2–3 inputs flow through end-to-end** | Demonstrated in `main.py`, the embedded walkthrough GIF, and the Streamlit tabs |
| **1. Reproducible, documented behavior** | Mock provider gives deterministic outputs; README sample interactions match `main.py` output |
| **1. Logging + error handling** | `logging_config.py`, all AI calls wrapped in try/except with fallback responses |
| **1. Setup steps documented** | README "Setup" section |
| **2. Design and architecture (UML/Mermaid)** | Mermaid diagram embedded in README; source in `architecture.mmd`; original UML in `assets/uml-diagram.png` |
| **3. Documentation — README quality** | README has project name, summary, architecture, setup, sample interactions, design decisions, testing, reflection link |
| **3. Demo walkthrough** | Animated GIF + 6 screenshots embedded directly in README |
| **4. Reliability — at least one summary stat** | `eval/run_eval.py` — overall accuracy + per-category accuracy + average confidence |
| **4. Tests** | 36 pytest tests across 3 files (was 10) |
| **4. Confidence scoring** | `score_confidence()` heuristic surfaced in CLI, UI, and eval report |
| **4. Human evaluation** | `eval/eval_set.json` is hand-curated; `model_card.md` §4.3 captures human observations during testing |
| **5. Reflection — limitations + biases** | `model_card.md` §4.1 |
| **5. Reflection — misuse + mitigation** | `model_card.md` §4.2 |
| **5. Reflection — what surprised you** | `model_card.md` §4.3 |
| **5. Reflection — helpful vs flawed AI suggestion** | `model_card.md` §4.4 |
| **6. (Optional) presentation / portfolio artifact** | Out of scope of this delivery |
