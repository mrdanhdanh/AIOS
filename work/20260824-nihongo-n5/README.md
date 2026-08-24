# Nhật N5 — Website học tiếng Nhật sơ cấp (JLPT N5)

Website tĩnh, **offline-first**, không cần build. Mở trực tiếp `site/index.html`
hoặc chạy dev server.

## Cấu trúc dự án
- `generate_site.py` — sinh trang (deterministic, KHÔNG dùng LLM)
- `governance_check.py` — validation gate (đầy đủ + xác thực nội dung)
- `site/` — đầu ra tĩnh
  - `index.html`, `hiragana.html`, `katakana.html`, `vocab.html`,
    `grammar.html`, `kanji.html`, `quiz.html`
  - `assets/style.css`, `assets/data.js`, `assets/app.js`
- `.github/instructions/nihongo-n5.instructions.md` — hướng dẫn dự án

## Lệnh
```powershell
python generate_site.py      # sinh lại site/
python serve.py             # dev server http://localhost:8000
python governance_check.py  # chạy governance gate
```

## Nội dung
Hiragana, Katakana, ~130 từ vựng N5, ~27 ngữ pháp, ~102 Kanji,
và trắc nghiệm đa dạng (5 dạng câu hỏi, đáp án random, xáo trộn).
