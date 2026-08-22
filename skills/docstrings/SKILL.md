---
name: docstrings
description: >-
  Use when writing, editing or reviewing docstrings and code comments.
---

# Docstrings

A docstring should only describe the thing. Do not treat it as logs of the session that built it.

## Rules

1. **Keep it concise.** More text means more cognitive load & room for error.

2. **Docstrings are not logs.** Do not write about rejected alternatives, or historical solutions.
  "plain strings rather than an enum", "returned rather than printed", or "now returns a list instead of a dict" is usually irrelevant to a reader. What changed belongs in the commit.

3. **Cut context the reader cannot reach.** Stack layer numbers, ticket ids,
   sprint names, "as discussed above", "as requested". "Implementation lands in
   L1" means nothing outside of the code.

## Where the cut text goes

- Why a design won, and what lost: an ADR.
- Vocabulary, and how the pieces fit: CONTEXT.md.
- What this change does and why now: the commit message or PR description.
