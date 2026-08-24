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
4. **Slices:** ordered vertical slices with observable behavior, validation,
   expected scope, and a review budget for each.

Use the `codebase-design` skill when an interface or seam needs designing.

Do not edit code during this gate. Stop for human approval.

## Execution gate

A vertical slice ends in behavior that an end user or external caller can
exercise. It crosses every technical layer required for that behavior. A slice
may use a temporary fake or hard-coded value, but the plan must name the
substitution and the later slice that removes it.

A database migration, backend module, endpoint, or frontend screen alone is a
technical layer, not a vertical slice.

Before editing, restate the approved slice:

- Observable behavior
- Test and manual probe
- Files expected to change
- Review budget
- Explicit exclusions

Then:

1. Implement the smallest end-to-end path that satisfies the slice.
2. Do not add behavior intended for later slices.
3. Do not perform unrelated cleanup, reformatting, or dependency changes.
4. If the work requires a changed contract, an unapproved file, or more than
   the review budget, stop and return to the design gate.
5. Run the agreed automated test and manual probe. If a probe cannot be run,
   state why rather than silently skipping it.
6. Inspect the final diff for changes outside the approved scope.
7. Report the result and stop for human review.

Do not begin another slice without another approval.

## Review report

Use the `jp-coding-preferences-reporting` skill. At minimum, report:

- **Scope:** the approved behavior and review budget.
- **Changed:** a reading order, with the question each important file answers.
- **Not changed:** adjacent behavior and later slices deliberately left alone.
- **Validation:** exact commands and probes run, with their outcomes.
- **Where to push:** the part of the change you are least confident about.
- **Decision requested:** what the human is being asked to approve.
- **Follow-ups:** remaining slices or newly discovered work, without starting it.
