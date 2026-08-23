"""Context Pipeline (M18) — repository-to-context retrieval substrate.

Packages the eight M18 capabilities as a single, import-safe ``unknown``
(infra) layer:

* T117 Repository Scanner      -> :mod:`aios.context.scanner`
* T118 Source/Symbol Index     -> :mod:`aios.context.symbol_index`
* T119 Dependency Graph        -> :mod:`aios.context.dependency_graph`
* T120 Semantic + Hybrid Index -> :mod:`aios.context.hybrid_index`
* T121 Context Retriever       -> :mod:`aios.context.retriever`
* T122 Context Builder + Budget-> :mod:`aios.context.builder`
* T123 Context Verification    -> :mod:`aios.context.verification`
* T124 Context Harness/Conform -> :mod:`aios.context.conformance`

Layering: ``unknown`` (infra) layer. Integrates with ``aios.governance.evidence``
(T001), ``aios.verification_integrity`` (T078), ``aios.security`` (T040/T113) and
``aios.context_optimizer`` (T024). Deterministic-first: no LLM in any stage.
"""

from .builder import BuildError, BuiltChunk, BuiltContext, ContextBuilder
from .common import ContextError, SecretBoundary
from .conformance import (
    ConformanceError,
    ConformanceResult,
    ConformanceStage,
    ConformanceVerdict,
    ContextConformance,
    ContextHarness,
)
from .dependency_graph import (
    DepEdge,
    DepNode,
    DependencyGraph,
    DependencyGraphError,
    DependencyGraphResult,
)
from .hybrid_index import (
    Embedding,
    HybridHit,
    HybridIndex,
    HybridIndexError,
    HybridIndexResult,
    HybridQueryResult,
)
from .retriever import ContextRetriever, RetrievalError, RetrievalHit, RetrievalResult
from .scanner import ChangeSet, RepositoryScanner, ScanError, ScanResult, ScannedFile
from .symbol_index import Symbol, SymbolIndex, SymbolIndexError, SymbolIndexResult
from .verification import (
    ContextVerification,
    VerificationError,
    VerificationResult,
    VerificationVerdict,
)

__all__ = [
    # common
    "ContextError",
    "SecretBoundary",
    # T117
    "ScanError",
    "ScannedFile",
    "ChangeSet",
    "ScanResult",
    "RepositoryScanner",
    # T118
    "SymbolIndexError",
    "Symbol",
    "SymbolIndexResult",
    "SymbolIndex",
    # T119
    "DependencyGraphError",
    "DepNode",
    "DepEdge",
    "DependencyGraphResult",
    "DependencyGraph",
    # T120
    "HybridIndexError",
    "Embedding",
    "HybridHit",
    "HybridIndexResult",
    "HybridQueryResult",
    "HybridIndex",
    # T121
    "RetrievalError",
    "RetrievalHit",
    "RetrievalResult",
    "ContextRetriever",
    # T122
    "BuildError",
    "BuiltChunk",
    "BuiltContext",
    "ContextBuilder",
    # T123
    "VerificationError",
    "VerificationVerdict",
    "VerificationResult",
    "ContextVerification",
    # T124
    "ConformanceError",
    "ConformanceStage",
    "ConformanceVerdict",
    "ConformanceResult",
    "ContextHarness",
    "ContextConformance",
]
