# TASK-005 — Implementation

The implementation lives in `d:\AIOS\aios\runtime\`.

```
aios/runtime/
  execution.py   # Executor (policy pre-check, retry, timeout, cancel, audit)
  scheduler.py   # Scheduler (technical priority queue of requests)
  state.py       # ExecutionState (serializable), StateStore (checkpoint/restore)
  resource.py    # ResourcePool (grant / queue / reject + promotion)
  kernel.py      # RuntimeKernel (composes all 9 services via Container)
  __init__.py    # extended public API
aios/core/
  container.py   # HARDENING: Lock -> RLock (factories may recursively resolve)
```

`verify_task005.py` below runs a self-contained smoke check of the kernel +
execution through the wiring (no pytest required).

```python
# Run with: python aios/progress/tasks/TASK-005/implementation/verify_task005.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from aios.runtime import RuntimeKernel, ExecutionOutcome
from aios.core.planner import ExecutionPlan, Step

ok = True
def check(name, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

k = RuntimeKernel()
check("kernel wires context", k.context is not None)
check("kernel wires policy", k.policy is not None)

plan = ExecutionPlan(plan_id="p1")
plan.add_step(Step(step_id="s0", action="echo"))
rep = k.executor.execute(plan, lambda s, c: f"ran-{s.step_id}")
check("executor runs through wiring", rep.status == ExecutionOutcome.COMPLETED)

# Resource pool.
k.resources.register("gpu", 1)
g = k.resources.request("h", "gpu", 1)
check("resource grant", g.status.value == "granted")

# Scheduler.
r = k.scheduler.enqueue("work", priority=0)
check("scheduler enqueue", k.scheduler.dequeue().request_id == r.request_id)

print("\nRESULT:", "ALL PASS" if ok else "FAILURES PRESENT")
raise SystemExit(0 if ok else 1)
```
