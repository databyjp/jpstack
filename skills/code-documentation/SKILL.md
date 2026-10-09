---
name: code-documentation
description: >-
  Use when writing or reviewing code that adds or changes an externally visible
  interface, contains decision-dense implementation logic, or when writing or
  reviewing documentation comments or implementation comments.
---

# Code documentation

Documentation attached to a declaration is part of the module's interface.
Implementation comments help maintainers understand and safely change the code.

Unless instructed otherwise, keep each declaration focused on its caller-visible
contract. Do not document design omissions or future plans.

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

* **Put details at the narrowest owning scope.** Lead module and type
  documentation with the abstraction and its use before narrower invariants or
  failure details. Put callable-specific inputs, outputs, side effects, and
  failures on that callable. Keep an invariant at type level only when it spans
  operations or callers must understand it before choosing an operation.

* **Describe divided responsibilities as data flow.** When documentation
  distinguishes the declaration's work from other work, name the subject
  responsible for each behavior and state what passes between them. Prefer
  positive input-to-output statements over listing work one subject does not
  perform. Negative exclusions leave ownership unclear and can imply an extra
  abstraction.

## Implementation comments

* **Explain non-obvious implementation decisions.** Add a local comment when
  changing the code safely requires information the code does not make clear,
  such as rationale, an invariant, a dependency, or an edge case. Do not
  narrate the implementation or repeat the interface contract.

* **Review decision-dense code before finishing.** Inspect branches, ordering,
  conversions, retries, compatibility workarounds, and side effects. Add a
  nearby comment when names, types, and control flow show what happens but not
  why the behavior is required.

* **Explain invisible orchestration guarantees.** Comment ordering constraints,
  checkpoints, recovery behavior, idempotency, and side-effect boundaries when
  moving or removing a statement could silently change behavior.

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

### Injected collaborators

Document the capability or variation that an injected collaborator gives the
enclosing interface. Explain what behavior the caller selects, along with any
ownership, reuse, ordering, or lifecycle contract that matters.

Do not paraphrase the collaborator's type or method names. If the enclosing
docstring already explains the relationship and there is no additional
parameter contract, omit the `Args` entry.

Rather than:

```python
Args:
    trial_executor: Adapter that executes individual Trials.
```

Prefer:

```python
"""Run Experiment orchestration through a caller-selected execution mechanism.

`TrialExecutor` lets the same orchestration submit Trials to Harbor or to a
deterministic in-process implementation.
"""
```

Only document concrete alternatives when the interface actually supports them.

## Examples

### Higher-level abstraction

Describe what a type represents rather than listing visible fields:

```python
@dataclass(frozen=True)
class ResolvedExperiment:
    """Validated experiment inputs resolved to project-relative resources."""
```

### Divided responsibility

Name both subjects and describe their input-to-output relationship:

```python
"""Task-specific criterion checks supply results in brief order.

This class converts those results into the detailed rubric and Harbor reward
output.
"""
```

Do not replace this with:

```python
"""Task verifiers record decisions in authored order without implementing
scoring or output persistence themselves."""
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

### Invisible orchestration guarantee

Explain why a checkpoint occurs at that position:

```python
# Persist an incomplete run before executing work so failures leave a
# discoverable record.
retain_run_progress(complete=False)
```

Do not replace this with `# Retain run progress`.
