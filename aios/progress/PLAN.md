# AIOS Progress Plan

Ordered task index and status. Status values: `PLANNED | SPECIFIED | ... | DONE | BLOCKED | DEPRECATED`.

| Task | Milestone | Title | Dependencies | Status |
|------|-----------|-------|--------------|--------|
| TASK-001 | M0 | Task Governance System | — | DONE |
| TASK-002 | M1 | Monorepo + aios Scaffold | TASK-001 | DONE |
| TASK-003 | M1 | Kernel Foundations | TASK-002 | DONE |
| TASK-004 | M1 | Runtime Services I | TASK-003 | DONE |
| TASK-005 | M1 | Runtime Services II | TASK-004 | DONE |
| TASK-006 | M1 | Model Contract + Provider Registry | TASK-004,TASK-005 | DONE |
| TASK-007 | M1 | Memory + Knowledge | TASK-003 | DONE |
| TASK-008 | M1 | Workflow Definition + Compiler | TASK-003 | DONE |
| TASK-009 | M1 | Capability Foundation | TASK-003 | DONE |
| TASK-011 | M1 | M1 Remediation / Architecture Hardening | TASK-005,TASK-009 | DONE |
| TASK-010 | M2 | Decision Pipeline | TASK-011 | DONE |

> TASK-010 is intentionally sequenced after TASK-011 in this index to keep the
> M1 hardening gate coherent; see the master spec for canonical ordering.

| TASK-012 | M2 | Operational Orchestration | TASK-010 | DONE |
| TASK-013 | M2 | Worker Plane | TASK-010,TASK-012 | DONE |
| TASK-014 | M2 | Tool + Capability Layer | TASK-010,TASK-013 | DONE |
| TASK-015 | M2 | Plugin / Skill Execution | TASK-014 | DONE |
| TASK-016 | M2 | Architecture Hardening | TASK-010,TASK-011,TASK-012,TASK-013,TASK-014,TASK-015 | DONE |
| TASK-017 | M3 | FastAPI REST + WebSocket | TASK-016 | DONE |

