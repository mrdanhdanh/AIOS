"""AIOS-driven generator for the N5 learning site (TASK-223 implementation).

Running this script (re)generates the static site from the AIOS tool
``aios.tool.website.n5_builder``. This proves the deliverable is PRODUCED BY
AIOS (with a ``build_evidence.json`` provenance record), not written by hand —
which is exactly what the ``runtime_utilization`` gate now enforces for tasks
that declare ``Demonstrates-AIOS: true``.
"""

from __future__ import annotations

import os

from aios.tool.website.n5_builder import build_n5_site

HERE = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    result = build_n5_site(HERE)
    print("AIOS built N5 site into:", result["target_dir"])
    for f in result["files"]:
        print("  -", f)
    print("content_hash:", result["content_hash"])
