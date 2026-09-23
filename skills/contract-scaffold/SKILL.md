---
name: contract-scaffold
description: >-
  Create syntactically valid but intentionally incomplete source that makes
  proposed interfaces, types, errors, schemas, and module seams reviewable. Use
  when behavior must remain unimplemented for review. When the scaffold is only
  a phase of a working implementation, use it under gated-development.
---

# Contract scaffold

Create reviewable source artifacts that resolve necessary interface decisions
while leaving behavior explicitly incomplete. A scaffold supports design review;
it does not prove Product behavior.

## Establish control

Choose the primary skill by the final outcome:

- For intentionally incomplete source, this skill is primary. Apply
  `gated-development` governance before non-trivial repository edits.
- For working behavior, `gated-development` is primary. Apply this skill only to
  its scaffold design phase.

Use `codebase-design` when choosing an interface or seam and
`code-documentation` for externally visible declarations. Use
`jp-coding-preferences-reporting` for the final review order.

Before editing, identify:

- authoritative project artifacts and terminology;
- the caller-facing interface under review;
- decisions the available evidence does not settle;
- excluded behavior and artifacts;
- whether the scaffold will be retained.

Do not invent a domain decision to complete a declaration. Surface decisions
that affect observable semantics, persisted data, ownership, lifecycle, errors,
or significant seams.

## Build from the interface inward

Start with the caller-facing interface. Add only declarations needed to
understand its contract and orchestration.

- Keep source syntactically valid and use the project's existing type system.
- Document caller-visible semantics, invariants, side effects, and failure modes.
- Use explicit `NotImplementedError`, an equivalent typed hole, or an unmistakable
  placeholder for missing behavior.
- Put pseudocode in comments rather than executable bodies.
- Do not return plausible placeholder values that could appear to work.
- Add a real caller or usage example only when it fits the approved scope.
- Add a seam only when callers, tests, or actual variation justify it.
- Do not add tests, dependencies, integrations, or entrypoints unless the
  scaffold contract includes them.

Keep implementation freedom explicit. Constrain public contracts and important
invariants, not private algorithms or speculative internal structure.

## Validate the scaffold

Choose the cheapest checks that support structural claims, such as parsing,
compilation, type checking, schema validation, importability, or repository
search. Confirm that:

- declarations agree with authoritative project artifacts;
- each intentional hole is explicit;
- excluded behavior and artifacts remain absent;
- every changed file contributes to the proposed interface.

Report these checks as structural evidence only. Do not claim the Product
behavior works. If implementation reveals that an approved contract must
change, stop under `gated-development` rather than weakening the scaffold.

## Stop and report

Stop before behavior implementation. Add tests only when the approved scaffold
contract includes them. Report:

1. a consequence-ordered reading order;
2. proposed interface and seam decisions;
3. intentional implementation holes;
4. unresolved domain decisions;
5. decisions required before tests or implementation;
6. structural validation results;
7. confirmation that excluded behavior remains absent.
