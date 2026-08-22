# AIOS — Agent Instructions

> Runtime-First · Plugin-First · Offline-First · Harness-Verified · Coding-Plane
> Read with [`docs/PLAN.md`](docs/PLAN.md) and [`aios/progress/README.md`](aios/progress/README.md) — together they are sufficient to continue without chat memory.

## 1. Quick start (new session)

1. Read `docs/PLAN.md` → `AGENTS.md` → `aios/progress/README.md`.
2. `pip install -e ".[dev]"` (requires Python ≥3.11, `pyyaml` only runtime dep). To run the **full** suite or API tests (`test_api.py`) also install the API extra — `pip install -e ".[dev,api]"` — otherwise `pytest aios` fails with `ModuleNotFoundError: fastapi` (the recurring CI breakage).
3. `python -m pytest aios -q` — must stay green; coverage `fail_under: 80` ([`pyproject.toml`](pyproject.toml)).
4. Pick next `READY` task from `aios/progress/PLAN.md` (check `DependencyGraph.is_ready`).

**Key CLIs**

```bash
python -m pytest aios -q                          # all gates
python -m pytest aios/governance/architecture -q  # architecture gate only
python aios/governance/cli/gate_check.py --task TASK-001
python aios/governance/cli/parse_spec.py          # registry + dependency validation
aiagent validate  |  aiagent simulate            # workflow CLI (aios/cli/workflow_cli.py)
```

**Config:** [`configs/default.yaml`](configs/default.yaml) (`log_level`, `log_format: json`, `config_dir: .aios`, `healthcheck_timeout: 5.0`, `metadata_cache_ttl: 300`). Overridden by `AIOS_*` env vars via `aios.core.config.Config`.

## 2. Architecture — layering is enforced

```
Agent -> Orchestrator -> Runtime -> Capability -> Tool
```

Imports must only go **downward**. Enforced by [`aios/governance/architecture/guard.py`](aios/governance/architecture/guard.py) (`ArchitectureGuard.check()`). Violations **BLOCK** the task.

| Rule | What it forbids (agents) |
|------|--------------------------|
| ARCH-001 | `subprocess`, `os` execution primitives |
| ARCH-002 | provider adapters (`aios.core.providers`, `aios.runtime.providers`, `providers`, …) |
| ARCH-003 | filesystem adapters (`aios.runtime.filesystem`, `filesystem`, …) |
| ARCH-004 | upward / skip-layer import (e.g. `tool` → `runtime`) |

`LAYER_ORDER = ["agent","orchestrator","runtime","capability","tool"]`; classification via `LAYER_KEYWORDS`. Agents obtain capabilities **only** through interfaces injected by orchestrator/runtime — never import provider/tool internals directly.

## 3. Project layout

```
aios/
  governance/  task_registry/ dependency/ architecture/ deterministic/ evidence/ lifecycle/ regression/ gates/ cli/
  runtime/     kernel.py context.py audit.py artifact.py permission.py policy.py execution.py scheduler.py state.py resource.py memory.py knowledge.py providers/ workflow/
  core/        config.py logging.py metadata.py healthcheck.py version.py contracts.py container.py events.py planner.py
  agents/      orchestrator.py spec_writer.py critic.py reviewer.py
  harness/     placeholder (M6)
  cli/         workflow_cli.py  (entry: aiagent)
  progress/    PLAN.md LOG.md STATS.md tasks/<TASK-xxx>/ _TEMPLATE/
configs/ default.yaml development.yaml test.yaml
docs/ PLAN.md AGENTS.md AIOS_Master_Task_Specification_M0-M26.md detailtask/
```

See [`aios/progress/README.md`](aios/progress/README.md) for task-folder standard (`spec.md`, `critique-1/2.md`, `tasks.md`, `review.md`, `implementation/`, `test.md`, `evaluation.md`).

## 4. Agent roles (pure, I/O-free)

