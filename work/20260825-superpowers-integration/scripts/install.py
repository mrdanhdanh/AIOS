"""Install generated Superpowers integration into the AIOS repo.

Copies work/20260825-superpowers-integration/generated/ into the AIOS tree:
  - skills/superpowers/...            (12 AIOS-adapted skills)
  - aios/skill/superpowers_router.py  (deterministic router)
  - aios/skill/tests/test_superpowers_router.py
  - docs/superpowers-integration.md   (mapping doc)
And appends a reference section to AGENTS.md (idempotent).

Pure stdlib, non-destructive (additive only). Run from repo root.
"""

from __future__ import annotations

import os
import shutil

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GEN = os.path.join(REPO, "work", "20260825-superpowers-integration", "generated")
SRC_SKILLS = os.path.join(GEN, "skills", "superpowers")
SRC_AIOS_SKILL = os.path.join(GEN, "aios", "skill")
SRC_DOCS = os.path.join(GEN, "docs")

DST_SKILLS = os.path.join(REPO, "skills", "superpowers")
DST_ROUTER = os.path.join(REPO, "aios", "skill", "superpowers_router.py")
DST_TEST = os.path.join(REPO, "aios", "skill", "tests", "test_superpowers_router.py")
DST_DOC = os.path.join(REPO, "docs", "superpowers-integration.md")
AGENTS = os.path.join(REPO, "AGENTS.md")

REF_MARKER = "<!-- superpowers-integration-ref -->"
REF_SECTION = (
    "\n"
    "<!-- superpowers-integration-ref -->\n"
    "## 13. Superpowers integration (TASK-SUPERPOWERS)\n"
    "\n"
    "Triết lý / nguyên tắc / xử lý của [obra/superpowers](https://github.com/obra/superpowers) "
    "đã được tích hợp sâu vào AIOS dưới dạng 12 skill trong `skills/superpowers/` và một router "
    "xác định (`aios/skill/superpowers_router.py`). Quy tắc cốt lõi **using-superpowers**: trước "
    "bất kỳ hành động nào, phải kiểm tra skill phù hợp (process skills ưu tiên: brainstorming, "
    "systematic-debugging). Xem ánh xạ chi tiết tại `docs/superpowers-integration.md`.\n"
    "\n"
    "Khi nhận yêu cầu, agent NÊN chạy `from aios.skill.superpowers_router import route; route(req)` "
    "để chọn skill theo thứ tự ưu tiên trước khi phản hồi.\n"
)


def copy_tree(src: str, dst: str) -> None:
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> None:
    assert os.path.isdir(SRC_SKILLS), f"missing generated skills: {SRC_SKILLS}"
    copy_tree(SRC_SKILLS, DST_SKILLS)
    shutil.copyfile(SRC_AIOS_SKILL + "/superpowers_router.py", DST_ROUTER)
    shutil.copyfile(SRC_AIOS_SKILL + "/tests/test_superpowers_router.py", DST_TEST)
    shutil.copyfile(SRC_DOCS + "/superpowers-integration.md", DST_DOC)

    with open(AGENTS, "r", encoding="utf-8") as f:
        text = f.read()
    if REF_MARKER not in text:
        with open(AGENTS, "a", encoding="utf-8") as f:
            f.write(REF_SECTION)
        print("Appended Superpowers reference to AGENTS.md")
    else:
        print("AGENTS.md already references Superpowers integration (skipped)")

    print("Installed Superpowers integration into AIOS repo.")


if __name__ == "__main__":
    main()
