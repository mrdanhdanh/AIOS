import sys, pathlib
# Make the repo root importable so `import aios.governance...` works under pytest.
ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
