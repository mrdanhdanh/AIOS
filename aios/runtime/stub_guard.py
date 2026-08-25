"""StubGuard — detect and reject null-stub / SKIPPED pipeline steps (TASK-227).

Runtime-layer capability (compliant ARCH-001..004). Enforces AGENTS.md §12 rule
"cấm null-stub / bước SKIPPED": a governance pipeline step must report OK /
COMPLETED / FAILED with a reason — never silently SKIPPED. This is deterministic
and fail-closed: an unknown status is rejected, not tolerated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


VALID = ("OK", "COMPLETED", "FAILED")
SKIP_MARKERS = ("SKIPPED", "skip", "null", "stub", "_Null", "SKIP")


@dataclass
class StepRecord:
    step_id: str
    status: str
    detail: str = ""


class StubGuard:
    """Validates pipeline step statuses; rejects SKIPPED/null-stub steps."""

    def __init__(self) -> None:
        self._steps: List[StepRecord] = []

    def record(self, step_id: str, status: str, detail: str = "") -> None:
        if not step_id:
            raise ValueError("step_id must be non-empty")
        if not status:
            raise ValueError("status must be non-empty")
        self._steps.append(StepRecord(step_id=step_id, status=status, detail=detail))

    def is_skip(self, status: str) -> bool:
        s = status.strip().upper()
        return any(m.upper() in s for m in SKIP_MARKERS) or s not in VALID

    def violations(self) -> List[StepRecord]:
        return [s for s in self._steps if self.is_skip(s.status)]

    def is_clean(self) -> bool:
        return len(self.violations()) == 0

    def report(self) -> str:
        v = self.violations()
        if not v:
            return ""
        lines = [f"STUB-GUARD: {len(v)} SKIPPED/null-stub step(s) detected:"]
        for s in v:
            lines.append(f"  - {s.step_id}: status='{s.status}' detail='{s.detail}'")
        lines.append("Pipeline must not bypass steps (AGENTS.md §12).")
        return "\n".join(lines)

    def reset(self) -> None:
        self._steps.clear()
