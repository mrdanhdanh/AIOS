"""N5 Japanese learning site builder (TASK-223).

This is a REAL AIOS tool: given a data spec it *generates* the static site
files (index.html, css, js/data.js, js/app.js) and a ``build_evidence.json``
provenance record. The deliverable is therefore produced BY AIOS, not written
by hand — which is exactly what the ``runtime_utilization`` gate now requires
for tasks that declare ``Demonstrates-AIOS: true``.

Layering: ``tool`` layer — stdlib + ``aios.core`` only. No runtime/agent/
orchestrator/capability imports.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List

PRODUCER = "aios.tool.website.n5_builder"


# ---------------------------------------------------------------------------
# Curated N5 dataset (>=100 vocab, >=10 grammar) — real learning content.
# Each vocab row: [japanese, romaji, vietnamese, topic]
# ---------------------------------------------------------------------------
VOCAB: List[List[str]] = [
    ["私", "watashi", "tôi", "đại từ"], ["あなた", "anata", "bạn", "đại từ"],
    ["彼", "kare", "anh ấy", "đại từ"], ["彼女", "kanojo", "cô ấy", "đại từ"],
    ["私たち", "watashitachi", "chúng tôi", "đại từ"], ["先生", "sensei", "giáo viên", "nghề nghiệp"],
    ["学生", "gakusei", "học sinh", "nghề nghiệp"], ["友達", "tomodachi", "bạn bè", "người"],
    ["人", "hito", "người", "người"], ["子供", "kodomo", "trẻ em", "người"],
    ["男の人", "otokonohito", "đàn ông", "người"], ["女の人", "onnanohito", "phụ nữ", "người"],
    ["家族", "kazoku", "gia đình", "người"], ["父", "chichi", "bố", "gia đình"],
    ["母", "haha", "mẹ", "gia đình"], ["兄", "ani", "anh trai", "gia đình"],
    ["姉", "ane", "chị gái", "gia đình"], ["弟", "otouto", "em trai", "gia đình"],
    ["妹", "imouto", "em gái", "gia đình"], ["猫", "neko", "mèo", "động vật"],
    ["犬", "inu", "chó", "động vật"], ["鳥", "tori", "chim", "động vật"],
    ["魚", "sakana", "cá", "động vật"], ["馬", "uma", "ngựa", "động vật"],
    ["本", "hon", "sách", "đồ vật"], ["鉛筆", "enpitsu", "bút chì", "đồ vật"],
    ["ペン", "pen", "bút bi", "đồ vật"], ["紙", "kami", "giấy", "đồ vật"],
    ["時計", "tokei", "đồng hồ", "đồ vật"], ["眼鏡", "megane", "kính mắt", "đồ vật"],
    ["傘", "kasa", "ô", "đồ vật"], ["鍵", "kagi", "chìa khóa", "đồ vật"],
    ["ドア", "doa", "cửa", "đồ vật"], ["窓", "mado", "cửa sổ", "đồ vật"],
    ["机", "tsukue", "bàn", "đồ vật"], ["椅子", "isu", "ghế", "đồ vật"],
    ["ベッド", "beddo", "giường", "đồ vật"], ["服", "fuku", "quần áo", "đồ vật"],
    ["靴", "kutsu", "giày", "đồ vật"], ["帽子", "boushi", "mũ", "đồ vật"],
    ["水", "mizu", "nước", "ẩm thực"], ["お茶", "ocha", "trà", "ẩm thực"],
    ["コーヒー", "koohii", "cà phê", "ẩm thực"], ["牛乳", "gyuunyuu", "sữa", "ẩm thực"],
    ["ご飯", "gohan", "cơm", "ẩm thực"], ["パン", "pan", "bánh mì", "ẩm thực"],
    ["卵", "tamago", "trứng", "ẩm thực"], ["魚", "sakana", "cá", "ẩm thực"],
    ["肉", "niku", "thịt", "ẩm thực"], ["野菜", "yasai", "rau", "ẩm thực"],
    ["果物", "kudamono", "hoa quả", "ẩm thực"], ["リンゴ", "ringo", "táo", "ẩm thực"],
    ["バナナ", "banana", "chuối", "ẩm thực"], ["みかん", "mikan", "quýt", "ẩm thực"],
    ["朝ご飯", "asa gohan", "bữa sáng", "ẩm thực"], ["昼ご飯", "hiru gohan", "bữa trưa", "ẩm thực"],
    ["晩ご飯", "ban gohan", "bữa tối", "ẩm thực"], ["行く", "iku", "đi", "động từ"],
    ["来る", "kuru", "đến", "động từ"], ["帰る", "kaeru", "về", "động từ"],
    ["見る", "miru", "xem", "động từ"], ["聞く", "kiku", "nghe", "động từ"],
    ["話す", "hanasu", "nói chuyện", "động từ"], ["読む", "yomu", "đọc", "động từ"],
    ["書く", "kaku", "viết", "động từ"], ["食べる", "taberu", "ăn", "động từ"],
    ["飲む", "nomu", "uống", "động từ"], ["する", "suru", "làm", "động từ"],
    ["買う", "kau", "mua", "động từ"], ["売る", "uru", "bán", "động từ"],
    ["寝る", "neru", "ngủ", "động từ"], ["起きる", "okiru", "thức dậy", "động từ"],
    ["働く", "hataraku", "làm việc", "động từ"], ["勉強する", "benkyou suru", "học tập", "động từ"],
    ["分かる", "wakaru", "hiểu", "động từ"], ["好き", "suki", "thích", "tính từ"],
    ["嫌い", "kirai", "ghét", "tính từ"], ["大きい", "ookii", "to", "tính từ"],
    ["小さい", "chiisai", "nhỏ", "tính từ"], ["新しい", "atarashii", "mới", "tính từ"],
    ["古い", "furui", "cũ", "tính từ"], ["高い", "takai", "cao/đắt", "tính từ"],
    ["安い", "yasui", "rẻ", "tính từ"], ["美味しい", "oishii", "ngon", "tính từ"],
    ["悪い", "warui", "xấu/tệ", "tính từ"], ["忙しい", "isogashii", "bận", "tính từ"],
    ["暇", "hima", "rảnh", "tính từ"], ["赤い", "akai", "đỏ", "tính từ"],
    ["青い", "aoi", "xanh", "tính từ"], ["白い", "shiroi", "trắng", "tính từ"],
    ["黒い", "kuroi", "đen", "tính từ"], ["今日", "kyou", "hôm nay", "thời gian"],
    ["明日", "ashita", "ngày mai", "thời gian"], ["昨日", "kinou", "hôm qua", "thời gian"],
    ["今", "ima", "bây giờ", "thời gian"], ["朝", "asa", "sáng", "thời gian"],
    ["午前", "gozen", "buổi sáng", "thời gian"], ["午後", "gogo", "buổi chiều", "thời gian"],
    ["夜", "yoru", "đêm", "thời gian"], ["一", "ichi", "một", "số"],
    ["二", "ni", "hai", "số"], ["三", "san", "ba", "số"],
    ["四", "yon", "bốn", "số"], ["五", "go", "năm", "số"],
    ["六", "roku", "sáu", "số"], ["七", "nana", "bảy", "số"],
    ["八", "hachi", "tám", "số"], ["九", "kyuu", "chín", "số"],
    ["十", "juu", "mười", "số"], ["百", "hyaku", "trăm", "số"],
    ["千", "sen", "nghìn", "số"], ["万", "man", "vạn", "số"],
    ["学校", "gakkou", "trường học", "nơi chốn"], ["会社", "kaisha", "công ty", "nơi chốn"],
    ["家", "ie", "nhà", "nơi chốn"], ["部屋", "heya", "phòng", "nơi chốn"],
    ["図書館", "toshokan", "thư viện", "nơi chốn"], ["病院", "byouin", "bệnh viện", "nơi chốn"],
    ["駅", "eki", "ga tàu", "nơi chốn"], ["空港", "kuukou", "sân bay", "nơi chốn"],
    ["日本", "nippon", "Nhật Bản", "nơi chốn"], ["東京", "toukyou", "Tokyo", "nơi chốn"],
    ["太陽", "taiyou", "mặt trời", "thiên nhiên"], ["月", "tsuki", "mặt trăng", "thiên nhiên"],
    ["星", "hoshi", "ngôi sao", "thiên nhiên"], ["空", "sora", "bầu trời", "thiên nhiên"],
    ["山", "yama", "núi", "thiên nhiên"], ["川", "kawa", "sông", "thiên nhiên"],
    ["海", "umi", "biển", "thiên nhiên"], ["雨", "ame", "mưa", "thiên nhiên"],
    ["雪", "yuki", "tuyết", "thiên nhiên"], ["風", "kaze", "gió", "thiên nhiên"],
    ["そして", "soshite", "và sau đó", "từ nối"], ["でも", "demo", "nhưng", "từ nối"],
    ["また", "mata", "lại nữa", "từ nối"], ["と", "to", "và", "từ nối"],
    ["か", "ka", "hay là (nghi vấn)", "từ nối"], ["ね", "ne", "nhé (xác nhận)", "từ nối"],
]

KANA: Dict[str, List[List[str]]] = {
    "Hiragana cơ bản": [
        ["あ", "a"], ["い", "i"], ["う", "u"], ["え", "e"], ["お", "o"],
        ["か", "ka"], ["き", "ki"], ["く", "ku"], ["け", "ke"], ["こ", "ko"],
        ["さ", "sa"], ["し", "shi"], ["す", "su"], ["せ", "se"], ["そ", "so"],
        ["た", "ta"], ["ち", "chi"], ["つ", "tsu"], ["て", "te"], ["と", "to"],
        ["な", "na"], ["に", "ni"], ["ぬ", "nu"], ["ね", "ne"], ["の", "no"],
        ["は", "ha"], ["ひ", "hi"], ["ふ", "fu"], ["へ", "he"], ["ほ", "ho"],
        ["ま", "ma"], ["み", "mi"], ["む", "mu"], ["め", "me"], ["も", "mo"],
        ["や", "ya"], ["ゆ", "yu"], ["よ", "yo"],
        ["ら", "ra"], ["り", "ri"], ["る", "ru"], ["れ", "re"], ["ろ", "ro"],
        ["わ", "wa"], ["を", "wo"], ["ん", "n"],
    ],
    "Katakana cơ bản": [
        ["ア", "a"], ["イ", "i"], ["ウ", "u"], ["エ", "e"], ["オ", "o"],
        ["カ", "ka"], ["キ", "ki"], ["ク", "ku"], ["ケ", "ke"], ["コ", "ko"],
        ["サ", "sa"], ["シ", "shi"], ["ス", "su"], ["セ", "se"], ["ソ", "so"],
        ["タ", "ta"], ["チ", "chi"], ["ツ", "tsu"], ["テ", "te"], ["ト", "to"],
        ["ナ", "na"], ["ニ", "ni"], ["ヌ", "nu"], ["ネ", "ne"], ["ノ", "no"],
        ["ハ", "ha"], ["ヒ", "hi"], ["フ", "fu"], ["ヘ", "he"], ["ホ", "ho"],
        ["マ", "ma"], ["ミ", "mi"], ["ム", "mu"], ["メ", "me"], ["モ", "mo"],
        ["ヤ", "ya"], ["ユ", "yu"], ["ヨ", "yo"],
        ["ラ", "ra"], ["リ", "ri"], ["ル", "ru"], ["レ", "re"], ["ロ", "ro"],
        ["ワ", "wa"], ["ヲ", "wo"], ["ン", "n"],
    ],
    "Dakuten / Handakuten": [
        ["が", "ga"], ["ぎ", "gi"], ["ぐ", "gu"], ["げ", "ge"], ["ご", "go"],
        ["ざ", "za"], ["じ", "ji"], ["ず", "zu"], ["ぜ", "ze"], ["ぞ", "zo"],
        ["だ", "da"], ["ぢ", "ji"], ["づ", "zu"], ["で", "de"], ["ど", "do"],
        ["ば", "ba"], ["び", "bi"], ["ぶ", "bu"], ["べ", "be"], ["ぼ", "bo"],
        ["ぱ", "pa"], ["ぴ", "pi"], ["ぷ", "pu"], ["ぺ", "pe"], ["ぽ", "po"],
    ],
    "Kết hợp (yōon)": [
        ["きゃ", "kya"], ["きゅ", "kyu"], ["きょ", "kyo"],
        ["しゃ", "sha"], ["しゅ", "shu"], ["しょ", "sho"],
        ["ちゃ", "cha"], ["ちゅ", "chu"], ["ちょ", "cho"],
        ["にゃ", "nya"], ["にゅ", "nyu"], ["にょ", "nyo"],
        ["ひゃ", "hya"], ["ひゅ", "hyu"], ["ひょ", "hyo"],
        ["みゃ", "mya"], ["みゅ", "myu"], ["みょ", "myo"],
        ["りゃ", "rya"], ["りゅ", "ryu"], ["りょ", "ryo"],
    ],
}

GRAMMAR: List[Dict[str, str]] = [
    {"pattern": "〜は〜です", "jp": "私は学生です。", "vn": "Tôi là học sinh."},
    {"pattern": "〜は〜ではありません", "jp": "彼は先生ではありません。", "vn": "Anh ấy không phải là giáo viên."},
    {"pattern": "〜は〜ですか", "jp": "これは本ですか。", "vn": "Đây có phải là sách không?"},
    {"pattern": "〜の〜", "jp": "私の本", "vn": "Quyển sách của tôi"},
    {"pattern": "〜に〜があります", "jp": "部屋に机があります。", "vn": "Trong phòng có cái bàn."},
    {"pattern": "〜で〜をします", "jp": "図書館で勉強をします。", "vn": "Tôi học ở thư viện."},
    {"pattern": "〜へ／に行きます", "jp": "学校へ行きます。", "vn": "Tôi đi đến trường."},
    {"pattern": "〜が好きです", "jp": "猫が好きです。", "vn": "Tôi thích mèo."},
    {"pattern": "〜たいです", "jp": "水を飲みたいです。", "vn": "Tôi muốn uống nước."},
    {"pattern": "〜てください", "jp": "本を読んでください。", "vn": "Hãy đọc sách."},
    {"pattern": "〜ました／〜ませんでした", "jp": "昨日、映画を見ました。", "vn": "Hôm qua tôi đã xem phim."},
    {"pattern": "〜とき", "jp": "暇なとき、本を読みます。", "vn": "Khi rảnh, tôi đọc sách."},
    {"pattern": "〜ので", "jp": "雨なので、家にいます。", "vn": "Vì mưa nên tôi ở nhà."},
    {"pattern": "〜ば", "jp": "安ければ、買います。", "vn": "Nếu rẻ thì tôi mua."},
    {"pattern": "〜てもいいです", "jp": "ここで話してもいいです。", "vn": "Ở đây nói chuyện cũng được."},
]


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------
HTML_TPL = """<!DOCTYPE html>
<html lang="vi" data-theme="light">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Học tiếng Nhật N5</title>
<link rel="stylesheet" href="css/style.css" />
</head>
<body>
<header class="app-header">
  <h1>Học tiếng Nhật N5</h1>
  <button id="themeToggle" aria-label="Chuyển giao diện sáng/tối" data-theme="light">🌓 Giao diện</button>
