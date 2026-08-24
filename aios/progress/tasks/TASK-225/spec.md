# TASK-225 — N5 Japanese Learning Website

## Objective
Build a static, offline-first Japanese N5 learning website (vanilla HTML/CSS/JS,
no external dependencies) covering Hiragana, Katakana, greetings, numbers,
vocabulary, grammar, and a multiple-choice quiz engine.

## Scope
In scope: 7 content sections, responsive dark-theme UI, offline operation,
client-side quiz with scoring.
Out of scope: backend, user accounts, LLM integration, hosting/deployment.

## Deliverables
- `index.html` — SPA shell with 8 views (home + 7 sections)
- `css/style.css` — responsive styling
- `js/data.js` — `N5_DATA` content + `buildQuizPool()`
- `js/app.js` — view navigation + quiz engine
- `README.md` — run instructions

## Acceptance Criteria
- AC1: All 5 deliverable files exist and are non-empty.
- AC2: `index.html` links `css/style.css`, `js/data.js`, `js/app.js` and defines 8 sections.
- AC3: `data.js` defines `N5_DATA` with >100 entries and `buildQuizPool()`.
- AC4: `app.js` implements `showView` navigation and a quiz engine (`nextQuestion`).

## Dependencies
- None (standalone deliverable).

## Governance references
- Rule 1..7 satisfied via `aios/governance/*` (lifecycle, architecture, registry,
  dependency, evidence, deterministic, regression).
