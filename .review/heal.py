#!/usr/bin/env python3
"""Heal T041/T050: renumber `### AC-NNN —` -> `### AC-0XX-NN —` and delete
spurious `#### AC-0XX-NN — NAME` / `NAME` duplicate blocks created by the
earlier buggy normalizer run."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DETAIL = os.path.join(ROOT, "docs", "detailtask")


def heal(path: str, tasknum: str):
    with open(path, "r", encoding="utf-8") as f:
        t = f.read()
    # 1) delete spurious duplicate blocks: "#### AC-0XX-NN — NAME\nNAME\n"
    t = re.sub(rf"^#### AC-{tasknum}-\d+ — (.+?)\n\1\n?", "", t, flags=re.MULTILINE)
    # 2) renumber "### AC-NNN —" -> "### AC-0XX-NN —"
    def ren(m):
        return f"### AC-{tasknum}-{int(m.group(1)):02d} —"
    t = re.sub(r"^### AC-(\d{1,3})\s*—", ren, t, flags=re.MULTILINE)
    with open(path, "w", encoding="utf-8") as f:
        f.write(t)
    print("healed", os.path.basename(path))


for tn in ["041", "050"]:
    heal(os.path.join(DETAIL, f"T{tn}.md"), tn)
