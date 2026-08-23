"""Smoke tests for the N5 Japanese learning website (TASK-222).

These tests verify the static deliverable under ``implementation/`` without a
browser: file presence, asset wiring, and data integrity. They run as part of
the AIOS pytest suite (``python -m pytest aios -q``).
"""
from __future__ import annotations

import os
import re

IMPL = os.path.dirname(os.path.abspath(__file__))


def _read(name: str) -> str:
    with open(os.path.join(IMPL, name), "r", encoding="utf-8") as fh:
        return fh.read()


def test_index_html_present_and_wired():
    html = _read("index.html")
    assert "css/style.css" in html
    assert "js/data.js" in html
    assert "js/app.js" in html
    assert "Học tiếng Nhật N5" in html


def test_data_js_defines_core_structures():
    data = _read("js/data.js")
    assert "const KANA" in data
    assert "const VOCAB" in data
    assert "const GRAMMAR" in data


def test_vocab_has_sufficient_entries():
    data = _read("js/data.js")
    rows = re.findall(r'\["[^\]]+","[^\]]+","[^\]]+","[^\]]+"\]', data)
    assert len(rows) >= 100, f"expected >=100 vocab rows, got {len(rows)}"


def test_grammar_has_sufficient_entries():
    data = _read("js/data.js")
    patterns = re.findall(r'pattern:\s*"', data)
    assert len(patterns) >= 10, f"expected >=10 grammar patterns, got {len(patterns)}"


def test_app_js_wires_ui():
    app = _read("js/app.js")
    assert "renderKana" in app
    assert "renderVocab" in app
    assert "startQuiz" in app
    assert "GRAMMAR" in app


def test_theme_toggle_present():
    html = _read("index.html")
    assert 'id="themeToggle"' in html
    assert 'data-theme="light"' in html
    app = _read("js/app.js")
    assert "applyTheme" in app
    assert "localStorage" in app


def test_design_tokens_defined():
    css = _read("css/style.css")
    # ui-ux-pro-max design-system: 3-layer tokens + dark theme
    assert ":root" in css
    assert "[data-theme=\"dark\"]" in css
    assert "--primary:" in css
    assert "--space" in css or "--sp-" in css
    assert ":focus-visible" in css
