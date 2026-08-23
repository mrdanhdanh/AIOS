# Breakdown — TASK-222

1. Scaffold `implementation/` with `index.html` + `css/` + `js/` folders. ✅
2. Author `js/data.js`: KANA (hiragana/katakana, 3 groups each), VOCAB (>=100
   rows), GRAMMAR (>=10 patterns). ✅
3. Author `css/style.css`: layout, tabs, kana grid, vocab table, quiz, responsive
   breakpoint. ✅
4. Author `js/app.js`: tab navigation, kana render + switch, vocab search/filter,
   grammar render, quiz engine. ✅
5. Author `implementation/test_website.py`: pytest smoke tests (presence, asset
   wiring, data integrity). ✅
6. Verify: `node --check` on JS; `python -m pytest` on `test_website.py`. ✅
7. Run governance gate `gate_check.py --task TASK-222` (lifecycle + architecture
   + CI). ⏳
