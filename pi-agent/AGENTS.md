# Development preferences

- Follow the existing project's language, package manager, and conventions.
- For new or otherwise unconstrained Python work, use `uv` for dependency management, virtual environments, locking, and command execution.
- When no language is specified and the repository does not imply one, prefer Python.
- Ask before choosing a language when the choice materially affects deployment, runtime constraints, interoperability, or maintenance.
- Project-level instructions override these defaults.

## Durable decisions

- Before changing architecture, read relevant records under `docs/adr/` when that directory exists.
- When a decision is hard to reverse, surprising without context, and based on a real trade-off, use the `domain-modeling` skill to offer an ADR. Do not record routine or easily reversible choices.
