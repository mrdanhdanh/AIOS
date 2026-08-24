#!/usr/bin/env python3
"""Static serve-readiness check (no network/socket used).

Confirms every local asset referenced by index.html exists on disk so the
site can be opened directly or served by any static file server offline.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    refs = re.findall(r'(?:href|src)="([^"]+)"', html)
    local = [r for r in refs if not r.startswith(("http://", "https://", "#", "javascript:"))]
    missing = []
    for ref in local:
        p = os.path.normpath(os.path.join(ROOT, ref))
        if not os.path.isfile(p):
            missing.append(ref)
    if missing:
        print("FAIL: missing local assets:", missing)
        sys.exit(1)
    print("SERVE-READY: all", len(local), "local assets resolve:", local)
    print("Site can be opened via file:// or any static server (offline).")


if __name__ == "__main__":
    main()
