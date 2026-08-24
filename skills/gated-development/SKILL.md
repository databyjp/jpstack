---
name: gated-development
description: >-
  Use this for any non-trivial coding changes. E.g. where misunderstanding or a large diff
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

## Gated sequence

Run one gate at a time. Each gate must use decisions approved at earlier
gates. Approval advances only the current gate; do not begin
later design work or implementation.

Use read-only tools during the four design gates. Do not edit code.

A gate may take several rounds. If unresolved decisions remain, ask only
questions whose prerequisites are settled and give a recommended answer for
each. Treat answers and corrections as clarification, not approval. Revise the
current gate after the human answers, then stop again.

Ask for approval only when no unresolved decisions remain. Approval must be
explicit.

### Product gate

Define the problem in the user's terms, what success means to the end user,
non-goals, and open product decisions. For user-visible output, consider a rough
mockup rather than relying on prose alone.

Do not propose system or program design yet. Stop for product approval.

### System gate

Using the approved product brief, define changed contracts, data flow,
dependencies, external systems, and failure paths. Separate unresolved choices
from recommendations.

Do not propose files, internal types, or implementation slices yet. Stop for
system approval.

### Program gate

Using the approved system design, present the file-tree diff, changed call
paths, key types and signatures, invariants, and error modes. Use the
`codebase-design` skill when an interface or seam needs designing.

Do not plan implementation slices yet. Stop for program approval.

### Slice gate

Using the approved program design, propose ordered vertical slices. A vertical
slice ends in behavior that an end user or external caller can exercise. It
crosses every technical layer required for that behavior.

A slice may use a temporary fake or hard-coded value, but name the substitution
and the later slice that removes it. A database migration, backend module,
endpoint, or frontend screen alone is a technical layer, not a vertical slice.

For every slice, state:

- Observable behavior
- Automated test and manual probe
- Files expected to change
- Explicit exclusions
- Review budget

Prefer 100-200 lines of code for uncertain work. Any larger budget
requires explicit human approval. Stop for approval of the slice plan.

## Execution gate

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
   the review budget, stop and return to the relevant earlier gate.
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