| TASK-018 | M3 | Dashboard SPA | TASK-017 | DONE |
| TASK-019 | M3 | VS Code Extension | TASK-017 | DONE |
| TASK-020 | M4 | Upgrade Pipeline | TASK-019 | DONE |
| TASK-021 | M4 | Observability | TASK-020 | DONE |
| TASK-022 | M4 | Orchestrator v2 | TASK-021 | DONE |
| TASK-023 | M5 | Memory Coordinator | TASK-022 | DONE |
| TASK-024 | M5 | Context Optimizer | TASK-023 | DONE |
| TASK-025 | M5 | Model Router | TASK-024 | DONE |
| TASK-026 | M5 | Planning Engine | TASK-025 | DONE |
| TASK-027 | M5 | Execution Graph | TASK-026 | DONE |
| TASK-028 | M5 | Parallel Scheduler | TASK-027 | DONE |
| TASK-029 | M6 | Harness Kernel | TASK-028 | DONE |
| TASK-030 | M6 | Execution Verification | TASK-029 | DONE |
| TASK-031 | M6 | Test Harness + Scenario | TASK-030 | DONE |
| TASK-032 | M6 | Evaluation Harness | TASK-031 | DONE |
| TASK-033 | M6 | Benchmark + Regression | TASK-032 | DONE |
| TASK-034 | M6 | Doctor + Readiness | TASK-033 | DONE |
| TASK-035 | M7 | Identity + RBAC | TASK-034 | DONE |
| TASK-036 | M7 | Multi-Tenancy | TASK-035 | DONE |
| TASK-037 | M7 | Distributed Runtime | TASK-036 | DONE |
| TASK-038 | M7 | Distributed Scheduler | TASK-037 | DONE |
| TASK-039 | M7 | Quota + Cost | TASK-038 | DONE |
| TASK-040 | M7 | Credential Isolation | TASK-039 | DONE |
| TASK-041 | M7 | HA + Audit + Recovery | TASK-040 | DONE |
| TASK-042 | M7 | Enterprise Operations | TASK-041 | DONE |
| TASK-043 | M8 | Public SDK | TASK-042 | DONE |
| TASK-044 | M8 | Plugin Runtime | TASK-043 | DONE |
| TASK-045 | M8 | Extension Contracts | TASK-044 | DONE |
| TASK-046 | M8 | Ecosystem Registry | TASK-045 | DONE |
| TASK-047 | M8 | Developer Kit | TASK-046 | DONE |
| TASK-048 | M8 | Ecosystem Hub | TASK-047 | DONE |
| TASK-049 | M8 | Certification | TASK-048 | DONE |
| TASK-050 | M9 | Autonomous Goal Engine | TASK-049 | DONE |
| TASK-051 | M9 | Autonomous Planner | TASK-050 | DONE |
| TASK-052 | M9 | World Model | TASK-051 | DONE |
| TASK-053 | M9 | Autonomous Loop | TASK-051 | DONE |
| TASK-054 | M9 | Autonomy Governor | TASK-053 | DONE |
| TASK-055 | M9 | Autonomous Recovery | TASK-054 | DONE |
| TASK-056 | M9 | Goal Durability | TASK-055 | DONE |
| TASK-057 | M9 | Autonomous Memory | TASK-056 | DONE |
| TASK-058 | M9 | Autonomous Experimentation | TASK-057 | DONE |
| TASK-059 | M9 | Multi-Agent Autonomy | TASK-058 | DONE |
| TASK-060 | M9 | Autonomous Evaluation | TASK-059 | DONE |
| TASK-061 | M9 | Advanced Stuck Detection | TASK-060 | DONE |
| TASK-062 | M9 | Autonomous Scheduler | TASK-054 | DONE |
| TASK-063 | M10 | AIOS Architecture 1.0 | TASK-062 | DONE |
| TASK-064 | M10 | Public Contract Freeze | TASK-063 | DONE |
| TASK-065 | M10 | Runtime Production Hardening | TASK-064 | DONE |
| TASK-066 | M10 | Durable Execution 1.0 | TASK-065 | DONE |
| TASK-067 | M10 | Autonomy Safety 1.0 | TASK-066 | DONE |
| TASK-068 | M10 | Kill Switch | TASK-067 | DONE |
| TASK-069 | M10 | Reliability Engineering | TASK-068 | DONE |
| TASK-070 | M10 | AIOS Security Baseline | TASK-069 | DONE |
| TASK-071 | M10 | AIOS 1.0 Developer Experience | TASK-070 | DONE |
| TASK-072 | M10 | AIOS Dashboard 1.0 | TASK-071 | DONE |
| TASK-073 | M10 | AIOS 1.0 Certification Suite | TASK-072 | DONE |
| TASK-074 | M10 | Upgrade & Migration 1.0 | TASK-073 | DONE |
| TASK-075 | M10 | Performance & Cost + Model Independence | TASK-074 | DONE |
| TASK-076 | M11 | Reserved / Not Specified in Source | TASK-075 | DONE |
| TASK-077 | M11 | Reserved / Not Specified in Source | TASK-076 | DONE |
| TASK-078 | M11 | Verification Integrity / Fail-Closed Gate | TASK-077 | DONE |
| TASK-079 | M11 | RenderReplay / Deterministic Harness | TASK-078 | DONE |
| TASK-080 | M11 | Visual Evidence + Visual Regression + UI State Contract | TASK-079 | DONE |
| TASK-081 | M11 | Asset Pipeline + Asset Capability Registry + Routing | TASK-080 | DONE |
| TASK-082 | M11 | Creative Domain + Vendor Integrity + Reference Asset | TASK-081 | DONE |
| TASK-083 | M11 | SkillDistiller + Static Deploy | TASK-082 | DONE |
| TASK-219 | M11 | GitHub Skill → AIOS Skill Plugin Bridge | TASK-083 | DONE |
| TASK-084 | M12 | Version + Compatibility Baseline | TASK-083 | DONE |
| TASK-085 | M12 | Migration 1.0 → 1.1 | TASK-084 | DONE |
| TASK-086 | M12 | Backward Compatibility | TASK-085 | DONE |
| TASK-087 | M12 | Compatibility Conformance | TASK-086 | DONE |
| TASK-088 | M12 | Docs & ADR — Compatibility | TASK-087 | DONE |
| TASK-089 | M13 | Behavioral Conformance | TASK-088 | DONE |
| TASK-090 | M13 | Harness Coverage + Readiness | TASK-089 | DONE |
| TASK-091 | M13 | Meta-Harness / Verify-the-Verifier | TASK-090 | DONE |
| TASK-092 | M13 | System Readiness vs Harness Trust | TASK-091 | DONE |
| TASK-093 | M13 | Behavioral Spec + ADR-0008 | TASK-092 | DONE |
| TASK-094 | M14 | Detect + Diagnose | TASK-093 | DONE |
| TASK-095 | M14 | Candidate Generation + Risk Scoring | TASK-094 | DONE |
| TASK-096 | M14 | Simulation + Meta-Verification Gate | TASK-095 | DONE |
| TASK-097 | M14 | Permission + Human Approval + Apply + Re-test + Rollback + Certification | TASK-096 | DONE |
| TASK-098 | M14 | Remediation Integrity + Kill Switch | TASK-097 | DONE |