| Agent | File | Contract |
|-------|------|----------|
| **Orchestrator** | `aios/agents/orchestrator.py` | Drives `TaskLifecycle`; only marks `DONE` after `UnifiedTaskGate` passes; coordinates spec-writer/critic/reviewer |
| **Spec-Writer** | `aios/agents/spec_writer.py` | `SpecInput` → `spec.md`; pure text transform, no I/O or provider access |
| **Critic** | `aios/agents/critic.py` | Produces `critique-1.md` / `critique-2.md`; flags missing spec sections |
| **Reviewer** | `aios/agents/reviewer.py` | Produces `review.md`; verifies pre-implementation artifacts present |

Keep agents deterministic and side-effect free. All I/O, provider calls and filesystem access go through Runtime.

## 5. Governance — 7 gates → Unified Task Gate + Rule 8 Auto-COMMIT

Workflow: `PLAN → SPEC → CRITIQUE×2 → BREAKDOWN → REVIEW → IMPLEMENT → TEST → EVALUATE → REGRESSION → PROGRESS/LOG → COMMIT`

> **Quy tắc 8 — Auto-COMMIT (scheduled TASK):** mọi TASK đã lên lịch trong `docs/AIOS_Master_Task_Specification_M0-M26.md` khi đạt `DONE` (Unified Gate `PASS`) phải `COMMIT` source **ngay trong cùng phiên** — không để working tree bẩn sang task sau. Commit message chuẩn `TASK-xxx: <title> — DONE` kèm cập nhật `aios/progress/PLAN.md`, `LOG.md`, `STATS.md` và evidence liên quan. `COMMIT` là bước bắt buộc của Definition of Done, không được trì hoãn.

[`aios/governance/gates/unified.py`](aios/governance/gates/unified.py): `UnifiedTaskGate` is logical AND of all gates; any exception → `FAIL` (fail-closed). `DONE` only on `PASS`.

| Rule | Module | Gate |
|------|--------|------|
| 1 Registry | `governance/task_registry/` | IDs unique/immutable/never-reused; `deprecate()` is soft-delete |
| 2 Dependency | `governance/dependency/graph.py` | DAG `A→B` = depends-on; `get_closure()`, `detect_cycle()` (DFS), `is_ready()` |
| 3 Architecture | `governance/architecture/` | §2 above |
| 4 Deterministic | `governance/deterministic/pipeline.py` | §6 below |
| 5 Evidence | `governance/evidence/store.py` | §7 below |
| 6 Lifecycle | `governance/lifecycle/statemachine.py` | 12 states `PLANNED→…→DONE`; `transition()` rejects missing artifacts / backward moves |
| 7 Regression | `governance/regression/runner.py` | Iterates sorted closure; first `FAIL` → `blocked=True` |

**Lifecycle artifacts** (`STATE_ARTIFACTS`): `SPECIFIED:spec.md`, `CRITIQUED_1:critique-1.md`, `CRITIQUED_2:critique-2.md`, `BROKEN_DOWN:tasks.md`, `REVIEWED:review.md`, `IMPLEMENTING:implementation/`, `TESTING:test.md`, `EVALUATING:evaluation.md`, `REGRESSION:regression.md`.

**Audit workflow** (khi user nói "Kiểm tra … có đầy đủ chưa"): chạy `python aios/governance/cli/gate_check.py --task TASK-00X` + `python -m pytest aios -q` rồi xuất bảng `| # | AC từ detailtask/ | File | Status | Evidence |` — link tới [`docs/detailtask/`](docs/detailtask/).

## 6. Deterministic-first (Rule 4)

Never call an LLM as the default path. [`governance/deterministic/pipeline.py`](aios/governance/deterministic/pipeline.py):

`Request → Normalizer → RuleEngine(SUFFICIENT|INSUFFICIENT) → WorkflowMatcher → CapabilityResolver → Policy.check → ExecutionPlan`

* `KNOWN_INTENTS = {status,health,help,list tasks}` → `SUFFICIENT` (`handle:<intent>`, `llm_call_count==0`).
* Else `INSUFFICIENT` → `llm_fallback()` only here, optional `validator(raw)`; `ValidationError` on fail.

