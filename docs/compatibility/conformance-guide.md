# Conformance Guide (T087)

A build is declared *compatible* only after passing the full conformance suite
(see [ADR-Compatibility](../adr/ADR-Compatibility.md)).

## The five checks

| Check | Source |
|-------|--------|
| `api` | Backward Compatibility (T086) |
| `schema` | Backward Compatibility (T086) |
| `event` | Backward Compatibility (T086) |
| `version` | Version Baseline (T084) |
| `contract` | Contract Freeze (T064) |

## Gate

One failing check → the build is **not conformant** (fail-closed). A conformant
build may receive a certificate via the Certification suite (T073).

## Usage

```python
from aios.conformance import ConformanceRunner
from aios.contracts.contract import Contract, ContractStatus, ContractSurface

contracts = [Contract(name="api", surface=ContractSurface.API,
                      status=ContractStatus.FROZEN)]
runner = ConformanceRunner()
report = runner.run("1.1.0", contracts=contracts, evidence_ref="ev-1")
assert runner.issue(report) is True  # fail-closed gate
```

The report carries full provenance and is deterministic for the same build + suite.