| TASK-099 | M15 | Autonomous Harness Loop | TASK-098 | DONE |
| TASK-100 | M15 | Failure-Corpus Improvement Engine | TASK-099 | DONE |
| TASK-101 | M15 | Continuous Certification | TASK-100 | DONE |
| TASK-102 | M15 | Trust Budget + Autonomy Levels + SAFE-STOP | TASK-101 | DONE |
| TASK-103 | M15 | Autonomy Constitution + Audit Trail | TASK-102 | DONE |

| TASK-104 | M16 | Independent Harness Integration Foundation | TASK-103 | DONE |
| TASK-105 | M16 | Independent Verification Oracle | TASK-104 | DONE |
| TASK-106 | M16 | Behavioral Conformance Bridge | TASK-105 | DONE |
| TASK-107 | M16 | Permission + Sandbox Bridge | TASK-106 | DONE |
| TASK-108 | M16 | Management Console / Independent Harness Integration | TASK-107 | DONE |

| TASK-109 | M17 | Model Contracts | TASK-108 | DONE |
| TASK-110 | M17 | Provider Registry + Lifecycle | TASK-109 | DONE |
| TASK-111 | M17 | Model Registry + Deterministic Resolver | TASK-110 | DONE |
| TASK-112 | M17 | Inference Runtime Orchestration | TASK-111 | DONE |
| TASK-113 | M17 | Credential + Permission + Policy Integration | TASK-112 | DONE |
| TASK-114 | M17 | Retry / Timeout / Streaming / Cancellation | TASK-113 | DONE |
| TASK-115 | M17 | Usage / Cost / Audit / Evidence | TASK-114 | DONE |
| TASK-116 | M17 | Provider Conformance + Certification | TASK-115 | DONE |

| TASK-117 | M18 | Repository Scanner | TASK-116 | DONE |
| TASK-118 | M18 | Source / Symbol Index | TASK-117 | DONE |
| TASK-119 | M18 | Dependency Graph | TASK-118 | DONE |
| TASK-120 | M18 | Semantic + Hybrid Index | TASK-119 | DONE |
| TASK-121 | M18 | Context Retriever | TASK-120 | DONE |
| TASK-122 | M18 | Context Builder + Budget | TASK-121 | DONE |
| TASK-123 | M18 | Context Verification + Evidence | TASK-122 | DONE |
| TASK-124 | M18 | Context Harness + Conformance | TASK-123 | DONE |

| TASK-125 | M19 | Coder Agent Contract + State Machine | TASK-124 | DONE |
| TASK-126 | M19 | Coding Planner + PlanVerifier | TASK-125 | DONE |
| TASK-127 | M19 | Code Generation Runtime | TASK-126 | DONE |
| TASK-128 | M19 | Patch Engine | TASK-127 | DONE |
| TASK-129 | M19 | Code Review Agent | TASK-128 | DONE |
| TASK-130 | M19 | Coding Artifact + CodingEvidence | TASK-129 | DONE |
| TASK-131 | M19 | Coder Conformance Harness + Security | TASK-130 | DONE |
| TASK-132 | M19 | Autonomy Level + Permission Integration | TASK-131 | DONE |
| TASK-133 | M19 | Prompt Architecture + PromptBuilder + Versioning | TASK-132 | DONE |
| TASK-134 | M19 | File Safety Boundary + Scope Enforcement | TASK-133 | DONE |