## 7. Evidence & provenance (Rule 5)

`Evidence → Run → Artifact → Task → Requirement` — `UNKNOWN` never promoted to `PASS`. See [`governance/evidence/store.py`](aios/governance/evidence/store.py).

* `Evidence` requires `evidence_id, task_id, run_id, producer, type, source, content_hash=sha256(content)`.
* `EvidenceStore` holds 5 registries; `get_provenance_chain(evidence_id)` must be complete.

## 8. Runtime kernel

[`aios/runtime/kernel.py`](aios/runtime/kernel.py) is the composition root: `Container` wires `EventBus → ContextStore/AuditTrail/ArtifactStore/PermissionBroker → PolicyEngine → Scheduler/StateStore/ResourcePool/MemoryStore/KnowledgeIndex → Executor(Policy→Resource→Scheduler→State)`.

Use `aios.core.container` (singleton/scoped/transient, thread-safe), `aios.core.events` (ordered dispatch), `aios.runtime.permission` + `policy` (pre-check), `aios.runtime.execution` (retry/cancel/timeout), `aios.runtime.providers` (Mock/OpenAI/Ollama via contract).

## 9. Memory & Knowledge (TASK-007)

* `aios/runtime/memory.py`: `MemoryStore` lifecycle `put → update(supersedes) → archive → expire`; `MemoryEntry.create(type, scope, content)`; `list_active()` excludes `ARCHIVED`/`EXPIRED`.
* `aios/runtime/knowledge.py`: `KnowledgeIndex` + `KnowledgeChunker(chunk_size, overlap)` + `KnowledgeSource`; chunks carry `source_id`, `document_id`, `location{chunk_index,char_start,content_hash}`, `verify()`; `ingest_chunks()` → `verify_chunks()`; `search_chunks()` / `search()` support `metadata_filter` and `evidence()` with provenance.

## 10. Conventions & pitfalls

