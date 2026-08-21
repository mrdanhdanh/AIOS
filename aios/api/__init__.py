"""AIOS API — FastAPI REST + WebSocket boundary (TASK-017, M3).

Presentation layer only — no business logic, no bypass of Policy/Permission.
All operations go through RuntimeKernel + PolicyEngine + EventBus.

Layering: ``api`` layer — may import orchestrator/runtime/skill/capability/tool/unknown.
"""
