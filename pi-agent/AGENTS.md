# Development preferences

- Follow the existing project's language, package manager, and conventions.
- For new or otherwise unconstrained Python work, use `uv` for dependency management, virtual environments, locking, and command execution.
- When no language is specified and the repository does not imply one, prefer Python.
- Ask before choosing a language when the choice materially affects deployment, runtime constraints, interoperability, or maintenance.
- Project-level instructions override these defaults.

## Documentation

Keep repository documentation accurate and durable for humans and agents.

- Prefer progressive disclosure. Use `README.md` as a concise entry point and move specialized or implementation-specific material
into focused documents.
- State supported behavior directly. Use "currently" only when contrasting versions or describing a temporary state.
- Use "not yet" only for committed roadmap work. Do not imply that an absent capability is planned.
- Describe positive workflows where readers perform them.
- Document an unsupported capability only when readers would reasonably expect it or when the boundary affects correct use.
- Keep each capability boundary in one authoritative location. Link to it instead of repeating absence lists.
- Base behavioral claims on implemented behavior verified in source or tests. Do not document planned behavior as available.
- Review documentation when a change affects a public API, supported workflow or command, validation rule, documented module
responsibility, or capability boundary. Behavior-preserving internal changes do not require documentation edits.

## Durable decisions

- Before changing architecture, read relevant records under `architecture/adr/` when that directory exists.
- When a decision is hard to reverse, surprising without context, and based on a real trade-off, use the `domain-modeling` skill to offer an ADR. Do not record routine or easily reversible choices.
