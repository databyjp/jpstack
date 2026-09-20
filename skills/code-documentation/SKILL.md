---
name: code-documentation
description: >-
  Use when writing or reviewing code that adds or changes an externally visible
  interface, or when writing or reviewing documentation comments or
  implementation comments.
---

# Code documentation

Documentation attached to a declaration is part of the module's interface.
Implementation comments help maintainers understand and safely change the code.

## Interface documentation

* **Document every external interface.** Document each externally visible
  module, type, and callable at its declaration or the narrowest enclosing
  externally visible scope.

* **Explain the abstraction and caller-visible contract.** Describe the purpose,
  responsibility, or mental model and when to use it. Include relevant input
  semantics, guarantees, side effects, failure modes, mutation, ownership,
  ordering, units, invariants, lifecycle, environmental requirements, and
  performance characteristics.

* **Make interface documentation self-contained.** Ensure callers can understand
  and use the abstraction without reading its implementation. Describe
  observable behavior, not internal control flow or strategy.

## Implementation comments

* **Explain non-obvious implementation decisions.** Add a local comment when
  changing the code safely requires information the code does not make clear,
  such as rationale, an invariant, a dependency, or an edge case. Do not
  narrate the implementation or repeat the interface contract.

* **Document meaningful internal declarations.** Document private modules,
  types, or callables when their abstraction, contract, or invariant would
  otherwise be costly to infer.

## Rules for both

* **Write at a different level from the code.** Add higher-level abstraction or
  rationale, or lower-level precision about exact semantics. Remove comments
  that repeat the code at the same level.

* **Improve declarations before compensating with prose.** Use clear names,
  precise types, and cohesive interfaces where the language permits. Use
  documentation to supplement strong declarations, not excuse vague names or
  unstructured values.

* **Be complete, then concise.** Use a one-line docstring only when it
  completely states the useful contract. Use `Args`, `Returns`, `Raises`, or
  `Attributes` sections when details need to be found independently. Do not add
  sections that only repeat names and types.

* **Keep documentation durable and reachable.** Do not preserve development
  chronology or refer to stack layers, tickets, sprints, or prior discussion.
  Put change history in commits and broader architectural trade-offs in an ADR.

## Examples

### Higher-level abstraction

Describe what a type represents rather than listing visible fields:

```python
@dataclass(frozen=True)
class ResolvedExperiment:
    """Validated experiment inputs resolved to project-relative resources."""
```

### Lower-level precision

Clarify semantics that the declaration cannot express:

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

### Implementation rationale

Record the constraint rather than narrating the operation:

```python
# Copy before iterating because callbacks may remove listeners.
for listener in list(self._listeners):
    listener(event)
```

Do not replace this with `# Iterate over listeners`.
