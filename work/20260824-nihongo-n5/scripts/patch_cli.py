"""Patch workflow_cli.py to register the `aiagent task <TASK-xxx>` subcommand.

The `task` command runs the full AIOS governance pipeline + 7 gates for a TASK,
so every AIOS job is driven through the real pipeline (no part is bypassed).
"""
import re

CLI = r"d:\AIOS\aios\cli\workflow_cli.py"

PATCH_IMPORT = (
    "from aios.runtime.workflow import WorkflowDefinition, WorkflowError  # noqa: E402\n"
)

PATCH_SUBCMD = '''    p_task = sub.add_parser("task", help="Run full AIOS pipeline + 7 gates for a TASK-xxx")
    p_task.add_argument("task_id", help="Task id, e.g. TASK-001")
    p_task.add_argument("--job-dir", default=None, help="Job folder for logs")
    p_task.set_defaults(func=_cmd_task)

'''

CMD_FUNC = '''def _cmd_task(args: argparse.Namespace) -> int:
    """Run the full AIOS governance pipeline + 7 gates for a TASK-xxx."""
    from pathlib import Path as _P
    sys.path.insert(0, str(REPO_ROOT))
    run_task = _P(REPO_ROOT) / "work" / "20260824-nihongo-n5" / "scripts" / "run_task.py"
    if not run_task.exists():
        # Fallback: look for the script next to this CLI file's repo.
        run_task = _P(REPO_ROOT) / "scripts" / "run_task.py"
    import subprocess as _sp
    cmd = [sys.executable, str(run_task), args.task_id]
    if getattr(args, "job_dir", None):
        cmd += ["--job-dir", args.job_dir]
    rc = _sp.call(cmd, cwd=str(REPO_ROOT))
    return rc


'''


def main() -> None:
    with open(CLI, "r", encoding="utf-8") as fh:
        src = fh.read()

    # 1) Register subcommand right after the `execute` subparser block.
    if "p_task = sub.add_parser(\"task\"" not in src:
        # Insert after the execute subparser's set_defaults line.
        marker = '    p_ex.set_defaults(func=_cmd_execute)'
        assert marker in src, "execute subparser marker not found"
        src = src.replace(marker, marker + "\n" + PATCH_SUBCMD, 1)

    # 2) Add the _cmd_task function before build_parser.
    if "def _cmd_task" not in src:
        marker = "def build_parser() -> argparse.ArgumentParser:"
        assert marker in src, "build_parser marker not found"
        src = src.replace(marker, CMD_FUNC + marker, 1)

    with open(CLI, "w", encoding="utf-8") as fh:
        fh.write(src)
    print("patched workflow_cli.py with `aiagent task` subcommand")


if __name__ == "__main__":
    main()