| TASK-135 | M20 | Execution Contract | TASK-134 | DONE |
| TASK-136 | M20 | Sandbox Manager | TASK-135 | DONE |
| TASK-137 | M20 | Workspace / Snapshot Manager | TASK-136 | DONE |
| TASK-138 | M20 | Resource + Network + Command Policy | TASK-137 | DONE |
| TASK-139 | M20 | Test Runner | TASK-138 | DONE |
| TASK-140 | M20 | Build / Lint Runner | TASK-139 | DONE |
| TASK-141 | M20 | Output + Artifact Collector | TASK-140 | DONE |
| TASK-142 | M20 | Verification Engine | TASK-141 | DONE |
| TASK-143 | M20 | Security + Replay Harness | TASK-142 | DONE |
| TASK-144 | M20 | Execution Evidence + Conformance | TASK-143 | DONE |

| TASK-145 | M21 | Coding Loop State Machine | TASK-144,TASK-053,TASK-050 | DONE |
| TASK-146 | M21 | Execution Observation | TASK-145,TASK-135,TASK-141 | DONE |
| TASK-147 | M21 | Failure Classification | TASK-146,TASK-135 | DONE |
| TASK-148 | M21 | Diagnostic Agent | TASK-147,TASK-146 | DONE |
| TASK-149 | M21 | Repair Planner | TASK-148,TASK-026,TASK-055 | DONE |
| TASK-150 | M21 | Progress + Regression Detection | TASK-149,TASK-033,TASK-055 | DONE |
| TASK-151 | M21 | Verification Gate | TASK-150,TASK-142,TASK-078 | DONE |
| TASK-152 | M21 | Context Refresh + Patch Chain | TASK-151,TASK-024,TASK-137 | DONE |
| TASK-153 | M21 | Autonomous Safety Controller | TASK-152,TASK-067,TASK-068 | DONE |
| TASK-154 | M21 | Autonomous Coding Harness | TASK-145,TASK-146,TASK-147,TASK-148,TASK-149,TASK-150,TASK-151,TASK-152,TASK-153,TASK-029,TASK-031,TASK-032 | DONE |

| TASK-155 | M22 | Requirement → Evidence Mapping | TASK-144,TASK-142,TASK-001 | DONE |
| TASK-156 | M22 | Test Adequacy Analyzer + Mutation Verifier | TASK-155,TASK-031,TASK-142 | DONE |
| TASK-157 | M22 | Behavioral Verifier | TASK-155,TASK-032,TASK-142 | DONE |
| TASK-158 | M22 | Contract Verifier | TASK-155,TASK-135,TASK-064,TASK-142 | DONE |
| TASK-159 | M22 | Regression Verifier | TASK-155,TASK-033,TASK-142 | DONE |
| TASK-160 | M22 | Security Verifier | TASK-155,TASK-143,TASK-070,TASK-142 | DONE |
| TASK-161 | M22 | Performance Verifier | TASK-155,TASK-021,TASK-075,TASK-142 | DONE |
| TASK-162 | M22 | Replay & Flaky Detector | TASK-155,TASK-030,TASK-079,TASK-142 | DONE |
| TASK-163 | M22 | Evidence Collector + Evidence Integrity | TASK-155,TASK-141,TASK-078,TASK-001 | DONE |
| TASK-164 | M22 | Trust Evaluator + CodingCertificate + Verification Harness | TASK-155,TASK-156,TASK-157,TASK-158,TASK-159,TASK-160,TASK-161,TASK-162,TASK-163,TASK-049,TASK-046,TASK-142 | DONE |

