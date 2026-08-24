---
name: docstrings
description: >-
  Use when writing, editing or reviewing docstrings and code comments.
---

# Docstrings

A docstring describes a callable's contract. A comment explains local behavior or constraints that the code cannot make clear. Neither records the session that produced the code.

## Rules

- **Keep it concise.** More text means more cognitive load and room for error.
- **Document the non-obvious contract.** Include side effects, raised exceptions,
  units, ordering guarantees, mutation, or ownership when the signature and code
  do not make them clear. Do not restate the signature as "Returns the result."
- **Docstrings are not logs.** Do not write about rejected alternatives or
  historical solutions. "Plain strings rather than an enum," "returned rather
  than printed," or "now returns a list instead of a dict" is usually irrelevant
  to a reader. What changed belongs in the commit.
- **Comments explain local reasons.** A comment such as "Copy before iterating
  because callbacks may remove listeners" records a constraint needed to modify
  the code safely.
- **Cut context the reader cannot reach.** Stack layer numbers, ticket IDs,
  sprint names, "as discussed above," and "as requested" do not belong in the
  code. "Implementation lands in L1" means nothing outside the session.

## Where the cut text goes

Consider these solutions instead (consult the user if these files do not exist)
- Why a design won, and what lost: an ADR.
- Vocabulary, and how the pieces fit: CONTEXT.md.
- What this change does and why now: the commit message or PR description.
