# Versioning Guide (T084)

AIOS 1.x uses **SemVer** (`MAJOR.MINOR.PATCH`) as defined in
[ADR-Compatibility](../adr/ADR-Compatibility.md).

## Bump rules

| Change type | Bump | Requirement |
|-------------|------|-------------|
| Breaking (breaks 1.0 consumer) | MAJOR | ADR + 180d deprecation notice |
| Backward-compatible | MINOR | — |
| Fix | PATCH | — |

## Compatibility matrix

A target version is backward-compatible with a base version iff they share the
same MAJOR and `target >= base`. So `1.0` ↔ `1.x` is compatible; `2.0` is a
breaking release.

## Usage

```python
from aios.versioning import VersionPolicyEngine, ChangeType, VersionChange

eng = VersionPolicyEngine()
decision = eng.decide(VersionChange(
    change_type=ChangeType.BREAKING,
    has_adr=True,
    has_deprecation_notice=True,
    evidence_ref="evt-1",
))
assert decision.bump.value == "major" and decision.allowed
```

Every decision carries an `evidence_ref` (T001 Rule 5). The same change type
always yields the same bump (deterministic).
