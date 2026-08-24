---
name: gated-development
description: >-
  Use this for any non-trivial coding changes. E.g. where misunderstanding or a large diff
  would be expensive. Design the change with the user, divide it into vertical
  slices, and implement only a human-approved slice before stopping for review.
---

# Gated development

The human approves each design gate and implementation slice.

## Choose a lane

- **Small:** obvious, low-risk, and easy to review. Implement directly.
- **Gated:** everything else; misunderstanding or a large diff would be slower, add re-work, or lower quality. Follow the gates below.

State which lane you recommend. When uncertain, use the gated lane.

## Gated sequence

Run Product, System, Program, Slice, and Execution gates in order. Work on one
gate at a time using only prior approved decisions. Use read-only tools before
execution.

A gate may take several rounds. While decisions remain, ask only unblocked
questions, recommend answers, revise the current artifact, and stop.
Clarification is not approval. Advance only after explicit approval of a
decision-complete artifact.

Keep review rounds small. Start with a short summary and ask no more than three
unresolved decisions per response. During clarification, show only affected
sections. Present the complete gate artifact only when it is ready for approval.

### Product gate

Define the problem in the user's terms, what success means to the end user,
non-goals, and open product decisions. Separate high-level user goals and
concrete post-use measures from acceptance criteria and non-negotiable
invariants. Recommend measurable thresholds for human approval. For
user-visible output, consider a rough mockup rather than relying on prose alone.

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
slice produces behavior that a user or external caller can exercise across
every required technical layer. A technical layer alone is not a slice. Name
any temporary substitution and the later slice that removes it.

For every slice, state:

- Observable behavior
- Automated test and manual probe
- Files expected to change
- Explicit exclusions
- Review budget

Prefer 100-200 lines of code for uncertain work. Any larger budget
requires explicit human approval. Stop for approval of the slice plan.

## Execution gate

Before editing, restate the approved slice using the five fields above.

Then:

1. Implement only the smallest end-to-end path. Do not add later behavior,
   unrelated cleanup, reformatting, or dependency changes.
2. If the work requires a changed contract, an unapproved file, or more than
   the review budget, stop and return to the relevant earlier gate.
3. Run the agreed automated test and manual probe. If a probe cannot be run,
   state why rather than silently skipping it.
4. Inspect the final diff for changes outside the approved scope.
5. Report the result and stop for human review.

Do not begin another slice without another approval.

## Review report

Use the `jp-coding-preferences-reporting` skill. Report scope, reading order,
what did not change, validation, the weakest point, the decision requested, and
follow-ups.
