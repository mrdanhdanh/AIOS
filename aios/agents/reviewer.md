# Reviewer Role

## Purpose
Final gate before implementation. Produces `review.md`.

## Gate decision
- **APPROVED**: spec + both critiques resolved; dependencies satisfied; invariants listed.
- **CHANGES_REQUESTED**: send back to spec-writer / critic.
- **BLOCKED**: dependency or rule violation; do not proceed.

## Rules
- A task that is not APPROVED cannot enter IMPLEMENT (Rule 6).
- Record the decision + reasoning + actor/source (provenance).
- If a General Rule cannot be satisfied by the proposed design, BLOCK rather than waive.
