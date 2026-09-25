# Language

Use the `unslop` skill when producing any non-trivial length of prose.

Prefer precise, established technical terminology over ambiguous shorthand. For example, prefer "CLI boundary" or "entrypoint orchestration," rather than broad phrases such as "process concerns." If no standard term fits, describe the mechanism directly.

# Development preferences

- Follow the existing project's language, package manager, and conventions.
- For new or otherwise unconstrained Python work, use `uv` for dependency management, virtual environments, locking, and command execution.
- When no language is specified and the repository does not imply one, prefer Python.
- Ask before choosing a language when the choice materially affects deployment, runtime constraints, interoperability, or maintenance.
- Project-level instructions override these defaults.
- Reduce the cognitive load of task reports. For coding tasks, strongly consider using the `/show-me` skill.

### Development workflow

Before a non-trivial codebase change, load `gated-development` and let it select
the Small or Gated lane.

Use `contract-scaffold` as the primary skill when the final artifact is
intentionally incomplete source for interface or contract review. For a working
outcome, keep `gated-development` primary and use `contract-scaffold` only as a
design gate.

Prefer that gate when the next executable checkpoint depends on an unsettled
public interface, persisted schema, protocol, error model, ownership decision,
or architectural seam that would be expensive to reject after implementation.
Include the recommendation in the execution packet rather than asking a separate
preliminary question.

Skip the scaffold when the interface is established, revision is inexpensive,
or a narrow executable checkpoint would resolve the uncertainty more directly.
Ask only when the approaches have materially different cost, review cadence, or
retained artifacts and neither is clearly preferable.

## Project documentation

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

### Code readability

Optimize for understanding at the point of use, not minimum line count or documentation coverage.

- Prefer clear names, types, and structure. Treat documentation attached to externally visible declarations as part of the interface.
- Give interface documentation priority over implementation comments. Cover every externally visible module, type, and callable at its declaration or the narrowest enclosing externally visible scope. Explain the abstraction and caller-visible contract completely enough that callers do not need to read the implementation.
- Use implementation comments to explain internal strategy, rationale, invariants, dependencies, and constraints needed to change the code safely. Keep them near the code they explain. Do not put implementation details in interface documentation or repeat the interface contract inside the implementation.
- Write comments and docstrings at a different level from the code. Add higher-level abstraction or rationale, or lower-level semantic precision. Do not paraphrase declarations or implementation.
- Make orchestration read top-down. Extract coherent operations, contracts, or repeated mechanics—not merely to shorten a function—and avoid pass-through helpers that increase navigation.
- Use blank lines to separate coherent phases within orchestration. Prefer whitespace and clear names for visible phases. Add a local comment only when ordering, recovery, or persistence semantics are not apparent from the statements themselves.
- Keep behavior-specific inputs, decisions, and expected results close to where they matter. Extract repeated mechanics when doing so removes noise without hiding the behavior.

In tests, favor local readability over deduplication when abstraction would separate a scenario from the data needed to understand its assertions.

### Name parameters by semantic role

Prefer parameter names that state each value's role at the interface. Make each keyword argument understandable without opening the
callee. Distinguish categories from instances, declaring files from authored or resolved paths, and classes from instances.

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
