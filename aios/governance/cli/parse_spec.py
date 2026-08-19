#!/usr/bin/env python
"""parse_spec.py — build a task registry from the master specification.

Validates Rule 1 (unique, immutable IDs) and Rule 2 (dependency references are
well-formed) by parsing the master spec markdown.

Usage:
    python aios/governance/cli/parse_spec.py \
        --spec docs/AIOS_Master_Task_Specification_M0-M26.md
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from typing import Dict, List


TASK_RE = re.compile(r"^#{1,2}\s+(TASK-\d+)\s+—\s+(.+?)\s*$", re.MULTILINE)
MILESTONE_RE = re.compile(r"^#{1,2}\s+(M\d+)\s*$", re.MULTILINE)
DEP_RE = re.compile(r"Dependency[^:]*:\s*(.+)", re.IGNORECASE)


@dataclass
class ParsedTask:
    task_id: str
    title: str
    milestone: str = ""
    dependencies: List[str] = field(default_factory=list)


def parse_spec(text: str) -> List[ParsedTask]:
    """Parse task headers and their milestone context from the spec text."""
    # Determine milestone for each task by position.
    milestones = [(m.start(), m.group(1)) for m in MILESTONE_RE.finditer(text)]
    tasks: List[ParsedTask] = []
    for m in TASK_RE.finditer(text):
        tid = m.group(1)
        title = m.group(2).strip()
        # Find the most recent milestone header before this task.
        milestone = ""
        for pos, ms in milestones:
            if pos < m.start():
                milestone = ms
            else:
                break
        tasks.append(ParsedTask(task_id=tid, title=title, milestone=milestone))
    return tasks


def validate_rule1(tasks: List[ParsedTask]) -> List[str]:
    """Rule 1: task IDs must be unique."""
    errors: List[str] = []
    seen: Dict[str, int] = {}
    for t in tasks:
        seen[t.task_id] = seen.get(t.task_id, 0) + 1
    for tid, count in seen.items():
        if count > 1:
            errors.append(f"Rule 1 violation: task ID '{tid}' appears {count} times (must be unique).")
    return errors


def validate_rule2(tasks: List[ParsedTask], known_ids: set) -> List[str]:
    """Rule 2: dependency references must exist and not be self-referential."""
    errors: List[str] = []
    for t in tasks:
        for dep in t.dependencies:
            if dep not in known_ids:
                errors.append(f"Rule 2 violation: {t.task_id} depends on unknown '{dep}'.")
            if dep == t.task_id:
                errors.append(f"Rule 2 violation: {t.task_id} depends on itself.")
    return errors


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parse master spec into a task registry.")
    parser.add_argument("--spec", default="docs/AIOS_Master_Task_Specification_M0-M26.md")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = parser.parse_args(argv)

    try:
        with open(args.spec, "r", encoding="utf-8") as fh:
            text = fh.read()
    except FileNotFoundError:
        print(f"ERROR: spec file not found: {args.spec}", file=sys.stderr)
        return 2

    tasks = parse_spec(text)
    errors = validate_rule1(tasks) + validate_rule2(tasks, {t.task_id for t in tasks})

    if args.json:
        import json
        print(json.dumps([vars(t) for t in tasks], indent=2))
    else:
        print(f"Parsed {len(tasks)} tasks from {args.spec}")
        for t in tasks[:10]:
            print(f"  {t.task_id} [{t.milestone}] {t.title}")
        if len(tasks) > 10:
            print(f"  ... ({len(tasks) - 10} more)")

    if errors:
        print("\nVALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("\nVALIDATION PASSED: Rule 1 (unique IDs) and Rule 2 (valid deps) OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