| TASK-165 | M23 | Adversarial Evaluation Harness | TASK-164,TASK-029,TASK-031,TASK-001 | DONE |
| TASK-166 | M23 | Evidence Attackers | TASK-165,TASK-163,TASK-078 | DONE |
| TASK-167 | M23 | Test Weakness Attackers | TASK-165,TASK-156,TASK-142 | DONE |
| TASK-168 | M23 | Requirement / Scope Attackers | TASK-165,TASK-155 | DONE |
| TASK-169 | M23 | Certificate Attackers | TASK-165,TASK-164,TASK-049,TASK-046 | DONE |
| TASK-170 | M23 | Prompt Injection Tester + Untrusted Artifact Isolation | TASK-165,TASK-040,TASK-113,TASK-136 | DONE |
| TASK-171 | M23 | Execution Integrity Attackers | TASK-165,TASK-135,TASK-078,TASK-030,TASK-079 | DONE |
| TASK-172 | M23 | Environment / Dependency Attackers | TASK-165,TASK-136,TASK-137,TASK-040 | DONE |
| TASK-173 | M23 | Boundary Attackers | TASK-165,TASK-153,TASK-067,TASK-068 | DONE |
| TASK-174 | M23 | Collusion Detector + Resilience Score + Attack Corpus Regression | TASK-165,TASK-166,TASK-167,TASK-168,TASK-169,TASK-170,TASK-171,TASK-172,TASK-173,TASK-033 | DONE |

| TASK-175 | M24 | Quality Gate + Gate States | TASK-164,TASK-151,TASK-001 | DONE |
| TASK-176 | M24 | Risk Model + Classification | TASK-175,TASK-164 | DONE |
| TASK-177 | M24 | Policy Engine + Profiles + Precedence | TASK-176,TASK-113,TASK-138 | DONE |
| TASK-178 | M24 | Exception Management | TASK-177,TASK-097,TASK-055 | DONE |
| TASK-179 | M24 | Quality Debt Tracking | TASK-178,TASK-175,TASK-021 | DONE |
| TASK-180 | M24 | Release Gate + Decision Explainability | TASK-175,TASK-179,TASK-181 | DONE |
| TASK-181 | M24 | Governance Ledger + Provenance Graph | TASK-180,TASK-001,TASK-078 | DONE |
| TASK-182 | M24 | Trust Lifecycle + Invalidation + Selective Reverification | TASK-181,TASK-164,TASK-049,TASK-046 | DONE |
| TASK-183 | M24 | Approval Workflow + Rollback Recommendation | TASK-182,TASK-097,TASK-055 | DONE |
| TASK-184 | M24 | Quality Dashboard + Governance Harness | TASK-175,TASK-176,TASK-177,TASK-178,TASK-179,TASK-180,TASK-181,TASK-182,TASK-183,TASK-072,TASK-021 | DONE |

| TASK-185 | M25 | Coding Evaluation Contract | TASK-032,TASK-001 | DONE |
| TASK-186 | M25 | Evaluation Engine | TASK-185,TASK-032,TASK-078 | DONE |
| TASK-187 | M25 | Quality Dimensions | TASK-186,TASK-185 | DONE |
| TASK-188 | M25 | Benchmark Registry | TASK-187,TASK-033,TASK-185 | DONE |
| TASK-189 | M25 | Baseline Manager | TASK-188,TASK-033 | DONE |
| TASK-190 | M25 | Regression Detector | TASK-189,TASK-159,TASK-033 | DONE |
| TASK-191 | M25 | Agent Behavior Evaluator | TASK-186,TASK-157,TASK-187 | DONE |
| TASK-192 | M25 | Efficiency Evaluator | TASK-186,TASK-161,TASK-187 | DONE |
| TASK-193 | M25 | Failure Attribution | TASK-186,TASK-148,TASK-147 | DONE |
| TASK-194 | M25 | Evaluation Store | TASK-186,TASK-185,TASK-163,TASK-001 | DONE |
| TASK-195 | M25 | Model / Agent Benchmark | TASK-188,TASK-189,TASK-186,TASK-190 | DONE |
| TASK-196 | M25 | Continuous Evaluation | TASK-185,TASK-186,TASK-187,TASK-188,TASK-189,TASK-190,TASK-191,TASK-192,TASK-193,TASK-194,TASK-195,TASK-021 | DONE |

