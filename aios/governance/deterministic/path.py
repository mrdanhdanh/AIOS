"""Deterministic Control Path — Rule 4 (LLM is fallback only, output validated)."""


class ControlPathError(Exception):
    pass


class DeterministicControlPath:
    def __init__(self):
        self.llm_calls = 0

    def route(self, can_decide, planner, validator=None):
        """
        Deterministic first (Rule 4 — fail-closed).
        - can_decide True  -> no LLM call (llm_calls stays 0).
        - can_decide False -> invoke planner (LLM fallback); its output MUST pass validator.
          validator is REQUIRED in fallback path; missing validator -> ControlPathError.
        """
        if can_decide:
            return {"used_llm": False, "result": "deterministic"}
        if validator is None:
            raise ControlPathError("LLM fallback requires a validator (fail-closed)")
        self.llm_calls += 1
        out = planner()
        if not validator(out):
            raise ControlPathError("planner/LLM output failed validation")
        return {"used_llm": True, "result": out}
