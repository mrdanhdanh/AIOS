# TASK-037 — Breakdown

## Steps
1. Create `aios/distributed/contracts.py` — RuntimeNode (node_id, name, address, state, capacity), NodeState (ONLINE/OFFLINE/DRAINING/FAILED)
2. Create `aios/distributed/node_manager.py` — NodeManager: register_node, get_node, list_nodes, set_node_state, get_healthy_nodes
3. Implement health model: only ONLINE is healthy, UNKNOWN/OFFLINE not selected
4. Implement tenant/policy-aware candidate filtering
5. Create `aios/distributed/tests/` — 5 tests (register, duplicate handling, unhealthy not selected, healthy filter, state transitions)
6. Run architecture guard — verify no Orchestrator → RuntimeNode internal, no Worker → Registry
7. Run full suite — 1773/1773 PASS (5 new), no regressions

## Dependencies
- TASK-036 Multi-Tenancy

## Exit Criteria
- All AC-037-01..07 PASS, gate PASS, no regressions