| TASK-197 | M26 | Unified Coding Contract | TASK-125,TASK-185,TASK-001 | DONE |
| TASK-198 | M26 | Coding State Machine | TASK-197,TASK-125,TASK-145 | DONE |
| TASK-199 | M26 | Coding Policy Engine | TASK-198,TASK-177,TASK-113 | DONE |
| TASK-200 | M26 | Risk Engine | TASK-199,TASK-176,TASK-164 | DONE |
| TASK-201 | M26 | Approval Gate | TASK-200,TASK-183,TASK-097 | DONE |
| TASK-202 | M26 | Autonomous Guardrails | TASK-201,TASK-153,TASK-067,TASK-068 | DONE |
| TASK-203 | M26 | Safe Stop / Resume | TASK-202,TASK-102,TASK-068 | DONE |
| TASK-204 | M26 | Recovery Orchestrator | TASK-203,TASK-055,TASK-094 | DONE |
| TASK-205 | M26 | Artifact Lineage | TASK-204,TASK-130,TASK-078 | DONE |
| TASK-206 | M26 | Coding Session | TASK-205,TASK-198,TASK-125 | DONE |
| TASK-207 | M26 | Session Fork | TASK-206,TASK-137,TASK-136 | DONE |
| TASK-208 | M26 | Multi-Agent Coding | TASK-207,TASK-059,TASK-125 | DONE |
| TASK-209 | M26 | Parallel Coding | TASK-208,TASK-028,TASK-206 | DONE |
| TASK-210 | M26 | Change Impact Analysis | TASK-209,TASK-119,TASK-121 | DONE |
| TASK-211 | M26 | Repository Knowledge Graph Integration | TASK-210,TASK-117,TASK-007 | DONE |
| TASK-212 | M26 | Coding Doctor | TASK-211,TASK-034,TASK-021 | DONE |
| TASK-213 | M26 | Coding Health Score | TASK-212,TASK-187,TASK-186 | DONE |
| TASK-214 | M26 | Release Gate | TASK-213,TASK-180,TASK-175 | DONE |
| TASK-215 | M26 | Coding Certification | TASK-214,TASK-049,TASK-164 | DONE |
| TASK-216 | M26 | Benchmark Gate | TASK-215,TASK-195,TASK-033 | DONE |
| TASK-217 | M26 | AIOS 2.0 Coding Integration | TASK-197,TASK-198,TASK-199,TASK-200,TASK-201,TASK-202,TASK-203,TASK-204,TASK-205,TASK-206,TASK-207,TASK-208,TASK-209,TASK-210,TASK-211,TASK-212,TASK-213,TASK-214,TASK-215,TASK-216,TASK-021 | DONE |
| TASK-218 | M26 | Full M0–M26 Regression | TASK-217,TASK-001,TASK-033 | DONE |

## Next action

M26 `DONE` (3138 tests, M26 full: T197-T218 implemented in `aios/coding_edition/`, AC-197..218 PASS). M26 COMPLETE — final milestone of roadmap M0-M26. ALL TASKS 001-218 + TASK-219 DONE. Roadmap M0-M26 CLOSED (2026-08-24).

## M27 — Control-Plane Extension (post-M26)

| TASK-220 | M27 | AIOS Coordinator Agent (control-plane + chat agent) | TASK-001,TASK-008,TASK-125 | DONE |
| TASK-221 | M27 | Coordinator Chat API Endpoint | TASK-220,TASK-017 | DONE |
| TASK-222 | M27 | Real Executor + CLI `execute` (practical usage) | TASK-221,TASK-008,TASK-005 | DONE |
| TASK-223 | M27 | AIOS Planner Agent + Skill (request → plan.yaml) | TASK-222,TASK-008 | DONE |
| TASK-224 | M27 | Planner confirm flow + `work/` directory convention | TASK-223,TASK-222 | DONE |
| TASK-225 | M28 | AIOS Self-Improver Agent | TASK-220,TASK-001,TASK-005 | DONE |
| TASK-226 | M28 | Deterministic Auto-Stop / RetryGuard | TASK-225,TASK-005,TASK-001 | DONE |
| TASK-227 | M28 | StubGuard: reject null-stub / SKIPPED steps | TASK-225,TASK-005,TASK-001 | DONE |
| TASK-228 | M29 | Unified ExecutionPlan Contract | TASK-222,TASK-008,TASK-010,TASK-001 | DONE |
| TASK-229 | M29 | Unified Execution Entry-Point (Governance-aware execute) | TASK-228,TASK-222,TASK-226,TASK-001 | DONE |
| TASK-230 | M30 | Coder Agent ↔ Capability Registry | TASK-218,TASK-009,TASK-001 | DONE |
| TASK-231 | M30 | CodingEdition ↔ RealToolHandler | TASK-230,TASK-222,TASK-218,TASK-001 | DONE |
| TASK-232 | M30 | Automated Test / Static Analysis + Code Provenance | TASK-231,TASK-005,TASK-001 | DONE |
| TASK-233 | M31 | Unified Autonomous Lifecycle | TASK-229,TASK-232,TASK-226,TASK-041,TASK-001 | DONE |
| TASK-234 | M32 | Automatic Evidence Generation | TASK-229,TASK-005,TASK-001 | DONE |
| TASK-235 | M32 | Evidence Quality & Integrity | TASK-234,TASK-030,TASK-032,TASK-001 | DONE |
| TASK-236 | M33 | Unified Remediation Lifecycle | TASK-233,TASK-011,TASK-041,TASK-001 | DONE |
| TASK-237 | M34 | Unified Control Center Dashboard | TASK-229,TASK-234,TASK-236,TASK-017,TASK-018,TASK-001 | PLANNED |
| TASK-238 | M35 | Self-Evolution Lifecycle | TASK-225,TASK-233,TASK-235,TASK-029,TASK-001 | PLANNED |

