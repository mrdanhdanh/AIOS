"""Source / Symbol Index (TASK-118, M18).

Parses source into symbols (function/class/variable) with location + content
hash (T078), stores them, and provides deterministic lookup. Fail-closed: a
parse failure is rejected (T078). Secret isolation (T040/T113). Provenance on
every index (T001 Rule 5).
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from aios.governance.evidence.store import EvidenceStore

from .common import ContextError, SecretBoundary, emit_evidence, sha256


__all__ = ["SymbolIndexError", "Symbol", "SymbolIndexResult", "SymbolIndex"]


class SymbolIndexError(ContextError):
    """Raised when symbol indexing fails (fail-closed, T078)."""


@dataclass
class Symbol:
    name: str
    kind: str  # function | class | variable
    file: str
    line: int
    content_hash: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "file": self.file,
            "line": self.line,
            "content_hash": self.content_hash,
        }


@dataclass
class SymbolIndexResult:
    repo_ref: str
    symbols: list[Symbol]
    index_id: str
    policy_ref: str
    evidence_ref: str
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_ref": self.repo_ref,
            "symbols": [s.to_dict() for s in self.symbols],
            "index_id": self.index_id,
            "policy_ref": self.policy_ref,
            "evidence_ref": self.evidence_ref,
            "content_hash": self.content_hash,
        }


# Generic (non-Python) symbol extraction via regex.
_GENERIC_RE = re.compile(
    r"(?:async\s+)?"
    r"(function|def|class|const|let|var|func)\s+"
    r"([A-Za-z_][A-Za-z0-9_]*)"
)


class SymbolIndex:
    """Parser + symbol store + index lookup."""

    def __init__(
        self,
        *,
        evidence_store: Optional[EvidenceStore] = None,
        run_id: str = "run-context",
        task_id: str = "TASK-118",
        producer: str = "context.symbol_index",
    ) -> None:
        self._store = evidence_store or EvidenceStore()
        self._run_id = run_id
        self._task_id = task_id
        self._producer = producer
        self._by_name: dict[str, list[Symbol]] = {}
        self._by_kind: dict[str, list[Symbol]] = {}

    # -- parsing -------------------------------------------------------- #
    def _parse_python(self, source: str, file: str, content_hash: str) -> list[Symbol]:
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            raise SymbolIndexError(f"python parse failed for {file}: {exc}") from exc
        symbols: list[Symbol] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                symbols.append(Symbol(node.name, "function", file, node.lineno, content_hash))
            elif isinstance(node, ast.ClassDef):
                symbols.append(Symbol(node.name, "class", file, node.lineno, content_hash))
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        symbols.append(
                            Symbol(target.id, "variable", file, node.lineno, content_hash)
                        )
        return symbols

    def _parse_generic(self, source: str, file: str, content_hash: str) -> list[Symbol]:
        symbols: list[Symbol] = []
        for m in _GENERIC_RE.finditer(source):
            kind_token, name = m.group(1), m.group(2)
            kind = {
                "function": "function",
                "def": "function",
                "class": "class",
                "const": "variable",
                "let": "variable",
                "var": "variable",
                "func": "function",
            }.get(kind_token, "variable")
            line = source[: m.start()].count("\n") + 1
            symbols.append(Symbol(name, kind, file, line, content_hash))
        return symbols

    def index_source(self, source: str, file: str, *, language: str = "python") -> list[Symbol]:
        if SecretBoundary.is_secret_path(file):
            raise SymbolIndexError(f"refusing to index secret file: {file}")
        content_hash = sha256(source)
        if language == "python":
            return self._parse_python(source, file, content_hash)
        return self._parse_generic(source, file, content_hash)

    # -- index ----------------------------------------------------------- #
    def index(
        self,
        sources: list[tuple[str, str, str]],
        *,
        policy_ref: str = "pol-context-symbol",
    ) -> SymbolIndexResult:
        """``sources``: list of (source_text, file_path, language)."""
        all_symbols: list[Symbol] = []
        for source, file, lang in sources:
            all_symbols.extend(self.index_source(source, file, language=lang))
        all_symbols.sort(key=lambda s: (s.file, s.line, s.name))
        self._by_name.clear()
        self._by_kind.clear()
        for s in all_symbols:
            self._by_name.setdefault(s.name, []).append(s)
            self._by_kind.setdefault(s.kind, []).append(s)
        fingerprint = "".join(s.name for s in all_symbols[:50])
        index_id = f"sym-{sha256(str(len(all_symbols)) + fingerprint)[:16]}"
        canonical = "\n".join(f"{s.file}:{s.line}:{s.name}:{s.kind}" for s in all_symbols)
        overall = sha256(canonical)
        evidence_ref = emit_evidence(
            self._store,
            task_id=self._task_id,
            run_id=self._run_id,
            producer=self._producer,
            type_="symbol_index",
            source="symbols",
            content=canonical,
        )
        return SymbolIndexResult(
            repo_ref="symbols",
            symbols=all_symbols,
            index_id=index_id,
            policy_ref=policy_ref,
            evidence_ref=evidence_ref,
            content_hash=overall,
        )

    def lookup(self, name: Optional[str] = None, kind: Optional[str] = None) -> list[Symbol]:
        if name is not None and kind is not None:
            return [s for s in self._by_name.get(name, []) if s.kind == kind]
        if name is not None:
            return list(self._by_name.get(name, []))
        if kind is not None:
            return list(self._by_kind.get(kind, []))
        return []
