---
name: docstrings
description: >-
  Use when writing or reviewing code, and whenever
  writing or editing docstrings and comments.
---

---

name: docstrings
description: >-
Use when writing or reviewing code, and whenever
writing or editing docstrings and comments.
-------------------------------------------

# Docstrings

A docstring gives the reader context for a module, type, or callable and describes its role or contract.

A comment explains local behavior or constraints that the code cannot make clear.

Neither records the session that produced the code.

## Rules

* **Give the reader an entry point.** Prefer a descriptive, concise docstring. State what the symbol does and its role or important behavior so the reader can orient themselves before reading its implementation.

* **Keep it concise, not minimal.** Include enough information for a caller or maintainer to understand the symbol's purpose and important contract.

* **Docstrings are not logs.** Do not write about rejected alternatives or historical solutions. "Plain strings rather than an enum," "returned rather than printed," or "now returns a list instead of a dict" is usually irrelevant to a reader. What changed belongs in the commit.

* **Comments explain local reasons.** A comment such as "Copy before iterating because callbacks may remove listeners" records a constraint needed to modify the code safely. Prefer explaining why a surprising implementation detail is necessary over describing what the next line does.

* **Cut context the reader cannot reach.** Stack layer numbers, ticket IDs, sprint names, "as discussed above," and "as requested" do not belong in the code. "Implementation lands in L1" means nothing outside the session.

## What good looks like

Prefer:

```python
def expire_sessions(cutoff):
    """Expire sessions last active before ``cutoff``.

    Expiration invalidates outstanding refresh tokens.
    """
```

over either:

```python
def expire_sessions(cutoff):
    """Expire sessions."""
```

or:

```python
def expire_sessions(cutoff):
    """Expire sessions.

    Args:
        cutoff: The cutoff.

    Returns:
        The result.
    """
```

The goal is high information density, not the fewest possible words.

## Where the cut text goes

When the information is worth preserving, consider these destinations:

* Why a design won, and what lost: an ADR.
* Vocabulary, and how the pieces fit: `CONTEXT.md` or equivalent project docs.
* What this change does and why now: the commit message or PR description.

Do not create a new project-level documentation convention merely to relocate
low-value commentary. Consult the user before introducing a new documentation
artifact or convention when the repository does not already have one.
