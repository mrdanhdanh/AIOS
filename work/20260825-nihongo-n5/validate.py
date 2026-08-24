#!/usr/bin/env python3
"""Validate the N5 Japanese learning website build (offline, no deps)."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def check(cond, msg):
    if not cond:
        print("FAIL:", msg)
        sys.exit(1)
    print("OK  :", msg)


def main():
    # 1. Required files exist and are non-empty
    required = [
        "index.html",
        "css/style.css",
        "js/data.js",
        "js/app.js",
        "README.md",
    ]
    for f in required:
        p = os.path.join(ROOT, f)
        check(os.path.isfile(p) and os.path.getsize(p) > 0, f"exists & non-empty: {f}")

    # 2. index.html references assets and defines sections
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    for ref in ["css/style.css", "js/data.js", "js/app.js"]:
        check(ref in html, f"index.html links {ref}")
    for sid in ["home", "hiragana", "katakana", "greetings", "numbers", "vocab", "grammar", "flashcard", "quiz"]:
        check(f'id="{sid}-view"' in html, f"section present: {sid}-view")

    # 3. data.js defines the content structures
    data = open(os.path.join(ROOT, "js/data.js"), encoding="utf-8").read()
    check("const N5_DATA" in data, "N5_DATA defined in data.js")
    check("buildQuizPool" in data, "buildQuizPool defined in data.js")
    # count hiragana basic entries (46 expected)
    check(data.count('roma: "') > 100, "content entries present (>100 romaji)")

    # 4. app.js wires navigation + quiz + flashcard + speech
    app = open(os.path.join(ROOT, "js/app.js"), encoding="utf-8").read()
    check("showView" in app, "showView navigation in app.js")
    check("nextQuestion" in app, "quiz engine in app.js")
    check("renderFlashcard" in app, "flashcard view in app.js")
    check("speakJa" in app, "speech synthesis (offline TTS) in app.js")
    check("SpeechSynthesisUtterance" in app, "Web Speech API used in app.js")

    print("\nALL CHECKS PASSED — N5 website build is valid.")


if __name__ == "__main__":
    main()
