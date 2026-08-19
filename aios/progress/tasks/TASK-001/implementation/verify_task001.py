"""Self-contained smoke check for TASK-001 (no pytest required).

Run with:  python aios/progress/tasks/TASK-001/implementation/verify_task001.py
It exercises every governance gate once and prints PASS/FAIL per rule.
"""

import sys
from pathlib import Path

# Make the repo root importable when run directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from aios.governance.task_registry import TaskRegistry, RegistryError
from aios.governance.dependency import DependencyGraph, CycleError
from aios.governance.lifecycle import TaskLifecycle, LifecycleError
from aios.governance.evidence import EvidenceStore, Artifact, Requirement, Run, TaskRecord
from aios.governance.architecture import scan_source
from aios.governance.deterministic import DeterministicControlPath, Request
from aios.governance.regression import RegressionRunner, RegressionOutcome
from aios.governance.gates import GateComponent, UnifiedTaskGate


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    return cond


def main():
    ok = True
    print("TASK-001 governance smoke check\n")

    # Rule 1 — registry rejects duplicate ids
    reg = TaskRegistry()
    reg.create_task("TASK-001", "Governance")
    dup = False
    try:
        reg.create_task("TASK-001", "Duplicate")
    except RegistryError:
        dup = True
    ok &= check("Rule 1: duplicate id rejected", dup)

    # Rule 2 — dependency readiness + cycle detection
    g = DependencyGraph()
    g.add_task("TASK-002", ["TASK-001"])
    # TASK-001 is NOT passed -> TASK-002 must be BLOCKED.
    ready, blocker = g.is_ready("TASK-002", lambda t: "BLOCKED")
    ok &= check("Rule 2: dependency not passed -> BLOCK", ready is False and blocker == "TASK-001")
    gc = DependencyGraph()
    gc.add_task("A", ["B"]); gc.add_task("B", ["A"])
    ok &= check("Rule 2: cycle detected", gc.detect_cycle() is not None)

    # Rule 3 — architecture guard
    v = scan_source("import subprocess\n", "aios/agents/x.py")
    ok &= check("Rule 3: agent subprocess -> violation", any(x.rule == "ARCH-001" for x in v))

    # Rule 4 — deterministic avoids LLM
    calls = {"n": 0}
    dp = DeterministicControlPath(llm_fallback=lambda nr: (_ for _ in ()).throw(AssertionError()) or "x")
    plan = dp.execute(Request(text="status"))
    ok &= check("Rule 4: deterministic -> 0 LLM calls", dp.llm_call_count == 0 and plan.source == "deterministic")

    # Rule 5 — evidence provenance
    store = EvidenceStore()
    store.add_requirement(Requirement("REQ-1", "r"))
    store.add_task_record(TaskRecord("TASK-001", "REQ-1"))
    store.add_artifact(Artifact("ART-1", "TASK-001", "REQ-1"))
    store.add_run(Run("RUN-1", "ART-1", "TASK-001"))
    store.add_evidence("E1", "TASK-001", "RUN-1", "pytest", "test", "src", content="PASS", parent_artifact="ART-1")
    ok &= check("Rule 5: provenance chain complete", store.is_admissible("E1"))

    # Rule 6 — lifecycle missing artifact blocks DONE
    lc = TaskLifecycle(); lc.init("TASK-001")
    blocked = False
    try:
        lc.transition("TASK-001", "SPECIFIED", provided_artifacts=[])
    except LifecycleError:
        blocked = True
    ok &= check("Rule 6: missing artifact -> REJECT", blocked)

    # Rule 7 — regression blocks on closure failure
    rr = RegressionRunner(lambda t: RegressionOutcome(t, passed=(t != "TASK-001")))
    res = rr.run("TASK-003", {"TASK-001", "TASK-002"})
    ok &= check("Rule 7: closure failure -> BLOCKED", res.blocked and res.failed_task == "TASK-001")

    # Unified gate convergence
    gate = UnifiedTaskGate()
    gate.register("registry", lambda c: GateComponent("registry", True))
    gate.register("dependency", lambda c: GateComponent("dependency", True))
    gate.register("architecture", lambda c: GateComponent("architecture", True))
    gate.register("lifecycle", lambda c: GateComponent("lifecycle", True))
    gate.register("evidence", lambda c: GateComponent("evidence", True))
    gate.register("test_evaluate", lambda c: GateComponent("test_evaluate", True))
    gate.register("regression", lambda c: GateComponent("regression", True))
    result = gate.evaluate({})
    ok &= check("Unified Gate: all pass -> PASS", result.passed)

    print("\nRESULT:", "ALL PASS" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
