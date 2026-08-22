"""AIOS Architecture 1.0 frozen baseline (TASK-063).

This module is the **canonical, frozen reference** for the AIOS architecture
baseline 1.0. It does NOT redefine layer rules — it re-exports the single
source of truth from :mod:`aios.governance.architecture.guard` so that the ADR
and every downstream consumer (CI, gates, docs) read identical constants.

Freeze principles (see ``docs/adr/ADR-ARCH-1.0.md``):
* **No silent change** — changing the layer contract requires an ADR + a
  ``ARCHITECTURE_VERSION`` bump.
* **Fail-closed** — a parse error or any violation BLOCKS the task; the guard
  never downgrades a violation to a warning.
* **Deterministic** — same source tree + same guard version => same result.
* **No parallel architecture** — there is exactly one layer order; no second
  parallel layering is ever introduced.
"""

from __future__ import annotations

from typing import Dict, List

from .guard import (
    ALLOWED_IMPORT_LAYERS,
    ARCH_RULES,
    LAYER_KEYWORDS,
    LAYER_ORDER,
    classify_module,
    scan_source,
)

# ---------------------------------------------------------------------------
# Frozen version marker
# ---------------------------------------------------------------------------
# Bump this ONLY via an ADR (no silent change). TASK-063 freezes 1.0.
ARCHITECTURE_VERSION = "1.0"

# Human-readable frozen layer contract. Lower index = higher layer (caller);
# higher index = lower layer (callee). Imports must only go downward.
FROZEN_LAYER_CONTRACT: List[str] = list(LAYER_ORDER)

# Frozen rule set (ARCH-001..004) — re-exported, never redefined here.
FROZEN_ARCH_RULES: Dict[str, str] = dict(ARCH_RULES)

# Frozen classification + allow-list — re-exported from the single source.
FROZEN_LAYER_KEYWORDS: Dict[str, str] = dict(LAYER_KEYWORDS)
FROZEN_ALLOWED_IMPORT_LAYERS: Dict[str, List[str]] = {
    k: list(v) for k, v in ALLOWED_IMPORT_LAYERS.items()
}


def frozen_layer_contract() -> List[str]:
    """Return the frozen, canonical layer order (Agent->...->Tool).

    The returned list is a copy of :data:`LAYER_ORDER` from ``guard.py`` so
    callers cannot mutate the single source of truth.
    """
    return list(LAYER_ORDER)


def frozen_arch_rules() -> Dict[str, str]:
    """Return the frozen ARCH-001..004 rule descriptions (copy)."""
    return dict(ARCH_RULES)


def is_frozen_layer(layer: str) -> bool:
    """True if ``layer`` is part of the frozen 1.0 contract."""
    return layer in LAYER_ORDER


def classify(module_path: str) -> str:
    """Classify a module path into a frozen layer (delegates to guard)."""
    return classify_module(module_path)


def scan(code: str, module_path: str = "<string>"):
    """Scan source against the frozen contract (delegates to guard)."""
    return scan_source(code, module_path=module_path)


__all__ = [
    "ARCHITECTURE_VERSION",
    "FROZEN_LAYER_CONTRACT",
    "FROZEN_ARCH_RULES",
    "FROZEN_LAYER_KEYWORDS",
    "FROZEN_ALLOWED_IMPORT_LAYERS",
    "frozen_layer_contract",
    "frozen_arch_rules",
    "is_frozen_layer",
    "classify",
    "scan",
]
