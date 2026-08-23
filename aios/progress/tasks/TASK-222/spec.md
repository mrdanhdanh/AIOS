# TASK-222 — Japanese N5 Learning Website

## Objective
Build a static, offline-first website to help beginners learn JLPT N5 Japanese:
Hiragana, Katakana, vocabulary, grammar, and a self-quiz.

## Scope
- **In scope:** 4-tab single-page app (Chữ cái / Từ vựng / Ngữ pháp / Trắc nghiệm),
  pure HTML/CSS/JS, no build step, no backend — works by opening `index.html`.
- **Out of scope:** user accounts, audio pronunciation, server, persistence.

## Deliverables
- `implementation/index.html`
- `implementation/css/style.css`
- `implementation/js/data.js` (KANA, VOCAB, GRAMMAR datasets)
- `implementation/js/app.js` (tab switching, kana render, vocab search/filter, quiz)
- `implementation/test_website.py` (pytest smoke tests, integrated into AIOS suite)

## Acceptance Criteria
1. Site opens in a browser with 4 working tabs.
2. Hiragana + Katakana tables render (basic + dakuten + combinations).
3. Vocabulary table shows >=100 N5 words with search + topic filter.
4. Grammar section lists >=10 N5 patterns with JP/VN examples.
5. Quiz generates questions, scores, and gives feedback.
6. `pytest` smoke tests pass; no architecture violations in `implementation/`.

## Dependencies
None (standalone deliverable; no AIOS runtime dependency). The architecture gate
(Rule 3) is expected to trivially pass because `implementation/` contains only
static assets plus one pytest file with no forbidden imports.
