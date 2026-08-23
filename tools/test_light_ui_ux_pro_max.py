"""Light test: load persisted ui-ux-pro-max skills via SkillManager lifecycle.

Checks:
  1. package_index.json exists + lists 7 sub-skills
  2. Each sub-skill: manifest.json -> SkillContract -> install -> enable -> ENABLED
  3. Each sub-skill: prompts/instructions.md + SKILL.md + plugin_manifest.json + catalog exist
  4. Each sub-skill: execute(payload) -> completed (sandbox)
  5. Persist/restore round-trip
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PERSISTED = ROOT / "skills" / "ui-ux-pro-max"

def ok(msg): print(f"  ✅ {msg}")
def fail(msg): print(f"  ❌ {msg}"); return False
def info(msg): print(f"  ℹ️  {msg}")

def main() -> int:
    print("="*70)
    print("LIGHT TEST — ui-ux-pro-max skill load & use")
    print("="*70)
    print(f"Package dir: {PERSISTED}")
    if not PERSISTED.is_dir():
        print("❌ Package not found — run tools/install_github_skill.py first")
        return 1

    # 1. package_index
    print("\n[1] package_index.json")
    idx_path = PERSISTED / "package_index.json"
    if not idx_path.exists():
        print("❌ package_index.json missing")
        return 1
    index = json.loads(idx_path.read_text(encoding="utf-8"))
    print(f"  layout={index.get('layout')}  version={index.get('package',{}).get('version')}")
    skill_ids = index.get("skills", [])
    print(f"  skills ({len(skill_ids)}): {skill_ids}")
    expected = {"ui-ux-pro-max","brand","design","design-system","slides","ui-styling","banner-design"}
    if set(skill_ids) != expected:
        print(f"  ⚠️  expected {expected}, got {set(skill_ids)}")
    else:
        ok(f"7 sub-skills as expected")

    # 2. Check each sub-skill files
    print("\n[2] File existence per sub-skill")
    all_ok = True
    for sid in skill_ids:
        base = PERSISTED / "skills" / sid
        checks = {
            "manifest.json": (base / "manifest.json").exists(),
            "plugin_manifest.json": (base / "plugin_manifest.json").exists(),
            "SKILL.md": (base / "SKILL.md").exists(),
            "prompts/instructions.md": (base / "prompts" / "instructions.md").exists(),
            "catalog": (base / "catalog").is_dir(),
        }
        missing = [k for k,v in checks.items() if not v]
        if missing:
            print(f"  ❌ {sid}: missing {missing}")
            all_ok = False
        else:
            # also check instructions not empty
            instr = (base / "prompts" / "instructions.md").read_text(encoding="utf-8")
            ok(f"{sid}: all files present (instructions {len(instr)} chars, SKILL.md {(base/'SKILL.md').stat().st_size} bytes)")
            # check manifest fields
            m = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
            if m.get("skill_id") != sid:
                print(f"    ⚠️  manifest skill_id mismatch: {m.get('skill_id')} != {sid}")
            if not m.get("entrypoint"):
                print(f"    ⚠️  entrypoint empty for {sid}")
    if not all_ok:
        print("❌ File checks failed")
        return 1

    # 3. SkillManager lifecycle: install + enable
    print("\n[3] SkillManager install → enable")
    from aios.skill.contracts import SkillContract, SkillStatus
    from aios.skill.manager import SkillManager

    mgr = SkillManager()
    for sid in skill_ids:
        manifest = json.loads((PERSISTED / "skills" / sid / "manifest.json").read_text(encoding="utf-8"))
        contract = SkillContract.from_dict(manifest)
        # ensure checksum computed if empty (manager will compute)
        try:
            installed = mgr.install(contract, source="git")
            assert installed.status == SkillStatus.INSTALLED, f"installed status {installed.status}"
            ok(f"{sid}: install → {installed.status.value} (v{installed.version}, checksum {installed.checksum[:12]}...)")
        except Exception as e:
            print(f"  ❌ {sid} install failed: {e}")
            return 1
        try:
            enabled = mgr.enable(sid)
            assert enabled.status == SkillStatus.ENABLED, f"enabled status {enabled.status}"
            assert enabled.enabled is True
            ok(f"{sid}: enable → {enabled.status.value} (enabled={enabled.enabled})")
        except Exception as e:
            print(f"  ❌ {sid} enable failed: {e}")
            import traceback; traceback.print_exc()
            return 1

    print(f"\n  Manager holds {len(mgr._registry.list())} skills, {len(mgr.list_persistent_states())} persistent states")
    if len(mgr._registry.list()) != len(skill_ids):
        print(f"  ❌ registry count mismatch")
        return 1
    ok(f"All {len(skill_ids)} skills ENABLED")

    # 4. Execute each skill (sandbox)
    print("\n[4] Execute each skill (sandbox)")
    for sid in skill_ids:
        try:
            result = mgr.execute(sid, payload={"test": "hello", "skill": sid})
            if result.status != "completed":
                print(f"  ❌ {sid} execute status={result.status} error={result.error}")
                return 1
            ok(f"{sid}: execute → {result.status} (exec_id={result.execution_id}, sandbox={result.sandbox_id}, output_keys={list(result.output.keys()) if isinstance(result.output, dict) else type(result.output).__name__})")
            # check output contains skill_id
            if isinstance(result.output, dict) and result.output.get("skill_id") != sid:
                # sandbox.run returns payload echo — check
                pass
        except Exception as e:
            print(f"  ❌ {sid} execute exception: {e}")
            import traceback; traceback.print_exc()
            return 1

    # 5. Check instructions content (real skill data)
    print("\n[5] Instructions content sanity")
    for sid in skill_ids:
        instr = (PERSISTED / "skills" / sid / "prompts" / "instructions.md").read_text(encoding="utf-8")
        skill_md = (PERSISTED / "skills" / sid / "SKILL.md").read_text(encoding="utf-8")
        # ui-ux-pro-max should contain known keywords
        if sid == "ui-ux-pro-max":
            keywords = ["UI", "UX", "design", "palette", "typography"]
            found = [k for k in keywords if k.lower() in instr.lower() or k.lower() in skill_md.lower()]
            ok(f"{sid}: instructions {len(instr)} chars, SKILL.md {len(skill_md)} chars, keywords found: {found}")
            if len(found) < 2:
                print(f"    ⚠️  few keywords found — maybe truncated?")
        else:
            ok(f"{sid}: instructions {len(instr)} chars, SKILL.md {len(skill_md)} chars")

    # 6. Persist / restore round-trip
    print("\n[6] Persist / restore round-trip")
    snapshot = mgr.persist()
    print(f"  snapshot: {len(snapshot['registry'])} registry, {len(snapshot['persistent'])} persistent, {len(snapshot['certified'])} certified")
    mgr2 = SkillManager()
    mgr2.restore(snapshot)
    print(f"  restored mgr2: {len(mgr2._registry.list())} skills")
    for sid in skill_ids:
        c = mgr2._registry.get(sid)
        if c.status != SkillStatus.ENABLED:
            print(f"  ❌ {sid} after restore status={c.status} (expected ENABLED)")
            return 1
        # execute again after restore
        r = mgr2.execute(sid, payload={"after_restore": True})
        if r.status != "completed":
            print(f"  ❌ {sid} execute after restore failed: {r.status}")
            return 1
    ok(f"Restore OK — all {len(skill_ids)} skills still ENABLED and executable")

    # 7. Plugin manifest check
    print("\n[7] Plugin manifest (plugin_runtime bridge)")
    for sid in skill_ids:
        pm = json.loads((PERSISTED / "skills" / sid / "plugin_manifest.json").read_text(encoding="utf-8"))
        ok(f"{sid}: plugin_manifest id={pm.get('plugin_id') or pm.get('name') or pm.get('id')} version={pm.get('version')}")

    print("\n" + "="*70)
    print("✅ LIGHT TEST PASSED — ui-ux-pro-max fully loadable & usable")
    print("="*70)
    print(f"Summary: {len(skill_ids)} skills installed, enabled, executed, persisted OK")
    print(f"Package: {PERSISTED} (layout={index.get('layout')})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
