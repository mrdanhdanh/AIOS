# configs/

Runtime configuration samples for AIOS (TASK-002).

- `default.yaml` — base configuration loaded via `aios.core.config.Config` (env `AIOS_*` overrides file values when present).
- `development.yaml` — overrides for local dev (`log_format: text`, `log_level: DEBUG`).
- `test.yaml` — overrides for CI/test (minimal timeouts).

> Config source of truth remains `aios.core.config.Config` — files here are
> documentation / examples; services must not parse them directly. See
> `docs/plan/tasks/TASK-002.md` (Architecture: Configuration).

Layout satisfies M1 spec:


configs/
  default.yaml
  development.yaml
  test.yaml
```
