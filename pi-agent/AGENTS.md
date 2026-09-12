# Development preferences

- Follow the existing project's language, package manager, and conventions.
- For new or otherwise unconstrained Python work, use `uv` for dependency management, virtual environments, locking, and command execution.
- When no language is specified and the repository does not imply one, prefer Python.
- Ask before choosing a language when the choice materially affects deployment, runtime constraints, interoperability, or maintenance.
- Project-level instructions override these defaults.
- When presenting outcomes of tasks, look to reduce the required cognitive load. When it relates to coding tasks, strongly consider using the `/show-me` skill to reduce the reader's cognitive load.

## Documentation

Keep documentation accurate, durable, and easy to navigate for humans and agents.

### Content

- Document implemented behavior and support behavioral claims with source or tests.
- State behavior directly. Use "currently" only for version contrasts or temporary states, and "not yet" only for committed roadmap
work.
- Document workflows where readers perform them. Mention unsupported behavior only when readers would reasonably expect it or when it
affects correct use.
- Keep each capability boundary authoritative in one place and link to it elsewhere.
- Review documentation when a change affects a public interface, workflow, command, validation rule, documented module responsibility,
or capability boundary. Behavior-preserving internal changes do not require documentation edits.

### Structure

- Use `README.md` to explain the repository's purpose, provide useful starting points, and route readers to deeper material.
- Organize around reader tasks by default. Use personas when their workflows materially differ, and stable domain areas when they
provide clearer reference or maintainer navigation.
- Apply progressive disclosure within each path: put prerequisites and common workflows first, then optional context, implementation
detail, and rationale. Keep linked pages understandable when opened directly.
- Use Diátaxis to clarify a page's purpose, not as a required directory structure.
- Prefer deep guides over clusters of shallow pages. Extend a guide when material serves the same audience and task; create a page for
a distinct reader need or maintenance responsibility. Do not split based on length alone.

## Durable decisions

- Before changing architecture, read relevant records under `architecture/adr/` when that directory exists.
- When a decision is hard to reverse, surprising without context, and based on a real trade-off, use the `domain-modeling` skill to offer an ADR. Do not record routine or easily reversible choices.

## Code style

### Name parameters by semantic role

Prefer parameter names that state each value's role at the interface. A caller should be able to understand a keyword argument without
opening the callee. Distinguish categories from instances, declaring files from authored or resolved paths, and classes from instances.

Rather than:

```python
def load_resource(
    *,
    resource: str,
    source: Path,
    reference: Path,
    model: type[BaseModel],
) -> BaseModel: ...
```

Prefer:

```python
def load_resource(
    *,
    resource_kind: str,             # "AgentConfig", not a resource instance
    declaring_file: Path,           # file containing the reference
    declared_resource_path: Path,   # path as authored, before resolution
    model_type: type[BaseModel],     # class used to validate the file
) -> BaseModel: ...
```

Use the same terminology across producer parameters, exception attributes, and serialized output. Treat JSON field names as public
interfaces.

Do not make names longer when the callable and type already establish the role. For example, load_experiment(path: Path) is clearer than
repeating load_experiment(experiment_path: Path).
