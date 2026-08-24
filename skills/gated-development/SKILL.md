---
name: gated-development
description: >-
  Use for non-trivial coding changes. E.g. where misunderstanding or a large diff
  would be expensive. Design the change with the user, divide it into vertical
  slices, and implement only a human-approved slice before stopping for review.
---

# Gated development

Perform development in stages. The human approves design and scope.
The agent investigates, proposes, and implements one approved slice at a time.

## Choose a lane

- **Small:** obvious, low-risk, and easy to review. Implement directly.
- **Gated:** everything else; misunderstanding or a large diff would be slower, add re-work, or lower quality. Follow the gates below.

State which lane you recommend. When uncertain, use the gated lane.

## Design gate

Investigate the codebase, then present a short change brief containing:

1. **Product:** the problem being solved, what success means (to the end user), and non-goals.
2. **System:** changed contracts, data flow, dependencies, and failure paths.
3. **Program:** file-tree diff, changed call path, and key types and signatures.
4. **Slices:** ordered vertical slices with a test or manual probe for each.

Use the `codebase-design` skill when an interface or seam needs designing.

Do not edit code during this gate. Stop for human approval.

## Execution gate

A vertical slice adds one observable behavior through the system. It may cross
the database, backend, and frontend. It is not a technical layer.

For the approved slice:

1. State the files and behavior in scope.
2. State what remains out of scope.
3. Implement only that slice.
4. Run its automated test and manual probe where applicable.
5. Stop for human review.

Do not continue to another slice without another approval.

## Review report

Report:

- Scope
- Changed
- Not changed
- Validation
- Follow-ups