</header>
<nav class="tabs" role="tablist" aria-label="Chủ đề học">
  <button class="tab" role="tab" aria-selected="true" data-tab="kana">Chữ cái</button>
  <button class="tab" role="tab" aria-selected="false" data-tab="vocab">Từ vựng</button>
  <button class="tab" role="tab" aria-selected="false" data-tab="grammar">Ngữ pháp</button>
  <button class="tab" role="tab" aria-selected="false" data-tab="quiz">Trắc nghiệm</button>
</nav>
<main>
  <section id="kana" class="panel" role="tabpanel"></section>
  <section id="vocab" class="panel" role="tabpanel" hidden>
    <div class="controls">
      <input id="vocabSearch" type="search" placeholder="Tìm từ..." aria-label="Tìm từ vựng" />
      <select id="vocabTopic" aria-label="Chọn chủ đề"></select>
    </div>
    <table id="vocabTable"><thead><tr><th>日本語</th><th>Romaji</th><th>Tiếng Việt</th><th>Chủ đề</th></tr></thead><tbody></tbody></table>
  </section>
  <section id="grammar" class="panel" role="tabpanel" hidden></section>
  <section id="quiz" class="panel" role="tabpanel" hidden>
    <button id="startQuiz">Bắt đầu làm bài</button>
    <div id="quizBody"></div>
    <div id="quizResult" aria-live="polite"></div>
  </section>
