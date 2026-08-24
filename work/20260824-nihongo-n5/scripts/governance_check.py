#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AIOS governance gate for the Nihongo N5 static site.

Deterministic validation (no LLM, no network):
  - All expected files exist (Registry/Evidence).
  - style.css is responsive (media query) and has hamburger menu (Architecture/UX).
  - app.js quiz is diverse: 5 question types + shuffle (Deterministic behaviour).
  - data.js carries VOCAB/GRAMMAR/KANJI (Evidence content present).
  - No external http(s) CDN dependency (Offline-First).
Emits a sha256 manifest as provenance evidence.
"""
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
ASSETS = os.path.join(SITE, "assets")

EXPECTED = [
    "index.html", "hiragana.html", "katakana.html", "vocab.html",
    "grammar.html", "kanji.html", "quiz.html",
    "assets/style.css", "assets/data.js", "assets/app.js",
]

REQUIRED_QTYPES = ["jp2vi", "vi2jp", "jp2ro", "ro2jp", "gram"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(msg):
    print("FAIL: " + msg)
    sys.exit(1)


def main():
    # 1. Registry/Evidence — all files present
    for rel in EXPECTED:
        p = os.path.join(SITE, rel)
        if not os.path.exists(p):
            fail("missing file: %s" % rel)

    # 2. Architecture/UX — responsive + hamburger
    css = open(os.path.join(ASSETS, "style.css"), encoding="utf-8").read()
    if "@media" not in css or "menu-toggle" not in css:
        fail("style.css missing responsive media query or hamburger menu")

    # 3. Deterministic behaviour — diverse quiz
    app = open(os.path.join(ASSETS, "app.js"), encoding="utf-8").read()
    for qt in REQUIRED_QTYPES:
        if qt not in app:
            fail("quiz missing question type: %s" % qt)
    if "function shuffle" not in app:
        fail("quiz missing shuffle (random answers)")

    # 4. Evidence — data present
    data = open(os.path.join(ASSETS, "data.js"), encoding="utf-8").read()
    for key in ["VOCAB", "GRAMMAR", "KANJI"]:
        if ("const %s =" % key) not in data:
            fail("data.js missing %s" % key)

    # 5. Offline-First — no external CDN
    for rel in EXPECTED:
        if rel.endswith(".html") or rel.endswith(".js") or rel.endswith(".css"):
            txt = open(os.path.join(SITE, rel), encoding="utf-8").read()
            if re.search(r'https?://(?!localhost)', txt):
                fail("external network dependency found in %s" % rel)

    # Provenance manifest (Evidence)
    print("PASS — governance gate OK")
    print("Evidence (sha256):")
    for rel in EXPECTED:
        print("  %s  %s" % (sha256(os.path.join(SITE, rel))[:16], rel))
    print("Files: %d | Quiz types: %d | Offline: yes" % (len(EXPECTED), len(REQUIRED_QTYPES)))


if __name__ == "__main__":
    main()
