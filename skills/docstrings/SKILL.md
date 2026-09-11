---
name: docstrings
description: >-
  Use when writing or reviewing code, and whenever
  writing or editing docstrings and comments.
---

# Docstrings

A docstring gives the reader context for a module, type, or callable and describes its role or contract.

A comment explains local behavior or constraints that the code cannot make clear.

Neither records the session that produced the code.

## Rules

* **Docstrings MUST give the reader an entry point and reduce cognitive load.**
  Prefer a descriptive docstring for modules, types, and meaningful callables.
  State what the symbol does and enough of its role, behavior, or contract that
  the reader can understand its purpose before reading the implementation.

* **Be complete, then concise.** Use as much documentation as the symbol
  warrants, but no more. Reserve one-line docstrings for genuinely simple
  callables whose purpose and contract can be captured completely in one
  sentence. For a non-trivial function, default to a short summary followed by
  a short paragraph explaining the most important workflow, side effects,
  constraints, or result.

  Do not compress a non-trivial operation into one sentence merely because the
  sentence is technically accurate.

* **Document information the signature does not convey.** Include important
  side effects, failure modes, mutation, ownership, ordering, units, invariants,
  lifecycle behavior, or environmental requirements when they matter to callers
  or maintainers.

* **Do not narrate the signature.** Parameter, return, and exception sections are
  useful when they add information, not merely because those things exist.
  Avoid descriptions such as "cutoff: The cutoff" or "Returns the result."

* **Docstrings are not logs.** Do not write about rejected alternatives or
  historical solutions. "Plain strings rather than an enum," "returned rather
  than printed," or "now returns a list instead of a dict" is usually irrelevant
  to a reader. What changed belongs in the commit.

* **Comments explain local reasons.** A comment such as "Copy before iterating
  because callbacks may remove listeners" records a constraint needed to modify
  the code safely. Prefer explaining why a surprising implementation detail is
  necessary over describing what the next line does.

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

### A contract that needs more than a summary

```python
def expire_sessions(cutoff):
    """Expire sessions last active before ``cutoff``.

    Expiration is permanent and invalidates outstanding refresh tokens.
    """
```

This is preferable to:

```python
def expire_sessions(cutoff):
    """Expire sessions."""
```

and to boilerplate that adds no information:

```python
def expire_sessions(cutoff):
    """Expire sessions.

    Args:
        cutoff: The cutoff.

    Returns:
        The result.
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

The goal is high information density: enough docume