M29–M35 (phase "AIOS 2.x — Operational Integration & Autonomous Coding OS") adds
11 PLANNED tasks (TASK-228 → TASK-238) that **connect existing planes into one
unified control/execution/evidence loop** instead of adding new subsystems. M29
(T228–T229) makes `aiagent execute` governance-aware (closes Flow B gap); M30
(T230–T232) wires `CodingEdition` ↔ `RealToolHandler` so the Coding Plane writes
real code (closes Flow H gap); M31 (T233) unifies the autonomous loop; M32
(T234–T235) makes evidence-native; M33 (T236) adds self-healing; M34 (T237)
upgrades the Dashboard to a Control Center; M35 (T238) adds the self-evolution
lifecycle. Full specs: `docs/AIOS_Master_Task_Specification_M29-M35.md`.

M27 opens a lightweight control-plane layer: `CoordinatorAgent` (pure, I/O-free,
capability-injected) drives the agent-role pipeline (spec → critique×2 →
breakdown → review → orchestrate/close) and a custom VS Code chat agent
(`.github/agents/aios-coordinator.agent.md`) lets users pick it from the chat
picker and auto-follow the governance next-step loop. TASK-221 adds a REST
endpoint (`POST /api/v1/coordinator/run`, `GET /{task_id}`) bridging the chat
UI to `CoordinatorAgent`. TASK-222 adds real execution: `aios/runtime/process.py`
(`RealToolHandler`) runs real OS commands (shell/git/file) gated by
Policy/Permission, wired into `RuntimeKernel` (opt-in `real_execution.enabled`),
exposed via `aiagent execute <plan>` (YAML/JSON/Markdown). TASK-223 closes the
front-door loop: `.github/agents/aios-planner.agent.md` + `.github/skills/aios-plan/SKILL.md`
turn a natural-language request into a runnable `plan.yaml` (WorkflowDefinition with
real `command`s) that `aiagent execute` runs. TASK-224 refines the loop: the planner
agent ASKS the user to confirm before executing, and all work is isolated under
`work/YYYYMMDD-slug/` (plan + generated source), with `aiagent execute --work-dir <dir>
--yes` confining execution to that folder (sandbox `allowed_cwd`). No LLM / external API
required — suitable for weak/offline machines. Unified Gate PASS; 3161+ tests green
(2026-08-24).

## Known implementation gaps (audit 2026-08-22) — CLOSED 2026-08-22

All gaps listed below were **implemented** in the session of 2026-08-22, bringing
each `aios/<package>/` implementation to meet its `docs/detailtask/` acceptance
criteria. Each task's new modules are covered by dedicated tests (see per-task
`tests/` files). Full suite: **1962 passed**.

