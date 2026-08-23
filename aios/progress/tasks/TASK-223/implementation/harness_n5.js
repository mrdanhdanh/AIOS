// Real behavior harness for the AIOS-generated N5 site (run with Node).
// Loads the generated data.js + app.js and asserts the PURE logic actually
// behaves correctly — not just that strings are present in the file.
const data = require("./js/data.js");
const app = require("./js/app.js");

let failures = 0;
function assert(cond, msg) {
  if (!cond) { console.error("FAIL: " + msg); failures++; }
  else { console.log("ok: " + msg); }
}

// --- Dataset integrity (acceptance criteria) ---
assert(data.VOCAB.length >= 100, "VOCAB >= 100 (got " + data.VOCAB.length + ")");
assert(data.GRAMMAR.length >= 10, "GRAMMAR >= 10 (got " + data.GRAMMAR.length + ")");

// --- filterVocab ---
const neko = app.filterVocab(data.VOCAB, "neko", "all");
assert(neko.length === 1 && neko[0][2] === "mèo", "filterVocab('neko') -> mèo");
const filtered = app.filterVocab(data.VOCAB, "", "động từ");
assert(filtered.every(function (v) { return v[3] === "động từ"; }),
  "filterVocab topic filter keeps only that topic");

// --- generateQuiz (deterministic with seed) ---
const q1 = app.generateQuiz(data.VOCAB, 5, 7);
const q2 = app.generateQuiz(data.VOCAB, 5, 7);
assert(JSON.stringify(q1) === JSON.stringify(q2), "generateQuiz deterministic for same seed");
assert(q1.length === 5, "generateQuiz returns requested count");
q1.forEach(function (q) {
  assert(q.options.length === 4, "each question has 4 options");
  assert(q.options.indexOf(q.answer) !== -1, "correct answer is among options");
});

// --- scoreQuiz ---
const allCorrect = q1.map(function (q) { return q.answer; });
assert(app.scoreQuiz(q1, allCorrect) === 5, "scoreQuiz all-correct = 5");
const allWrong = q1.map(function (q) {
  return q.options[(q.options.indexOf(q.answer) + 1) % 4];
});
assert(app.scoreQuiz(q1, allWrong) < 5, "scoreQuiz wrong answers < 5");

if (failures > 0) {
  console.error("HARNESS FAILED: " + failures + " assertion(s)");
  process.exit(1);
}
console.log("HARNESS PASSED");
