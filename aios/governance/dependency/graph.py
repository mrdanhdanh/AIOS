"""Dependency Graph — Rule 2 (dependency decides order; milestone decides boundary)."""
from ..task_registry.registry import TaskRegistry

WHITE, GRAY, BLACK = 0, 1, 2


class DependencyError(Exception):
    pass


class DependencyGraph:
    def __init__(self, registry: TaskRegistry):
        self.reg = registry

    def _deps(self, task_id):
        """Return direct dependencies. Raises RegistryError if task unknown (fail-closed)."""
        return list(self.reg.get(task_id).dependencies)

    def deps_of(self, task_id):
        """Safe accessor: returns [] only if task has no deps; raises if task unknown."""
        return self._deps(task_id)

    def is_ready(self, task_id, statuses):
        """A task is READY only when every dependency status == 'PASS'. Fail-closed."""
        try:
            deps = self._deps(task_id)
        except Exception:
            return False  # unknown task -> BLOCK
        for dep in deps:
            if statuses.get(dep) != "PASS":
                return False
        # also enforce milestone boundary: dependency milestone must not be later stage
        # (milestone string comparison: M0 < M1 < ...; UNKNOWN never blocks)
        try:
            task_milestone = self.reg.get(task_id).milestone
            for dep in deps:
                try:
                    dep_milestone = self.reg.get(dep).milestone
                    if dep_milestone != "UNKNOWN" and task_milestone != "UNKNOWN":
                        # extract numeric part for ordering
                        import re
                        tm = int(re.search(r'\d+', task_milestone).group())
                        dm = int(re.search(r'\d+', dep_milestone).group())
                        if dm > tm:
                            return False
                except Exception:
                    return False
        except Exception:
            return False
        return True

    def detect_cycle(self, task_id):
        color = {}

        def dfs(nid):
            color[nid] = GRAY
            try:
                deps = self._deps(nid)
            except Exception:
                color[nid] = BLACK
                return False
            for d in deps:
                c = color.get(d, WHITE)
                if c == GRAY:
                    return True
                if c == WHITE and dfs(d):
                    return True
            color[nid] = BLACK
            return False

        return dfs(task_id)

    def closure(self, task_id):
        """Transitive dependency closure (for regression Rule 7)."""
        out, stack = set(), list(self._deps(task_id))
        while stack:
            cur = stack.pop()
            if cur in out:
                continue
            out.add(cur)
            try:
                stack.extend(self._deps(cur))
            except Exception:
                pass
        return out
