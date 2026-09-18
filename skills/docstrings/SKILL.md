---
name: docstrings
description: >-
  Use when writing or reviewing non-trivial docstrings or comments,
  or when code-documentation quality is a material part of the task.
---

# Docstrings

A docstring gives the reader context for a module, type, or callable and describes its role or contract.

A comment gives readers the abstraction, rationale, dependency, or constraint
needed to understand or safely change nearby code when that information is not
obvious from the implementation or would be costly to infer.

Neither records the session that produced the code.

## Rules

* **Docstrings MUST give the reader an entry point and reduce cognitive load.**
  Prefer a descriptive docstring for modules, types, and meaningful callables.
  Orient the reader to the symbol's purpose and add important role, behavior,
  or contract information that is not apparent from its name, signature,
  types, and surrounding structure.

* **Be complete, then concise.** Use as much documentation as the symbol
  warrants, but no more. Reserve one-line docstrings for genuinely simple
  callables whose purpose and contract can be captured completely in one
  sentence. For a non-trivial function, default to a short summary followed by
  a short paragraph explaining the most important workflow, side effects,
  constraints, or result.

  Do not compress a non-trivial operation into one sentence merely because the
  sentence is technically accurate.

* **Document information the signature does not convey.** Include important
  parameter interpretation and use, such as a path's resolution base or a label
  used in diagnostics. Also include return guarantees, side effects, failure
  modes, mutation, ownership, ordering, units, invariants, lifecycle behavior,
  or environmental requirements when they matter to callers or maintainers.

* **Use sections for contract details.** Use an `Args` section when several
  parameters need semantic explanation. Use `Returns`, `Raises`, or `Attributes`
  when those contracts need to be found independently. Each entry should add
  information beyond the name and annotation.

* **Docstrings and comments are not logs.** Do not preserve development
  chronology or describe changes from historical implementations. Document
  durable rationale when it explains why an obvious alternative would violate
  a constraint. Put change history in commits and broader architectural
  trade-offs in an ADR.

* **Comments explain non-obvious information.** Use them for block-level intent
  in long operations, design rationale, invariants, edge cases, dependencies,
  and local constraints. A comment such as "Copy before iterating because
  callbacks may remove listeners" records a constraint needed to modify the
  code safely. Prefer the abstraction or reason over a paraphrase of the next
  line.

* **Cut context the reader cannot reach.** Stack layer numbers, ticket IDs,
  sprint names, "as discussed above," and "as requested" do not belong in the
  code. "Implementation lands in L1" means nothing outside the session.

## What good looks like

### A simple callable

A one-line docstring is enough when it captures the useful contract:

```python
def normalize_slug(value: str) -> str:
    """Normalize a user-facing name into a lowercase URL slug."""
```

Do not expand this merely to fill out `Args` and `Returns` sections.

### A non-trivial operation

Give the reader enough context to understand the operation before reading its
body:

```python
def run_harbor_doctor() -> dict[str, Any]:
    """Verify the local Harbor installation with a synthetic Oracle trial.

    Runs the bundled doctor fixture in an isolated temporary job and returns
    the Harbor version and verifier rewards from the scored result.
    """
```

This is preferable to:

```python
def run_harbor_doctor() -> dict[str, Any]:
    """Run a synthetic Oracle trial and return its scored-result report."""
```

when the isolation, validation role, and returned report are important to
understanding the operation.

### A domain type

Describe what the object represents rather than enumerating visible fields:

```python
@dataclass(frozen=True)
class ResolvedExperiment:
    """Validated experiment inputs resolved to project-relative resources."""
```

Do not write:

```python
@dataclass(frozen=True)
class ResolvedExperiment:
    """An experiment with a project root, source, manifest, task, and skill."""
```

### An important internal helper

Private does not mean undocumented. Document helpers that encode an important
operation or invariant:

```python
def _validate_arm_parity(...):
    """Ensure matched arms differ only by identity and the declared treatment."""
```

Trivial private helpers need not receive docstrings merely for consistency.

### Parameters with semantic roles

```python
def resolve_path(declaring_file: Path, declared_path: str | Path) -> Path:
    """Resolve a declared path relative to the file that contains it.

    Args:
        declaring_file: File whose parent is the base for relative paths.
        declared_path: Path as declared, before expansion and resolution.

    Returns:
        The resolved absolute path.
    """
```

### A useful comment

```python
# Copy before iterating because callbacks may remove listeners.
for listener in list(self._listeners):
    listener(event)
```

The comment records a constraint that is not obvious from the code. Do not
replace it with `# Iterate over listeners`.

The goal is high information density: each sentence should add context needed
to use or maintain the code.