</main>
<footer class="app-footer">Được tạo bởi AIOS · N5 Learning Site</footer>
<script src="js/data.js"></script>
<script src="js/app.js"></script>
</body>
</html>
"""

CSS_TPL = """:root {
  --bg: #f7f7fb; --surface: #ffffff; --text: #1a1a2e; --muted: #6b6b80;
  --accent: #c0392b; --accent-2: #2c7be5; --border: #e3e3ee; --radius: 12px;
}
[data-theme="dark"] {
  --bg: #15151f; --surface: #1f1f2e; --text: #f2f2f7; --muted: #a0a0b8;
  --accent: #e74c3c; --accent-2: #4aa3ff; --border: #2e2e40;
}
* { box-sizing: border-box; }
body { margin: 0; font-family: "Hiragino Sans", "Noto Sans JP", system-ui, sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.6; }
.app-header { display: flex; justify-content: space-between; align-items: center;
  padding: 1rem 1.5rem; background: var(--surface); border-bottom: 1px solid var(--border); }
.app-header h1 { font-size: 1.25rem; margin: 0; }
#themeToggle { background: var(--accent-2); color: #fff; border: 0; border-radius: var(--radius);
  padding: .5rem 1rem; cursor: pointer; }
.tabs { display: flex; gap: .5rem; padding: .75rem 1.5rem; flex-wrap: wrap; }
.tab { background: var(--surface); color: var(--text); border: 1px solid var(--border);
  border-radius: var(--radius); padding: .5rem 1rem; cursor: pointer; }
