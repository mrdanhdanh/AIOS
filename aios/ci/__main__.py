"""Allow ``python -m aios.ci <subcommand>``."""
from aios.ci.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
