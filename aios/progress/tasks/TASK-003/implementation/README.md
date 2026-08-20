# TASK-003 — Implementation

The implementation lives in `d:\AIOS\aios\core\`.

```
aios/core/
  version.py    # SemVer parsing / comparison / VersionError
  contracts.py  # Typed contracts + compatibility checker
  container.py  # DI container (singleton / scoped / transient, RLock)
  events.py     # EventBus (typed pub/sub, wildcard, ordered)
  planner.py    # ExecutionPlan / Step / StepStatus primitives
  __init__.py   # public API exports
  tests/
    test_version.py
    test_contracts.py
    test_container.py
    test_events.py
    test_planner.py
```

`verify_task003.py` below runs a self-contained smoke check (no pytest required).

```python
# Run with: python aios/progress/tasks/TASK-003/implementation/verify_task003.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from aios.core.version import SemVer
from aios.core.contracts import Contract
from aios.core.container import Container
from aios.core.events import EventBus
from aios.core.planner import ExecutionPlan, Step

ok = True
def check(name, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

# Version
check("semver parse", str(SemVer.parse("1.2.3")) == "1.2.3")
check("semver compare", SemVer.parse("1.0.0") < SemVer.parse("2.0.0"))

# Container
c = Container()
c.register(str, lambda: "hello", lifetime="singleton")
check("container singleton", c.resolve(str) == "hello")

# EventBus
bus = EventBus()
seen = []
bus.subscribe("test", lambda e: seen.append(e))
bus.publish("test", {"x": 1})
check("event bus", len(seen) == 1)

# Planner
plan = ExecutionPlan.create("p1")
plan.add_step(Step(id="s1", name="step1"))
check("planner", len(plan.steps) == 1)

print("\nAll checks", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
```
