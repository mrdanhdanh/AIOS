"""Context Harness + Conformance (TASK-124, M18).

Runs the full context pipeline (T117->T123) deterministically (no LLM) and
produces a conformance verdict. Fail-closed: any stage FAIL/INCONCLUSIVE ->
conformance FAIL. Provenance (T001 Rule 5). Deterministic.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from aios.governance.evidence.store import EvidenceStore

from .builder import BuiltContext, ContextBuilder
from .common import ContextError, emit_evidence, sha256
from .dependency_graph import DependencyGraph, DependencyGraphResult
from .hybrid_index import HybridIndex, HybridIndexResult
from .retriever import ContextRetriever, RetrievalResult
from .scanner import RepositoryScanner, ScanResult
from .symbol_index import SymbolIndex, SymbolIndexResult
from .verification import ContextVerification, VerificationResult


__all__ = [
    "ConformanceError",
    "ConformanceStage",
    "ConformanceVerdict",
    "ConformanceResult",
    "ContextHarness",
    "ContextConformance",
]


class ConformanceError(ContextError):
    """Raised when conformance cannot proceed (fail-closed, T078)."""


class ConformanceVerdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


@dataclass
class ConformanceStage:
    name: str
    verdict: ConformanceVerdict
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "verdict": self.verdict.value, "detail": self.detail}


@dataclass
class ConformanceResult:
    pipeline_ref: str
    stage_results: list[ConformanceStage]
    conformance_result: ConformanceVerdict
    integrity_verified: bool
    evidence_ref: str
    authority: str = "aios"
    content_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "pipeline_ref": self.pipeline_ref,
            "stage_results": [s.to_dict() for s in self.stage_results],
            "conformance_result": self.conformance_result.value,
            "integrity_verified": self.integrity_verified,
            "evidence_ref": self.evidence_ref,
            "authority": self.authority,
            "content_hash": self.content_hash,
        }


class ContextHarness:
    """Runs the T117->T123 pipeline deterministically (no LLM)."""

    def __init__(
        self,
        *,
        evidence_store: Optional[EvidenceStore] = None,
        run_id: str = "run-context",
        producer: str = "context.harness",
    ) -> None:
        self._store = evidence_store or EvidenceStore()
        self._run_id = run_id
        self._producer = producer

    def run_pipeline(
        self,
        repo_path: str,
        query: str,
        chunks: list,
        *,
        budget_limit: int = 1000,
    ) -> dict[str, Any]:
        scanner = RepositoryScanner(
            evidence_store=self._store, run_id=self._run_id, task_id="TASK-117"
        )
        scan = scanner.scan(repo_path)
        # Build symbol index + dependency graph from scanned (non-secret) files.
        sources: list[tuple[str, str, str]] = []
        for f in scan.files:
            full = os.path.join(repo_path, f.path)
            try:
                with open(full, "r", encoding="utf-8") as fh:
                    text = fh.read()
            except Exception:
                continue
            lang = "python" if f.file_type == "py" else "generic"
            sources.append((text, f.path, lang))
        sym_index = SymbolIndex(evidence_store=self._store, run_id=self._run_id, task_id="TASK-118")
        sym_res = sym_index.index(sources)
        dep_graph = DependencyGraph(
            evidence_store=self._store, run_id=self._run_id, task_id="TASK-119"
        )
        dep_res = dep_graph.build(sources)
        hybrid = HybridIndex(evidence_store=self._store, run_id=self._run_id, task_id="TASK-120")
        hyb_res = hybrid.build(sym_res, dep_res, chunks)
        retriever = ContextRetriever(
            evidence_store=self._store, run_id=self._run_id, task_id="TASK-121"
        )
        retrieval = retriever.retrieve(hybrid, query)
        builder = ContextBuilder(
            evidence_store=self._store, run_id=self._run_id, task_id="TASK-122"
        )
        built = builder.build(retrieval, budget_limit=budget_limit)
        verifier = ContextVerification(
            evidence_store=self._store, run_id=self._run_id, task_id="TASK-123"
        )
        verification = verifier.verify(built)
        return {
            "scan": scan,
            "symbol_index": sym_res,
            "dependency": dep_res,
            "hybrid": hyb_res,
            "retrieval": retrieval,
            "built": built,
            "verification": verification,
        }


class ContextConformance:
    """Conformance suite over the T117->T123 pipeline stages."""

    def __init__(
        self,
        *,
        evidence_store: Optional[EvidenceStore] = None,
        run_id: str = "run-context",
        producer: str = "context.conformance",
    ) -> None:
        self._store = evidence_store or EvidenceStore()
        self._run_id = run_id
        self._producer = producer

    def evaluate(self, harness_result: dict[str, Any]) -> ConformanceResult:
        stages: list[ConformanceStage] = []
        scan: ScanResult = harness_result["scan"]
        stages.append(
            ConformanceStage(
                "scan", ConformanceVerdict.PASS if scan.files else ConformanceVerdict.FAIL, "scanned files"
            )
        )
        sym: SymbolIndexResult = harness_result["symbol_index"]
        stages.append(
            ConformanceStage(
                "symbol_index",
                ConformanceVerdict.PASS if sym.symbols else ConformanceVerdict.FAIL,
                "indexed symbols",
            )
        )
        dep: DependencyGraphResult = harness_result["dependency"]
        stages.append(
            ConformanceStage(
                "dependency",
                ConformanceVerdict.FAIL if dep.has_cycle else ConformanceVerdict.PASS,
                "cyclic" if dep.has_cycle else "acyclic",
            )
        )
        hyb: HybridIndexResult = harness_result["hybrid"]
        stages.append(
            ConformanceStage(
                "hybrid", ConformanceVerdict.PASS if hyb.embeddings else ConformanceVerdict.FAIL, "embeddings built"
            )
        )
        ret: RetrievalResult = harness_result["retrieval"]
        stages.append(
            ConformanceStage(
                "retriever", ConformanceVerdict.PASS if ret.hits else ConformanceVerdict.FAIL, "retrieved hits"
            )
        )
        built: BuiltContext = harness_result["built"]
        stages.append(
            ConformanceStage(
                "builder",
                ConformanceVerdict.PASS if built.within_budget else ConformanceVerdict.FAIL,
                "budget",
            )
        )
        ver: VerificationResult = harness_result["verification"]
        ver_verdict = ConformanceVerdict(ver.verification_result.value)
        stages.append(
            ConformanceStage("verification", ver_verdict, "; ".join(ver.notes) or "ok")
        )

        integrity_verified = ver.integrity_verified
        any_bad = any(
            s.verdict in (ConformanceVerdict.FAIL, ConformanceVerdict.INCONCLUSIVE) for s in stages
        )
        all_pass = all(s.verdict == ConformanceVerdict.PASS for s in stages)
        # Fail-closed: any FAIL/INCONCLUSIVE or unverified integrity -> FAIL.
        if any_bad or not integrity_verified:
            result = ConformanceVerdict.FAIL
        elif all_pass:
            result = ConformanceVerdict.PASS
        else:
            result = ConformanceVerdict.INCONCLUSIVE
        canonical = "\n".join(f"{s.name}:{s.verdict.value}" for s in stages)
        content_hash = sha256(canonical)
        evidence_ref = emit_evidence(
            self._store,
            task_id="TASK-124",
            run_id=self._run_id,
            producer=self._producer,
            type_="conformance",
            source="conformance",
            content=canonical,
        )
        return ConformanceResult(
            pipeline_ref="T117-T123",
            stage_results=stages,
            conformance_result=result,
            integrity_verified=integrity_verified,
            evidence_ref=evidence_ref,
            authority="aios",
            content_hash=content_hash,
        )
