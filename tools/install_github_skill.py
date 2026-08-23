"""Install a GitHub skill into AIOS as a persistent Skill Plugin (TASK-219).

Clones (or uses a local path of) a GitHub skill, converts it via the
``aios.skill.github_bridge`` bridge, writes the package under ``skills/``,
then registers + installs + enables every sub-skill through the real
``SkillManager`` lifecycle so it survives across sessions.

Usage:
    python tools/install_github_skill.py \
        --repo https://github.com/nextlevelbuilder/ui-ux-pro-max-skill \
        --out skills/ui-ux-pro-max

Layering: this is a CLI tool (presentation), not part of the ``skill`` layer,
so it may use ``subprocess``/``os`` to clone. The bridge itself stays pure.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Make repo root importable when run directly.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aios.skill.github_bridge import convert_skill_dir  # noqa: E402
from aios.skill.manager import SkillManager  # noqa: E402


def _clone(repo: str, dest: Path) -> Path:
    if dest.exists() and any(dest.iterdir()):
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", repo, str(dest)], check=True)
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install a GitHub skill as an AIOS Skill Plugin.")
    parser.add_argument("--repo", help="GitHub repo URL (cloned if --local not given).")
    parser.add_argument("--local", type=str, help="Local path to an already-cloned skill dir.")
    parser.add_argument("--out", required=True, help="Output package directory under the repo (e.g. skills/ui-ux-pro-max).")
    parser.add_argument("--source", default="git", help="install_source label (git/local).")
    args = parser.parse_args(argv)

    if args.local:
        skill_dir = Path(args.local)
    elif args.repo:
        skill_dir = _clone(args.repo, Path(ROOT / "tmp_skill_test" / Path(args.repo).stem))
    else:
        print("ERROR: provide --repo or --local", file=sys.stderr)
        return 2

    if not skill_dir.is_dir():
        print(f"ERROR: skill dir not found: {skill_dir}", file=sys.stderr)
        return 2

    out_dir = ROOT / args.out
    result = convert_skill_dir(skill_dir, out_dir, install_source=args.source)
    print(f"[convert] layout={result['layout']} sub-skills={len(result['skills'])} -> {out_dir}")

    mgr = SkillManager()
    enabled = []
    for sk in result["skills"]:
        contract = sk["contract"]
        mgr.install(contract, source=args.source)
        mgr.enable(contract.skill_id)
        enabled.append(contract.skill_id)
        print(f"[enable] {contract.skill_id} -> ENABLED")

    print(f"[done] {len(enabled)} skill(s) installed & enabled.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
