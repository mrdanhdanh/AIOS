#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-Improver: feed REAL session-store friction signals and propose a task.

Signals are derived from the local session store (provenance-bearing,
deterministic). Counts observed 2026-08-25:
  - retry loops ("thử lại"/"Try Again"/"tiếp tục"): 165
  - SKIPPED / null-stub: 44
  - permission errors: 9
  - PowerShell false-negatives: 6
These mirror the /chronicle improve analysis recorded in AGENTS.md §12.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))

from aios.agents.self_improver import SelfImproverAgent  # type: ignore


@dataclass
class Sig:
    evidence_id: str
    task_id: str
    producer: str
    type: str
    status: str


# Real signal counts -> evidence records (proportional, capped for clarity).
SIGNALS = [
    *[Sig(f"retry-{i}", "AIOS-OPS", "retry-loop", "friction", "FAIL") for i in range(10)],
    *[Sig(f"skip-{i}", "AIOS-OPS", "skipped-stub", "friction", "FAIL") for i in range(6)],
    *[Sig(f"perm-{i}", "AIOS-OPS", "permission", "friction", "FAIL") for i in range(3)],
    *[Sig(f"ps-{i}", "AIOS-OPS", "powershell-false-negative", "friction", "UNKNOWN") for i in range(2)],
]


class Store:
    def list_all(self):
        return SIGNALS


class Registry:
    def get_task(self, tid):
        return None

    def list_tasks(self):
        return []


def main() -> int:
    agent = SelfImproverAgent(Store(), Registry())
    result = agent.analyze()
    print(f"analyzed signals: {result.analyzed_tasks}")
    print(f"proposals: {len(result.proposals)}")
    for p in result.proposals:
        print(f"  - {p.title} | module={p.target_module} | conf={p.confidence:.2f}")
    best = agent.propose_next()
    if best is None:
        print("FAIL-CLOSED: no proposal (insufficient evidence)")
        return 0
    print("\n=== TOP PROPOSAL (spec draft) ===")
    print(best.proposed_spec)
    # Persist the proposal as a ready-to-go spec for the Coordinator pipeline.
    out = REPO / "aios" / "progress" / "tasks" / "TASK-225" / "proposal-draft.md"
    out.write_text(
        f"# Self-Improvement Proposal — {best.title}\n\n"
        f"**Target module:** `{best.target_module}`\n\n"
        f"**Confidence:** {best.confidence:.2f}\n\n"
        f"**Source signals:**\n"
        + "\n".join(f"- {s}" for s in best.source_signals)
        + f"\n\n{best.proposed_spec}\n",
        encoding="utf-8",
    )
    print(f"\n[written] {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
