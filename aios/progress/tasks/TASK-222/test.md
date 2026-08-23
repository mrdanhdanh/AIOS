# Test — TASK-222

## Automated (pytest, part of the AIOS suite)
Run from the repo root:
```
python -m pytest aios/progress/tasks/TASK-222/implementation -q
```
Checks performed by `test_website.py`:
- `index.html` is present and wires `css/style.css`, `js/data.js`, `js/app.js`.
- `data.js` defines `KANA`, `VOCAB`, `GRAMMAR`.
- `VOCAB` has >=100 rows; `GRAMMAR` has >=10 patterns.
- `app.js` wires `renderKana` / `renderVocab` / `startQuiz` / `GRAMMAR`.

## Static analysis (JS)
```
node --check js/data.js && node --check js/app.js
```

## Manual (browser)
Open `implementation/index.html`; verify the 4 tabs, kana tables, vocab search,
grammar list, and a full quiz run with scoring + feedback.

## Governance gate
```
python aios/governance/cli/gate_check.py --task TASK-222
```
