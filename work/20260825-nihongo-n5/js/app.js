// App logic: navigation, rendering, and quiz engine (vanilla JS, offline).

const App = (() => {
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));

  function renderKana(key) {
    const data = N5_DATA[key];
    let html = `<div class="card"><h2>${data.title}</h2><p class="desc">${data.desc}</p>`;
    data.groups.forEach(g => {
      html += `<div class="group-label">${g.label}</div><div class="grid">`;
      g.items.forEach(it => {
        html += `<div class="kana-cell" title="${it.roma}"><div class="jp">${it.jp}</div><div class="roma">${it.roma}</div></div>`;
      });
      html += `</div>`;
    });
    html += `</div>`;
    return html;
  }

  function renderTable(key) {
    const data = N5_DATA[key];
    let html = `<div class="card"><h2>${data.title}</h2><p class="desc">${data.desc}</p><table class="word-table"><thead><tr><th>Nhật</th><th>Romaji</th><th>Nghĩa</th></tr></thead><tbody>`;
    data.items.forEach(it => {
      html += `<tr><td class="jp">${it.jp}</td><td class="roma">${it.roma}</td><td>${it.vi}</td></tr>`;
    });
    html += `</tbody></table></div>`;
    return html;
  }

  function renderVocab() {
    const data = N5_DATA.vocabulary;
    let html = `<div class="card"><h2>${data.title}</h2><p class="desc">${data.desc}</p>`;
    data.groups.forEach(g => {
      html += `<div class="group-label">${g.label}</div><table class="word-table"><thead><tr><th>Nhật</th><th>Romaji</th><th>Nghĩa</th></tr></thead><tbody>`;
      g.items.forEach(it => {
        html += `<tr><td class="jp">${it.jp}</td><td class="roma">${it.roma}</td><td>${it.vi}</td></tr>`;
      });
      html += `</tbody></table>`;
    });
    html += `</div>`;
    return html;
  }

  function renderGrammar() {
    const data = N5_DATA.grammar;
    let html = `<div class="card"><h2>${data.title}</h2><p class="desc">${data.desc}</p>`;
    data.items.forEach(it => {
      html += `<div class="grammar-item"><div class="jp">${it.jp}</div><div class="roma">${it.roma}</div><div class="vi">${it.vi}</div><div class="note">${it.note}</div></div>`;
    });
    html += `</div>`;
    return html;
  }

  // ---- Quiz engine ----
  const quiz = {
    pool: [],
    current: null,
    options: [],
    score: 0,
    total: 0,
    answered: false
  };

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function nextQuestion() {
    quiz.answered = false;
    quiz.current = quiz.pool[Math.floor(Math.random() * quiz.pool.length)];
    const wrong = shuffle(quiz.pool.filter(p => p.a !== quiz.current.a)).slice(0, 3).map(p => p.a);
    quiz.options = shuffle([quiz.current.a, ...wrong]);
    renderQuiz();
  }

  function renderQuiz() {
    const box = $("#quiz-view");
    box.innerHTML = `
      <div class="card quiz-box">
        <div class="quiz-cat">${quiz.current.cat}</div>
        <div class="quiz-q">${quiz.current.q}</div>
        <div class="quiz-options">
          ${quiz.options.map(o => `<button data-opt="${o}">${o}</button>`).join("")}
        </div>
        <div class="quiz-meta">
          <span>Đúng: <span class="quiz-score" id="q-score">${quiz.score}</span> / ${quiz.total}</span>
          <span id="q-progress"></span>
        </div>
        <div class="quiz-feedback" id="q-feedback"></div>
        <button class="btn-primary" id="q-next">Câu tiếp theo →</button>
      </div>`;
    box.querySelectorAll(".quiz-options button").forEach(btn => {
      btn.addEventListener("click", () => onAnswer(btn));
    });
    $("#q-next").addEventListener("click", nextQuestion);
  }

  function onAnswer(btn) {
    if (quiz.answered) return;
    quiz.answered = true;
    quiz.total++;
    const chosen = btn.getAttribute("data-opt");
    const correct = chosen === quiz.current.a;
    if (correct) quiz.score++;
    btn.classList.add(correct ? "correct" : "wrong");
    if (!correct) {
      btn.parentElement.querySelectorAll("button").forEach(b => {
        if (b.getAttribute("data-opt") === quiz.current.a) b.classList.add("correct");
      });
    }
    const fb = $("#q-feedback");
    fb.textContent = correct ? "✅ Chính xác!" : `❌ Đáp án: ${quiz.current.a}`;
    fb.style.color = correct ? "var(--ok)" : "var(--bad)";
    $("#q-score").textContent = quiz.score;
  }

  function initQuiz() {
    quiz.pool = buildQuizPool();
    quiz.score = 0;
    quiz.total = 0;
    nextQuestion();
  }

  function showView(id) {
    $$("section.view").forEach(s => s.classList.remove("active"));
    $$("nav.tabs button").forEach(b => b.classList.toggle("active", b.dataset.view === id));
    const view = $("#" + id + "-view");
    if (!view) return;
    if (id === "quiz" && !view.dataset.init) {
      initQuiz();
      view.dataset.init = "1";
    }
    view.classList.add("active");
  }

  function init() {
    $("#hiragana-view").innerHTML = renderKana("hiragana");
    $("#katakana-view").innerHTML = renderKana("katakana");
    $("#greetings-view").innerHTML = renderTable("greetings");
    $("#numbers-view").innerHTML = renderTable("numbers");
    $("#vocab-view").innerHTML = renderVocab();
    $("#grammar-view").innerHTML = renderGrammar();

    $$("nav.tabs button").forEach(btn => {
      btn.addEventListener("click", () => showView(btn.dataset.view));
    });
    showView("home");
  }

  return { init };
})();

document.addEventListener("DOMContentLoaded", App.init);
