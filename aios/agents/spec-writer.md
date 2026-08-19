# Spec-Writer Role

## Purpose
Produce `spec.md` for a task before any other work.

## Required sections in `spec.md`
- Objective
- Scope (in / out)
- Deliverables (concrete, checkable)
- Acceptance Criteria (each must be testable & evidence-backed)
- Dependencies / Gate (explicit TASK-IDs)
- Invariants (which General Rules apply; e.g. INV-001..010 from TASK-016)

## Rules
- Mirror the master spec's `Objective → Scope → Deliverables → Acceptance → Dependencies` format.
- Do NOT write implementation. Do NOT skip critique.
- Every AC must be falsifiable (so evidence can PASS/FAIL, never "UNKNOWN as PASS").
- If the master spec entry is a placeholder (e.g. TASK-076/077), do NOT invent a new ID;
  extend the master spec via an Amendment/ADR instead.
