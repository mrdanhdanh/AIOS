#!/usr/bin/env python
"""AIOS Workflow CLI — simulate & validate (TASK-008)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

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
    p_wf = sub.add_parser("workflow", help="Workflow subcommands")
    wf_sub = p_wf.add_subparsers(dest="wf_command", required=True)
    p_val = wf_sub.add_parser("validate", help="Validate a workflow YAML file")
    p_val.add_argument("workflow", help="Path to workflow YAML file")
    p_val.set_defaults(func=_cmd_validate)
    p_val2 = sub.add_parser("validate", help="Validate a workflow YAML file (alias)")
    p_val2.add_argument("workflow", help="Path to workflow YAML file")
    p_val2.set_defaults(func=_cmd_validate)
    return parser


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
