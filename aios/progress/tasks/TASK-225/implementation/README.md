# TASK-225 — N5 Japanese Learning Website (deliverable)

Static, offline-first Japanese N5 learning website (vanilla HTML/CSS/JS).

## Run
Open `index.html` directly, or serve locally:
```bash
python -m http.server 8000
# visit http://localhost:8000
```

## Structure
- `index.html` — SPA shell, 8 views
- `css/style.css` — responsive dark theme
- `js/data.js` — `N5_DATA` content + `buildQuizPool()`
- `js/app.js` — view navigation + quiz engine

## Sections
Hiragana · Katakana · Chào hỏi · Số đếm · Từ vựng · Ngữ pháp · Thẻ ghi nhớ (Flashcard + phát âm offline) · Kiểm tra (quiz)
