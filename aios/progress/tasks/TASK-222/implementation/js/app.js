// Logic ứng dụng học tiếng Nhật N5
(function () {
  "use strict";

  /* ---------- Tabs ---------- */
  const tabs = document.querySelectorAll(".tab");
  const panels = document.querySelectorAll(".panel");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      panels.forEach((p) => p.classList.remove("active"));
      tab.classList.add("active");
      document.getElementById(tab.dataset.tab).classList.add("active");
    });
  });

  /* ---------- Kana ---------- */
  const kanaContainer = document.getElementById("kanaContainer");
  const kbtns = document.querySelectorAll(".kbtn");
  function renderKana(type) {
    const data = KANA[type];
    let html = "";
    data.groups.forEach((g) => {
      html += `<div class="kana-group"><h3>${g.label}</h3><div class="kana-grid">`;
      g.items.forEach(([char, romaji]) => {
        html += `<div class="kana-cell"><div class="kana-char">${char}</div><div class="kana-romaji">${romaji}</div></div>`;
      });
      html += `</div></div>`;
    });
    kanaContainer.innerHTML = html;
  }
  kbtns.forEach((b) => {
    b.addEventListener("click", () => {
      kbtns.forEach((x) => x.classList.remove("active"));
      b.classList.add("active");
      renderKana(b.dataset.kana);
    });
  });
  renderKana("hiragana");

  /* ---------- Vocab ---------- */
  const vocabBody = document.getElementById("vocabBody");
  const vocabSearch = document.getElementById("vocabSearch");
  const vocabFilter = document.getElementById("vocabFilter");
  const vocabCount = document.getElementById("vocabCount");

  // populate filter
  const topics = [...new Set(VOCAB.map((v) => v[3]))].sort();
  topics.forEach((t) => {
    const opt = document.createElement("option");
    opt.value = t; opt.textContent = t;
    vocabFilter.appendChild(opt);
  });

  function renderVocab() {
    const q = vocabSearch.value.trim().toLowerCase();
    const f = vocabFilter.value;
    const rows = VOCAB.filter(([jp, rom, vn, topic]) => {
      if (f && topic !== f) return false;
      if (!q) return true;
      return (jp + " " + rom + " " + vn + " " + topic).toLowerCase().includes(q);
    });
    vocabBody.innerHTML = rows
      .map(
        ([jp, rom, vn, topic]) =>
          `<tr><td class="vocab-jp">${jp}</td><td>${rom}</td><td>${vn}</td><td><span class="tag">${topic}</span></td></tr>`
      )
      .join("");
    vocabCount.textContent = `Hiển thị ${rows.length} / ${VOCAB.length} từ`;
  }
  vocabSearch.addEventListener("input", renderVocab);
  vocabFilter.addEventListener("change", renderVocab);
  renderVocab();

  /* ---------- Grammar ---------- */
  const grammarList = document.getElementById("grammarList");
  grammarList.innerHTML = GRAMMAR.map(
    (g) => `
    <div class="grammar-card">
      <div class="pat">${g.pattern}</div>
      <div class="mean">${g.meaning}</div>
      <div class="ex-jp">🇯🇵 ${g.example_jp}</div>
      <div class="ex-vn">🇻🇳 ${g.example_vn}</div>
    </div>`
  ).join("");

  /* ---------- Quiz ---------- */
  const quizQuestion = document.getElementById("quizQuestion");
  const quizOptions = document.getElementById("quizOptions");
  const quizFeedback = document.getElementById("quizFeedback");
  const quizProgress = document.getElementById("quizProgress");
  const quizScore = document.getElementById("quizScore");
  const quizNext = document.getElementById("quizNext");
  const quizRestart = document.getElementById("quizRestart");

  let questions = [];
  let current = 0;
  let score = 0;
  let answered = false;

  function buildQuestions() {
    const q = [];
    // Dạng: chọn nghĩa tiếng Việt từ từ vựng
    VOCAB.slice(0, 40).forEach(([jp, rom, vn]) => {
      const wrong = VOCAB.filter((x) => x[2] !== vn)
        .map((x) => x[2])
        .sort(() => Math.random() - 0.5)
        .slice(0, 3);
      q.push({
        q: `${jp} (${rom})`,
        options: shuffle([vn, ...wrong]),
        answer: vn,
        type: "vn",
      });
    });
    // Dạng: chọn romaji từ kana
    KANA.hiragana.groups[0].items.slice(0, 20).forEach(([char, rom]) => {
      const wrong = KANA.hiragana.groups[0].items
        .filter((x) => x[1] !== rom)
        .map((x) => x[1])
        .sort(() => Math.random() - 0.5)
        .slice(0, 3);
      q.push({
        q: `Cách đọc của ${char} là?`,
        options: shuffle([rom, ...wrong]),
        answer: rom,
        type: "rom",
      });
    });
    return shuffle(q);
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function startQuiz() {
    questions = buildQuestions();
    current = 0;
    score = 0;
    answered = false;
    quizScore.textContent = "Điểm: 0";
    renderQuestion();
  }

  function renderQuestion() {
    answered = false;
    quizNext.disabled = true;
    quizFeedback.textContent = "";
    const item = questions[current];
    quizQuestion.textContent = item.q;
    quizProgress.textContent = `Câu ${current + 1}/${questions.length}`;
    quizOptions.innerHTML = "";
    item.options.forEach((opt) => {
      const btn = document.createElement("button");
      btn.className = "quiz-opt";
      btn.textContent = opt;
      btn.addEventListener("click", () => selectOption(btn, opt, item.answer));
      quizOptions.appendChild(btn);
    });
  }

  function selectOption(btn, choice, answer) {
    if (answered) return;
    answered = true;
    const all = quizOptions.querySelectorAll(".quiz-opt");
    all.forEach((b) => (b.disabled = true));
    if (choice === answer) {
      btn.classList.add("correct");
      score++;
      quizScore.textContent = "Điểm: " + score;
      quizFeedback.textContent = "✅ Chính xác!";
      quizFeedback.style.color = "#1f7a47";
    } else {
      btn.classList.add("wrong");
      all.forEach((b) => {
        if (b.textContent === answer) b.classList.add("correct");
      });
      quizFeedback.textContent = "❌ Sai rồi. Đáp án đúng: " + answer;
      quizFeedback.style.color = "#b83232";
    }
    quizNext.disabled = false;
  }

  quizNext.addEventListener("click", () => {
    if (current < questions.length - 1) {
      current++;
      renderQuestion();
    } else {
      quizQuestion.textContent = "🎉 Hoàn thành!";
      quizOptions.innerHTML = "";
      quizFeedback.textContent = `Kết quả: ${score}/${questions.length} câu đúng.`;
      quizFeedback.style.color = "var(--accent)";
      quizProgress.textContent = "Xong";
      quizNext.disabled = true;
    }
  });
  quizRestart.addEventListener("click", startQuiz);

  startQuiz();

  /* ---------- Theme toggle (ui-ux-pro-max: dark mode) ---------- */
  const themeToggle = document.getElementById("themeToggle");
  const themeLabel = document.getElementById("themeLabel");
  const root = document.documentElement;
  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    themeLabel.textContent = theme === "dark" ? "Sáng" : "Tối";
    themeToggle.firstChild.textContent = theme === "dark" ? "☀️ " : "🌙 ";
    try { localStorage.setItem("n5-theme", theme); } catch (e) {}
  }
  const saved = (function () {
    try { return localStorage.getItem("n5-theme"); } catch (e) { return null; }
  })();
  if (saved) applyTheme(saved);
  else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) applyTheme("dark");
  themeToggle.addEventListener("click", () => {
    applyTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
  });
})();
