# TASK-059 Implementation

## Modules
- `contracts.py` — `Authority` (multi-dimensional), `DelegateRequest`, `DelegateResponse`, `DelegationDecision`.
- `delegation.py` — `AuthorityAttenuator` (Parent ∩ Scope ∩ Policy ∩ Budget), `DelegationManager` (anti-amplification, bounded limits, provenance records).

## Design notes
- Delegation is a capability on the existing Orchestrator; no second control plane.
- Authority is multi-dimensional; attenuation intersects every dimension and reduces `max_depth` per level (anti-amplification).
- Child tenant must equal parent tenant; otherwise attenuation yields empty tenant → BLOCK.
- Governor (T054) can BLOCK/ASK_HUMAN; parent remains accountable for aggregated outcome.
