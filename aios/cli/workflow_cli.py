#!/usr/bin/env python
"""AIOS Workflow CLI — simulate & validate (TASK-008)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from aios.runtime.workflow import WorkflowDefinition, WorkflowError  # noqa: E402
from aios.runtime.workflow.simulation import simulate  # noqa: E402


def _cmd_validate(args: argparse.Namespace) -> int:
    path = args.workflow
    try:
        wd = WorkflowDefinition.from_file(path)
        wd.validate()
    except (WorkflowError, OSError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(f"VALID: {wd.name} v{wd.version} ({len(wd.nodes)} nodes, {len(wd.edges)} edges)")
    return 0


def _write_execution_log(work_dir: str, wf, report, gates_result) -> str:
    """Persist a durable execution log (JSON + text) under <work_dir>/logs/.

    EvidenceStore is in-memory only, so this file is the durable proof that a
    plan was actually processed by AIOS (execution_id, per-step status, and
    optional 7-governance-gate result).
    """
    logs_dir = os.path.join(work_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    exec_id = report.execution_id
    ts = datetime.now(timezone.utc).isoformat()

    steps = []
    for sid, sr in report.results.items():
        out = str(sr.output).strip() if sr.output else (sr.error or "")
        steps.append({"step_id": sid, "status": sr.status, "output": out[:2000]})

    record = {
        "tool": "aiagent execute",
        "timestamp": ts,
        "plan_name": wf.name,
        "plan_version": wf.version,
        "execution_id": exec_id,
        "overall_status": "PASS" if report.is_success else "FAIL",
        "steps": steps,
        "governance_gates": gates_result,
    }
    json_path = os.path.join(logs_dir, f"execution-{exec_id}.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)

    text_path = os.path.join(logs_dir, f"execution-{exec_id}.log")
    lines = [
        "AIOS plan execution log",
        f"timestamp : {ts}",
        f"plan      : {wf.name} v{wf.version}",
        f"exec_id   : {exec_id}",
        f"status    : {'PASS' if report.is_success else 'FAIL'}",
        f"work_dir  : {work_dir}",
        "",
        "steps:",
    ]
    for s in steps:
        lines.append(
            f"  - {s['step_id']}: {s['status']}"
            + (f" :: {s['output'][:120]}" if s["output"] else "")
        )
    if gates_result:
        lines.append("")
        lines.append("governance gates (7 rules):")
        if "error" in gates_result:
            lines.append(f"  error: {gates_result['error']}")
        else:
            lines.append(
                f"  task={gates_result.get('task')} returncode={gates_result.get('returncode')}"
            )
            detail = (gates_result.get("stdout") or gates_result.get("stderr") or "").strip()
            if detail:
                lines.append(detail)
    else:
        lines.append("")
        lines.append("governance gates: not run (pass --govern --task TASK-xxx to execute)")
    with open(text_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return json_path


def _cmd_execute(args: argparse.Namespace) -> int:
    """Execute a plan file via the AIOS runtime (TASK-222 / TASK-224).

    Real execution is opt-in (real_execution.enabled in configs/default.yaml or
    AIOS_REAL_EXECUTION_ENABLED=1). With --simulate, only validate/print the plan
    (0 LLM calls, 0 real execution).

    TASK-224: --work-dir <dir> creates/uses a job folder and confines execution to it
    (sandbox allowed_cwd); --yes skips the interactive confirmation prompt (used when the
    user already approved, e.g. via the AIOS Planner agent).
    """
    path = args.file
    simulate = args.simulate
    timeout = args.timeout
    work_dir = getattr(args, "work_dir", None)
    yes = getattr(args, "yes", False)

    # TASK-224: resolve work dir — if a directory is given, place plan inside it.
    if work_dir:
        from pathlib import Path as _WD

        wd = _WD(work_dir)
        wd.mkdir(parents=True, exist_ok=True)
        p = _WD(path)
        if p.is_dir():
            path = str(wd / "plan.yaml")
        else:
            # Copy the plan into the work dir if it lives elsewhere.
            import shutil

            dest = wd / "plan.yaml"
            if p.resolve() != dest.resolve():
                shutil.copy2(p, dest)
            path = str(dest)
        allowed_cwd = str(wd.resolve())
    else:
        allowed_cwd = None

    try:
        if path.endswith(".md"):
            from pathlib import Path as _P
            wf = WorkflowDefinition.from_markdown(_P(path).read_text(encoding="utf-8"))
        else:
            wf = WorkflowDefinition.from_file(path)
    except (WorkflowError, OSError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    if simulate:
        print(f"[SIMULATE] {wf.name} v{wf.version} ({len(wf.nodes)} nodes, 0 LLM calls)")
        for n in wf.nodes:
            print(f"  - {n.command or n.description or n.id}")
        return 0

    # TASK-224: interactive confirmation unless --yes (agent/script pre-approved).
    if not yes:
        try:
            reply = input(
                f"Execute plan '{path}' in work-dir '{allowed_cwd or 'repo root'}'? [y/N] "
            ).strip().lower()
        except (EOFError, KeyboardInterrupt):
            reply = "n"
        if reply not in ("y", "yes", "có", "co"):
            print("Aborted by user.")
            return 3

    from aios.runtime.process import load_real_execution_config
    from aios.runtime.kernel import RuntimeKernel
    from aios.governance.evidence.store import EvidenceStore, record_execution_evidence

    re_cfg = load_real_execution_config()
    if not re_cfg.get("enabled"):
        print(
            "ERROR: real_execution disabled. Set real_execution.enabled: true in "
            "configs/default.yaml or AIOS_REAL_EXECUTION_ENABLED=1",
            file=sys.stderr,
        )
        return 2

    # TASK-224: confine execution to the work dir when provided.
    if allowed_cwd:
        re_cfg = dict(re_cfg)
        re_cfg["allowed_cwd"] = allowed_cwd

    kernel = RuntimeKernel(real_execution=re_cfg)
    plan = wf.to_execution_plan(allowed_cwd=allowed_cwd)
    report = kernel.execute_plan(plan, timeout=timeout)
    store = EvidenceStore()
    record_execution_evidence(store, wf.name, wf.version, plan, report, path)

    # Determine the work dir for durable logging (TASK-224 work-dir or plan's folder).
    work_dir = allowed_cwd or os.path.dirname(os.path.abspath(path)) or "."

    # Optional: actually run the 7 governance gates (proves governance executed).
    gates_result = None
    if getattr(args, "govern", False):
        task_id = getattr(args, "task", None)
        if not task_id:
            print("WARN: --govern requires --task TASK-xxx; skipping governance gates", file=sys.stderr)
        else:
            import subprocess as _sp
            try:
                proc = _sp.run(
                    [sys.executable, "aios/governance/cli/gate_check.py", "--task", task_id],
                    capture_output=True, text=True, cwd=str(REPO_ROOT),
                )
                gates_result = {
                    "task": task_id,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                }
                gstatus = "PASS" if proc.returncode == 0 else "FAIL"
                print(f"  [governance] 7 gates for {task_id}: {gstatus}")
            except Exception as exc:  # noqa: BLE001
                gates_result = {"task": task_id, "error": str(exc)}
                print(f"  [governance] gates error: {exc}", file=sys.stderr)

    # Durable log (EvidenceStore is in-memory only — this file is the proof).
    log_path = _write_execution_log(work_dir, wf, report, gates_result)
    print(f"  [log] written: {log_path}")

    status = "PASS" if report.is_success else "FAIL"
    print(f"[{status}] {wf.name} v{wf.version} (execution_id={report.execution_id})")
    for sid, sr in report.results.items():
        out = str(sr.output).strip() if sr.output else (sr.error or "")
        print(f"  {sid}: {sr.status}" + (f" :: {out[:120]}" if out else ""))
    return 0 if report.is_success else 1


def _cmd_run(args: argparse.Namespace) -> int:
    path = args.workflow
    if not args.simulate:
        print("Only --simulate is supported in M1. Use: aiagent run <workflow.yaml> --simulate", file=sys.stderr)
        return 2
    try:
        result = simulate(path)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except WorkflowError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    else:
        status = "PASS" if result.success else "FAIL"
        print(f"[{status}] {result.workflow_name} v{result.workflow_version} engine={result.engine}")
        print(f"  llm_calls={result.llm_calls} tool_calls={result.tool_calls}")
        if result.success:
            order = result.compiled.representation.get("topo_order", [])
            print(f"  topo_order: {' -> '.join(order) if order else '(empty)'}")
            for nr in result.node_results:
                print(f"    {nr.node_id}: {nr.status} ({nr.output})")
            print(f"  events: {len(result.events)}")
        else:
            print(f"  error: {result.error}", file=sys.stderr)
    return 0 if result.success else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aiagent", description="AIOS Workflow CLI (TASK-008)")
    sub = parser.add_subparsers(dest="command", required=True)
    p_run = sub.add_parser("run", help="Run a workflow (M1: --simulate only)")
    p_run.add_argument("workflow", help="Path to workflow YAML file")
    p_run.add_argument("--simulate", action="store_true", help="Simulate without real tools/LLM")
    p_run.add_argument("--json", action="store_true", help="Output JSON")
    p_run.set_defaults(func=_cmd_run)
    p_ex = sub.add_parser("execute", help="Execute a plan via AIOS runtime (real tools, opt-in)")
    p_ex.add_argument("file", help="Path to plan file (.yaml/.yml/.json/.md) or a directory")
    p_ex.add_argument("--simulate", action="store_true", help="Validate only, no real execution")
    p_ex.add_argument("--timeout", type=float, default=30.0, help="Per-step timeout in seconds")
    p_ex.add_argument(
        "--work-dir", default=None,
        help="Job folder (e.g. work/20260824-webno1); created if missing, execution confined to it",
    )
    p_ex.add_argument("--yes", action="store_true", help="Skip interactive confirmation (pre-approved)")
    p_ex.add_argument(
        "--govern", action="store_true",
        help="Also run the 7 governance gates (gate_check.py) after the plan and log the result",
    )
    p_ex.add_argument(
        "--task", default=None,
        help="TASK-xxx id used by --govern to run the 7 governance gates on that task",
    )
    p_ex.set_defaults(func=_cmd_execute)
    p_wf = sub.add_parser("workflow", help="Workflow subcommands")
    wf_sub = p_wf.add_subparsers(dest="wf_command", required=True)
    p_val = wf_sub.add_parser("validate", help="Validate a workflow YAML file")
    p_val.add_argument("workflow", help="Path to workflow YAML file")
    p_val.set_defaults(func=_cmd_validate)
    p_val2 = sub.add_parser("validate", help="Validate a workflow YAML file (alias)")
    p_val2.add_argument("workflow", help="Path to workflow YAML file")
    p_val2.set_defaults(func=_cmd_validate)
    p_ci = sub.add_parser("ci", help="Local CI/CD checker (check|run|install-hook|uninstall-hook)")
    p_ci.add_argument("rest", nargs=argparse.REMAINDER, help="ci subcommand and its options")
    p_ci.set_defaults(func=_cmd_ci)
    # Stable DX surface (T071): version + dx (scaffold/verify/policy).
    p_ver = sub.add_parser("version", help="Print the aiagent CLI version")
    p_ver.set_defaults(func=_cmd_version)
    p_dx = sub.add_parser("dx", help="Developer Experience tooling (scaffold/verify/policy)")
    dx_sub = p_dx.add_subparsers(dest="dx_command", required=True)
    p_sc = dx_sub.add_parser("scaffold", help="Scaffold a capability/agent/tool/workflow skeleton")
    p_sc.add_argument("kind", choices=["capability", "agent", "tool", "workflow"])
    p_sc.add_argument("name", help="Artifact name")
    p_sc.add_argument("--version", default="1.0.0", help="Artifact version (default 1.0.0)")
    p_sc.add_argument("--author", default="", help="Author name")
    p_sc.add_argument("--out", default=None, help="Directory to write generated files")
    p_sc.set_defaults(func=_cmd_dx_scaffold)
    p_vr = dx_sub.add_parser("verify", help="Verify a scaffolded artifact against T063+T064")
    p_vr.add_argument("dir", help="Directory containing the scaffolded artifact")
    p_vr.set_defaults(func=_cmd_dx_verify)
    p_po = dx_sub.add_parser("policy", help="Check CLI stability / breaking-change rule")
    p_po.add_argument("--baseline", default="", help="Comma-separated baseline command list")
    p_po.add_argument("--current", default="", help="Comma-separated current command list")
    p_po.add_argument("--baseline-version", default=None, help="Baseline CLI version")
    p_po.set_defaults(func=_cmd_dx_policy)
    return parser


def _cmd_ci(args: argparse.Namespace) -> int:
    from aios.ci.cli import main as ci_main

    # Delegate the remaining tokens (everything after `aiagent ci`) to the CI CLI.
    return ci_main(args.rest)


def _cmd_version(args: argparse.Namespace) -> int:
    from aios.devkit.cli_version import CLI_VERSION
    print(f"aios {CLI_VERSION}")
    return 0


def _cmd_dx_scaffold(args: argparse.Namespace) -> int:
    from aios.devkit.cli import DevKitCLI
    from aios.devkit.errors import format_actionable

    try:
        cli = DevKitCLI()
        artifact = cli.scaffold(args.kind, args.name, args.version or "1.0.0", args.author or "")
        if args.out:
            from aios.devkit.scaffold import ScaffoldArtifact, GeneratedFile
            full = ScaffoldArtifact(
                kind=artifact["kind"], name=artifact["name"], version=artifact["version"],
                author=artifact["author"], template_version=artifact["template_version"],
                spec=artifact["spec"],
                files=[GeneratedFile(f["path"], f["code"], f["module_path"]) for f in artifact["files"]],
            )
            written = cli._scaffold.render(full, args.out)
            print(f"scaffolded {args.kind} '{args.name}' -> {len(written)} files in {args.out}")
        else:
            print(f"scaffolded {artifact['kind']} '{artifact['name']}' v{artifact['version']} "
                  f"(template {artifact['template_version']})")
        return 0
    except Exception as exc:  # noqa: BLE001 - actionable DX error
        print(format_actionable(exc), file=sys.stderr)
        return 1


def _cmd_dx_verify(args: argparse.Namespace) -> int:
    from aios.devkit.scaffold import DevKitScaffold
    from aios.devkit.errors import format_actionable

    try:
        scaffold = DevKitScaffold()
        files = []
        spec: dict = {}
        base = args.dir
        for root, _dirs, names in os.walk(base):
            for nm in names:
                if nm.endswith(".py") or nm == "extension_spec.json":
                    full = os.path.join(root, nm)
                    with open(full, "r", encoding="utf-8") as fh:
                        code = fh.read()
                    rel = os.path.relpath(full, base).replace(os.sep, "/")
                    module_path = rel if nm.endswith(".py") else "extension_spec.json"
                    files.append((code, module_path))
                    if nm == "extension_spec.json":
                        spec = json.loads(code)
        if not spec:
            print("verify FAILED: no extension_spec.json found", file=sys.stderr)
            return 1
        artifact = scaffold.scaffold_artifact(
            spec.get("kind", "capability"), spec.get("name", ""), spec.get("version", "1.0.0")
        )
        # Rebuild artifact files from disk for an honest verification.
        from aios.devkit.scaffold import GeneratedFile, ScaffoldArtifact
        py_files = [GeneratedFile(rel, code, mp) for (code, mp) in files if mp.endswith(".py")]
        artifact = ScaffoldArtifact(
            kind=spec.get("kind", "capability"), name=spec.get("name", ""),
            version=spec.get("version", "1.0.0"), author="", template_version="1.0.0",
            spec=spec, files=py_files,
        )
        result = scaffold.verify_conformance(artifact)
        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] architecture={result['architecture']['passed']} "
              f"contract={result['contract']['valid']} boundary={result['boundary']['valid']}")
        if not result["passed"]:
            print(f"  arch_violations={result['architecture']['violations']}", file=sys.stderr)
            print(f"  contract_errors={result['contract']['errors']}", file=sys.stderr)
            return 1
        return 0
    except Exception as exc:  # noqa: BLE001 - actionable DX error
        print(format_actionable(exc), file=sys.stderr)
        return 1


def _cmd_dx_policy(args: argparse.Namespace) -> int:
    from aios.devkit.cli_version import CLI_VERSION, CliVersionPolicy
    from aios.devkit.errors import format_actionable

    policy = CliVersionPolicy(current_version=CLI_VERSION)
    baseline = args.baseline.split(",") if args.baseline else []
    current = args.current.split(",") if args.current else []
    try:
        removed = policy.assert_stable(baseline, current, args.baseline_version)
        if removed:
            print(f"breaking change detected (removed {removed}) but version bumped to {CLI_VERSION}")
        else:
            print(f"cli stable: no breaking changes (version {CLI_VERSION})")
        return 0
    except Exception as exc:  # noqa: BLE001 - actionable DX error
        print(format_actionable(exc), file=sys.stderr)
        return 1


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "wf_command", None) == "validate":
        return _cmd_validate(args)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 2
    return func(args)


if __name__ == "__main__":
    raise SystemExit(main())