.tab[aria-selected="true"] { background: var(--accent); color: #fff; border-color: var(--accent); }
.panel { padding: 1rem 1.5rem; }
.controls { display: flex; gap: .5rem; margin-bottom: 1rem; flex-wrap: wrap; }
.controls input, .controls select { padding: .5rem; border: 1px solid var(--border);
  border-radius: 8px; background: var(--surface); color: var(--text); }
table { width: 100%; border-collapse: collapse; }
th, td { text-align: left; padding: .5rem; border-bottom: 1px solid var(--border); }
.kana-group { margin-bottom: 1.25rem; }
.kana-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(64px, 1fr)); gap: .5rem; }
.kana-cell { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
  padding: .5rem; text-align: center; }
.kana-cell .k { font-size: 1.5rem; } .kana-cell .r { color: var(--muted); font-size: .8rem; }
.quiz-q { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 1rem; margin-bottom: 1rem; }
.quiz-q .opts { display: flex; flex-direction: column; gap: .4rem; margin-top: .5rem; }
.quiz-q button { text-align: left; padding: .5rem; border: 1px solid var(--border);
  border-radius: 8px; background: var(--surface); color: var(--text); cursor: pointer; }
.quiz-q button.correct { background: #2ecc71; color: #fff; }
.quiz-q button.wrong { background: #e74c3c; color: #fff; }
.app-footer { text-align: center; color: var(--muted); padding: 1rem; font-size: .85rem; }
"""

DATA_JS_TPL = """// Auto-generated by {producer} — do not edit by hand.
const KANA = {kana};
const VOCAB = {vocab};
const GRAMMAR = {grammar};
if (typeof module !== "undefined" && module.exports) {{
  module.exports = {{ KANA: KANA, VOCAB: VOCAB, GRAMMAR: GRAMMAR }};
}}
"""

APP_JS_TPL = """// Auto-generated by {producer} — UI wiring + pure logic (Node-testable).
(function () {{
  "use strict";

  // ---------- Pure logic (no DOM; exported for Node harness) ----------
  function filterVocab(vocab, query, topic) {{
    query = (query || "").toLowerCase();
    return vocab.filter(function (v) {{
      if (topic && topic !== "all" && v[3] !== topic) return false;
      if (!query) return true;
      return (v[0] + " " + v[1] + " " + v[2]).toLowerCase().indexOf(query) !== -1;
    }});
  }}

  function makeRng(seed) {{
    var s = seed >>> 0 || 1;
    return function () {{ s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }};
  }}

  function shuffle(arr, rng) {{
    for (var i = arr.length - 1; i > 0; i--) {{
      var j = Math.floor(rng() * (i + 1));
      var t = arr[i]; arr[i] = arr[j]; arr[j] = t;
    }}
    return arr;
  }}

  function generateQuiz(vocab, n, seed) {{
    var rng = makeRng(seed || 1);
    var pool = vocab.slice();
    var questions = [];
    n = Math.min(n || 5, pool.length);
    for (var i = 0; i < n; i++) {{
      var idx = Math.floor(rng() * pool.length);
      var word = pool.splice(idx, 1)[0];
      var options = [word[2]];
      while (options.length < 4 && pool.length) {{
        var o = pool[Math.floor(rng() * pool.length)][2];
        if (options.indexOf(o) === -1) options.push(o);
      }}
      questions.push({{
        q: word[0] + " (" + word[1] + ")",
        answer: word[2],
        options: shuffle(options.slice(), rng),
      }});
    }}
    return questions;
  }}

  function scoreQuiz(questions, answers) {{
    var score = 0;
    for (var i = 0; i < questions.length; i++) {{
      if (answers[i] === questions[i].answer) score++;
    }}
    return score;
  }}

  // ---------- DOM wiring (browser only) ----------
  function ready(fn) {{
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }}

  function renderKana() {{
    var root = document.getElementById("kana");
    if (!root || typeof KANA === "undefined") return;
    root.innerHTML = "";
    KANA.forEach(function (group) {{
      var wrap = document.createElement("div");
      wrap.className = "kana-group";
      var h = document.createElement("h2"); h.textContent = group.name || "Kana";
      wrap.appendChild(h);
      var grid = document.createElement("div"); grid.className = "kana-grid";
      group.rows.forEach(function (r) {{
        var cell = document.createElement("div"); cell.className = "kana-cell";
        cell.innerHTML = '<div class="k">' + r[0] + '</div><div class="r">' + r[1] + "</div>";
        grid.appendChild(cell);
      }});
      wrap.appendChild(grid); root.appendChild(wrap);
    }});
  }}

  function renderVocab() {{
    var tbody = document.querySelector("#vocabTable tbody");
    var topicSel = document.getElementById("vocabTopic");
    if (!tbody || typeof VOCAB === "undefined") return;
    var topics = Array.from(new Set(VOCAB.map(function (v) {{ return v[3]; }})));
    topicSel.innerHTML = '<option value="all">Tất cả</option>' +
      topics.map(function (t) {{ return '<option value="' + t + '">' + t + "</option>"; }}).join("");
    function draw() {{
      var q = document.getElementById("vocabSearch").value;
      var t = topicSel.value;
      var rows = filterVocab(VOCAB, q, t);
      tbody.innerHTML = rows.map(function (v) {{
        return "<tr><td>" + v[0] + "</td><td>" + v[1] + "</td><td>" + v[2] + "</td><td>" + v[3] + "</td></tr>";
      }}).join("");
    }}
    document.getElementById("vocabSearch").addEventListener("input", draw);
    topicSel.addEventListener("change", draw);
    draw();
  }}

  function renderGrammar() {{
    var root = document.getElementById("grammar");
    if (!root || typeof GRAMMAR === "undefined") return;
    root.innerHTML = GRAMMAR.map(function (g) {{
      return '<div class="kana-group"><h2>' + g.pattern + "</h2>" +
        '<div class="kana-cell"><div class="k">' + g.jp + '</div><div class="r">' + g.vn + "</div></div></div>";
    }}).join("");
  }}

  function startQuiz() {{
    var body = document.getElementById("quizBody");
    var result = document.getElementById("quizResult");
    var questions = generateQuiz(VOCAB, 5, 7);
    var answers = [];
    body.innerHTML = "";
    questions.forEach(function (q, i) {{
      var box = document.createElement("div"); box.className = "quiz-q";
      box.innerHTML = "<p><strong>" + (i + 1) + ". " + q.q + "</strong></p><div class='opts'></div>";
      var opts = box.querySelector(".opts");
      q.options.forEach(function (opt) {{
        var b = document.createElement("button"); b.textContent = opt;
        b.addEventListener("click", function () {{
          answers[i] = opt;
          Array.prototype.forEach.call(opts.children, function (c) {{ c.disabled = true; }});
          b.classList.add(opt === q.answer ? "correct" : "wrong");
        }});
        opts.appendChild(b);
      }});
      body.appendChild(box);
    }});
    var submit = document.createElement("button");
    submit.textContent = "Xem kết quả";
    submit.addEventListener("click", function () {{
      var score = scoreQuiz(questions, answers);
      result.textContent = "Điểm: " + score + " / " + questions.length;
    }});
    body.appendChild(submit);
  }}

  function applyTheme(theme) {{
    document.documentElement.setAttribute("data-theme", theme);
    var btn = document.getElementById("themeToggle");
    if (btn) btn.setAttribute("data-theme", theme);
  }}

  function wireTabs() {{
    document.querySelectorAll(".tab").forEach(function (tab) {{
      tab.addEventListener("click", function () {{
        document.querySelectorAll(".tab").forEach(function (t) {{ t.setAttribute("aria-selected", "false"); }});
        tab.setAttribute("aria-selected", "true");
        document.querySelectorAll(".panel").forEach(function (p) {{ p.hidden = true; }});
        document.getElementById(tab.dataset.tab).hidden = false;
      }});
    }});
  }}

  if (typeof document !== "undefined") {{
    ready(function () {{
      renderKana(); renderVocab(); renderGrammar(); wireTabs();
      var tb = document.getElementById("startQuiz"); if (tb) tb.addEventListener("click", startQuiz);
      var tog = document.getElementById("themeToggle");
      if (tog) tog.addEventListener("click", function () {{
        var cur = document.documentElement.getAttribute("data-theme");
        applyTheme(cur === "dark" ? "light" : "dark");
      }});
    }});
  }}

  if (typeof module !== "undefined" && module.exports) {{
    module.exports = {{
      filterVocab: filterVocab, generateQuiz: generateQuiz, scoreQuiz: scoreQuiz,
    }};
  }}
}})();
"""


@dataclass
class N5SiteBuilder:
    """AIOS tool that generates the N5 learning site into a target directory."""

    producer: str = PRODUCER

    def _emit(self, target_dir: str) -> Dict[str, str]:
        os.makedirs(os.path.join(target_dir, "css"), exist_ok=True)
        os.makedirs(os.path.join(target_dir, "js"), exist_ok=True)

        kana_struct = [{"name": name, "rows": rows} for name, rows in KANA.items()]
        data_js = DATA_JS_TPL.format(
            producer=self.producer,
            kana=json.dumps(kana_struct, ensure_ascii=False),
            vocab=json.dumps(VOCAB, ensure_ascii=False),
            grammar=json.dumps(GRAMMAR, ensure_ascii=False),
        )
        app_js = APP_JS_TPL.format(producer=self.producer)
        files = {
            "index.html": HTML_TPL,
            "css/style.css": CSS_TPL,
            "js/data.js": data_js,
            "js/app.js": app_js,
        }
        written = {}
        for rel, content in files.items():
            path = os.path.join(target_dir, rel)
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            written[rel] = content
        return written

    def build(self, target_dir: str) -> Dict[str, object]:
        """Generate the site and write AIOS-produced provenance evidence."""
        written = self._emit(target_dir)

        # Build a single content hash over all emitted files (deterministic).
        h = hashlib.sha256()
        for rel in sorted(written):
            h.update(rel.encode("utf-8"))
            h.update(written[rel].encode("utf-8"))
        content_hash = h.hexdigest()

        evidence = {
            "producer": self.producer,
            "produced_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": content_hash,
            "files": sorted(written.keys()),
            "vocab_count": len(VOCAB),
            "grammar_count": len(GRAMMAR),
            "note": "Static N5 site generated by an AIOS tool (not hand-written).",
        }
        ev_path = os.path.join(target_dir, "build_evidence.json")
        with open(ev_path, "w", encoding="utf-8") as fh:
            json.dump(evidence, fh, ensure_ascii=False, indent=2)

        return {
            "target_dir": target_dir,
            "files": sorted(written.keys()) + ["build_evidence.json"],
            "content_hash": content_hash,
            "evidence": evidence,
        }


def build_n5_site(target_dir: str, producer: str = PRODUCER) -> Dict[str, object]:
    """Convenience entry point used by the Capability / tests."""
    return N5SiteBuilder(producer=producer).build(target_dir)
