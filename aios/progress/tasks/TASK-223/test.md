# Test — TASK-223

## How the deliverable is verified

1. **AIOS build test** (`test_aios_builds_site_with_evidence`):
   - Calls `aios.tool.website.n5_builder.build_n5_site(tmp)`.
   - Asserts `index.html`, `js/data.js`, `js/app.js`, `build_evidence.json` exist.
   - Asserts `build_evidence.json.producer` starts with `aios` and has `content_hash`.
   - Asserts `vocab_count >= 100`, `grammar_count >= 10`.

2. **Real behavior harness** (`test_behavior_harness_runs`):
   - Builds the site into a temp dir, copies `harness_n5.js`, runs `node harness_n5.js`.
   - The Node harness asserts: VOCAB>=100, GRAMMAR>=10, `filterVocab('neko')`→mèo,
     topic filter, deterministic `generateQuiz`, 4 options/question, `scoreQuiz`
     all-correct=5 and wrong<5.
   - Exits non-zero on any failure (real verification, not string presence).

Run: `python -m pytest aios/progress/tasks/TASK-223/implementation/test_t223_aios_website.py -q`
