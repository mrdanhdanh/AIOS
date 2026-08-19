"""Parse the master spec into a TaskRegistry (validates Rule 1 + derives Rule 2)."""
import re
import pathlib
from .registry import TaskRegistry, RegistryError
from .schema import TaskRecord

_MILESTONE_RE = re.compile(r"^#\s+(M\d+)\b")
_TASK_RE = re.compile(r"^##\s+TASK-(\d+)\s*[—-]\s*(.+)$")

DEFAULT_SPEC = (
    pathlib.Path(__file__).resolve().parents[3]
    / "docs"
    / "AIOS_Master_Task_Specification_M0-M26.md"
)


def parse_master_spec(path=DEFAULT_SPEC):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    reg = TaskRegistry()
    current_milestone = None
    for line in text.splitlines():
        m = _MILESTONE_RE.match(line)
        if m:
            current_milestone = m.group(1)
            continue
        t = _TASK_RE.match(line)
        if t:
            tid = "TASK-" + t.group(1)
            title = t.group(2).strip()
            # create_task raises RegistryError on duplicate -> proves Rule 1 uniqueness
            reg.create_task(tid, title, milestone=current_milestone or "UNKNOWN")
    return reg