- **T021** Observability → added `observability/health_api.py` + `dashboard.py` (fail-closed UNKNOWN≠PASS).
- **T023** Memory Coordinator → `filters`/`ranking_policy` on `MemoryQuery`, `provenance`/`checksum`/`scope` on `MemoryCandidate`, `filter.py` + retrieval observability.
- **T024** Context Optimizer → `ExtractiveCompressor`+`LLMCompressor`, priority enum aligned, non-ASCII bug fixed.
- **T025** Model Router → `FallbackResolver` fallback chain + extended `ModelRequirement`/`ModelCandidate`.
- **T028** Parallel Scheduler → `DispatchDecision` enum + `ANY_SUCCESS`/`ALL_COMPLETED` join policies.
- **T029** Harness Kernel → `HarnessRegistry` (AC-029-02) + `HarnessContext`/`HarnessEvent`/`HarnessArtifact`/`HarnessReport`.
- **T030** Execution Verification → `ReplayEngine` + expanded `EvidencePackage`.
- **T031** Test Harness → `test_harness.py` (`FakeRuntime`/`FakeTool`/`GoldenScenario`/`TestHarness`/`run_harness_test`).
- **T032** Evaluation Harness → `evaluators.py` (Evaluator base + Deterministic/Semantic/LLM/Human/Composite + trajectory eval).
- **T033** Benchmark → `GateEvaluator` (PASS/WARNING/FAIL/INCONCLUSIVE) + named primitives.
- **T034** Doctor + Readiness → `readiness.py` (13 domain doctors + `ReadinessEngine` fail-closed).
- **T035** Identity + RBAC → `abac.py` + `delegation.py` (ABAC engine, delegation w/ attenuation).
- **T036** Multi-Tenancy → `Organization`/`Project`/`Workspace`/`TenantContext` + `resolve_scope`/`assert_same_tenant`/`filter_by_tenant`.
- **T041** HA + Audit + Recovery → `health.py`/`lease.py`/`recovery.py`/`audit.py` (hash-chained audit, single-active lease).
- **T042** Enterprise Operations → `metrics.py`/`health.py` + tenant-scoped operations.
- **T043** Public SDK → error model + `SDKVersion` compat + `MockAIOSClient` + `discovery.py`.
- **T044** Plugin Runtime → `manifest.py`/`resolver.py` + validate-before-load/rollback/snapshots.
- **T045** Extension Contracts → `ExtensionContext` + `compatibility.py`/`evidence.py` + boundary check.
- **T046** Ecosystem Registry → `TrustState` + search/resolve_version/is_compatible/set_trust/checksum.
- **T047** Developer Kit → `manifest.py`/`packaging.py`/`cli.py` (`create`/`validate`/`test`/`simulate`/`package`/`inspect`).
- **T048** Ecosystem Hub → search/is_compatible/install via PluginRuntime + checksum/provenance.
- **T049** Certification → `pipeline.py` + profiles/checks/revocation reasons/expiry.
- **T050** Autonomous Goal Engine → `state_machine.py`/`policy.py` + objectives/progress/policy boundary/evidence.

## M10 implementation (2026-08-22)

M10 (Architecture 1.0) froze the 1.0 baseline and added production hardening,
safety, security, reliability and certification controls. New packages:
`aios/contracts` (T064), `aios/durable` (T066), `aios/autonomy_safety` (T067),
`aios/kill_switch` (T068), `aios/reliability` (T069), `aios/cost_meter` (T075);
extended: `aios/governance/architecture` (T063 ADR + baseline), `aios/runtime`
(T065 hardening), `aios/security` (T070), `aios/devkit`+`aios/cli` (T071),
`aios/dashboard` (T072), `aios/certification` (T073 release certifier),
`aios/upgrade` (T074 migration engine), `aios/model_router` (T075 routing).
Full suite: **2272 passed** (was 1962; +310 M10 tests). All 13 M10 tasks PASS
the unified gate (lifecycle artifacts + architecture guard + full CI suite).

### Minor governance-artifact inconsistencies (still open, non-blocking)
- Task-folder `implementation/` dirs are empty for T015, T016, T029, T041, T044, T045, T049, T050 (real code lives in `aios/<package>/`).
- Regression artifact casing inconsistent: `REGRESSION.md` (uppercase) for T011/012/013/014/016/017 vs canonical `regression.md` (lowercase) elsewhere.
