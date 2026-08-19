# TASK-006 — Implementation

The implementation lives in `d:\AIOS\aios\runtime\providers\`.

```
aios/runtime/providers/
  contract.py    # ModelCapability, ModelMetadata, UsageRecord, CompletionRequest/Result, ProviderAdapter
  adapters.py    # MockProvider (offline), OpenAIProvider (lazy SDK), OllamaProvider (stdlib urllib)
  registry.py    # ProviderRegistry, select_model (deterministic), RegistryError
  __init__.py    # public API for the providers package
  tests/
    test_contract.py
    test_adapters.py
    test_registry.py
aios/runtime/__init__.py   # extended to export the provider API
```

`verify_task006.py` below runs a self-contained smoke check of the provider
contract + deterministic selection (no pytest, no network required).

```python
# Run with: python aios/progress/tasks/TASK-006/implementation/verify_task006.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from aios.runtime.providers import (
    ProviderRegistry, ModelCapability, ModelMetadata, CompletionRequest, select_model,
)

ok = True
def check(name, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")

r = ProviderRegistry()
check("defaults to offline mock", r.list_models(offline_only=True)[0].offline)

# Deterministic selection: offline + lower cost wins.
models = [
    ModelMetadata(model_id="online", provider="x", offline=False, cost_per_1k_input=0.0),
    ModelMetadata(model_id="offline", provider="y", offline=True, cost_per_1k_input=5.0),
]
chosen = select_model(models, offline_first=True)
check("select_model offline-first", chosen.model_id == "offline")

# Complete through mock + call accounting.
res = r.complete(CompletionRequest(prompt="hi"))
check("complete via mock", "hi" in res.text and r.call_count == 1)

print("\nRESULT:", "ALL PASS" if ok else "FAILURES PRESENT")
raise SystemExit(0 if ok else 1)
```
