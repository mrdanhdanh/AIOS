# AIOS 1.0 Developer Experience — Getting Started

This guide gets you productive building **capability / agent / tool / workflow**
artifacts on AIOS 1.0 using the Developer Experience (DX) tooling delivered by
TASK-071.

## Prerequisites

- Python >= 3.11
- Installed package: `pip install -e ".[dev]"`
- The `aiagent` CLI (entry point: `aios.cli.workflow_cli:main`)

## 1. Check the CLI version

```bash
aiagent version
```

The version is governed by `aios.devkit.cli_version.CLI_VERSION`. A *breaking*
change (removing/renaming a stable subcommand) requires a version bump plus a
deprecation window — enforced by `CliVersionPolicy`.

## 2. Scaffold a new artifact

```bash
# capability / agent / tool / workflow
aiagent dx scaffold capability mycap --out ./mycap
aiagent dx scaffold tool mytool --out ./mytool
aiagent dx scaffold agent myagent --out ./myagent
aiagent dx scaffold workflow myflow --out ./myflow
```

Each command writes:

- `aios/<layer>/<name>.py` — an architecture-clean skeleton (passes the
  T063 architecture guard: no ARCH-001..004).
- `extension_spec.json` — a Contract 1.0 (T064) conformant spec.
- `README.md` — artifact metadata.

## 3. Verify conformance

```bash
aiagent dx verify ./mycap
```

This runs the real governance checks:

- **Architecture 1.0 (T063)** via `aios.governance.architecture.guard`.
- **Contract 1.0 (T064)** via `aios.extension_contracts.validator`.

Output: `[PASS]` when architecture + contract + boundary all pass.

## 4. Check CLI stability policy

```bash
aiagent dx policy --baseline run,validate --current run,validate
```

Detects breaking changes and fails closed if a command was removed without a
version bump.

## Programmatic API

```python
from aios.devkit import DevKitScaffold, DevKitCLI

cli = DevKitCLI()
artifact = cli.scaffold("capability", "mycap")      # dict
result = cli.verify(artifact)                        # {"passed": True, ...}
```

See [reference.md](reference.md) for the full API and command surface.