* **Python ≥3.11**, `pyyaml` only runtime dep. Run `pip install -e ".[dev]"` before `pytest`; `pip install -e ".[api]"` for FastAPI (`TASK-017+` only), `pip install -e ".[dev,api]"` for both. `fastapi`/`pydantic`/`uvicorn` are **not** in base deps — `ModuleNotFoundError: fastapi` before TASK-017 is expected.
* **fastapi pre-flight (bắt buộc cho TASK-017+ / API):** trước khi claim DONE hoặc chạy API test, chạy `python -c "import fastapi"`; nếu fail thì `pip install -e ".[dev,api]"` rồi verify lại. Tuyệt đối không để user phải hỏi "sao chạy import fastapi bị lỗi" — pre-flight này phải chạy tự động trước mọi API work.
* **Never** add `subprocess`/`os`/provider/filesystem imports inside `aios/agents/` — architecture gate fails closed on parse errors too.
* **Never** bypass Runtime/Capability/Permission/Policy — agents receive capabilities via injection.
* **Naming:** task IDs `TASK-xxx` are immutable and never reused, even after deprecation.
* **Artifacts:** respect `STATE_ARTIFACTS` mapping; `can_close()` requires `READY_TO_CLOSE` + `missing_for_done()==[]`.
* **Auto-COMMIT (Quy tắc 8):** TASK đã lên lịch trong `AIOS_Master_Task_Specification_M0-M26.md` khi đạt `DONE` phải commit ngay trong cùng phiên (`TASK-xxx: <title> — DONE` + `PLAN.md`/`LOG.md`/`STATS.md`); cấm để working tree bẩn sang task sau.
* **Spec-first:** trước khi claim `PASS`/`DONE`, phải đọc `docs/detailtask/T00X.md` + `aios/progress/tasks/TASK-00X/` và đối chiếu từng AC trong bảng — không đoán.
* **Không khôi phục:** khi user nói "không khôi phục / làm lại từ đầu / không được khôi phục", xóa/recreate từ `aios/progress/tasks/_TEMPLATE/` — không reuse `implementation/` cũ.
* **Chẩn đoán trước khi retry (bắt buộc):** cấm `Try Again`/`retry`/`thử lại`/`fix`/`sửa giúp tôi` trống. Khi fail phải chạy `python aios/governance/cli/gate_check.py --task TASK-00X` + `python -m pytest aios -q` rồi báo `Violation(rule,module,line)` hoặc test failure cụ thể trước khi thử lại. User cũng phải dán lỗi đầy đủ, không nói chung chung.
* **Cấm "Continue to iterate?" / autopilot mù:** trong chế độ autopilot, khi lệnh/test fail, agent PHẢI tự chạy `gate_check.py` + `pytest` và báo lỗi cụ thể trước khi gửi bất kỳ message "Continue"/"Try Again"/"tiếp tục" nào. Tuyệt đối không loop "Try Again" chờ user — nếu lỗi lặp >2 lần thì auto-stop và báo root cause (theo quy tắc "Tự chủ theo lô + auto-stop").
* **Xử lý terminal lỗi (tiết kiệm token):** khi terminal báo lỗi, ưu tiên đọc qua terminal tool / chạy lệnh chẩn đoán trực tiếp; cấm paste nguyên output terminal >2k chars vào chat. Tóm tắt lỗi thành 1 dòng (exit code + tên test fail / Violation) rồi chạy `gate_check.py`/`pytest` để lấy chi tiết.
* **Ngôn ngữ giao tiếp (bắt buộc):** user yêu cầu giao tiếp bằng **tiếng Việt** — mọi trả lời, giải thích, tóm tắt đều bằng tiếng Việt. Commit message / code comment giữ tiếng Anh chuẩn.
* **Local CI gate trước khi push / claim DONE (bắt buộc):** luôn chạy `aiagent ci check` (hoặc `python aios/governance/cli/gate_check.py --task TASK-00X` — mặc định `--ci` bật, scope=full) trước khi push hoặc tuyên bố task DONE. Phát hiện sớm lỗi như `ModuleNotFoundError: fastapi` (thiếu extra `api`) trước khi lên CI. Cấm push khi local CI FAIL (fail-closed).
* **Tự chủ theo lô + auto-stop:** khi được giao chuỗi TASK đã lên lịch, tự thực hiện tuần tự, tự quyết định thứ tự không cần hỏi lại mỗi bước. Nhưng **ngưng lại** sau khi cùng 1 lỗi lặp lại nhiều lần (không loop "Try Again"/"thử lại" vô tận) — báo cáo root cause rồi chờ user.
* **Short approval = proceed:** khi user chỉ nói "có"/"duyệt"/"ok", hiểu là phê duyệt và tiếp tục bước tiếp theo, không cần xác nhận lại.
* **PowerShell contract (Windows):** workspace chạy PowerShell — cấm bash-isms `head`, `&&`, `grep`, `2>&1 | head`. Dùng `pip show fastapi`, `pip list | Select-String fastapi`, `Select-Object -First 20`, `;` cho sequence. Kiểm tra `pyproject.toml` dependencies trước khi kết luận thiếu package.
* **Workspace path:** luôn dùng path tương đối `${workspaceFolder}` (`d:\AIOS` / `aios/...`); cấm hardcode `OneDrive\Desktop\AIAGENT` legacy.
* **Session hygiene:** sau ~15 turns hoặc paste >2k chars, chạy `/compact` hoặc mở session mới; ưu tiên file reference thay vì paste dài; 0 checkpoints hiện tại — session dài không compact làm tăng input tokens mỗi turn.
* **Logging:** JSON via `aios.core.logging`; config via `AIOS_*` env overrides.
* **Docs:** detailed specs in [`docs/AIOS_Master_Task_Specification_M0-M26.md`](docs/AIOS_Master_Task_Specification_M0-M26.md) and [`docs/detailtask/`](docs/detailtask/) — link, don't duplicate.
* For architecture violations, run `python -m pytest aios/governance/architecture -q` and inspect `Violation(rule, module, detail, line)`.
