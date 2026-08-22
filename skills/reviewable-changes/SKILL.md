---
name: reviewable-changes
description: >-
  Use when writing code someone will review: implementing a feature, fixing a
  bug, refactoring, adding a module or integration, preparing a pull request.
  Keeps each change small enough to hold in one head.
  Triggers on broad-sounding tasks ("add search", "migrate X", "build the
  backend for Y"), on a diff that has spread across several concerns, and on
  requests to split or salvage a diff that got too big. Not for reviewing
  someone else's PR, writing commit messages, or resolving merge conflicts.
---

# Reviewable changes

Producing code is cheap; reviewing it is not. **The size of the change is the
constraint everything else serves.** Where any instruction competes with
keeping the change small, small wins. Good design does not earn extra size.

If something is underspecified, call the Skill tool, for "grilling" to clarify intent.

1. **Plan, then stop.** Root cause, files you would and would not touch, the
   smallest safe slice, the test that should fail first, the validation
   command. No edits this turn, then wait for the human to confirm scope. Skip
   only for the genuinely trivial: a typo, a version bump, a one-line guard
   already described precisely. A new seam also needs its signatures agreed,
   bodies empty.
2. **Set a budget.** Declare it before the diff exists. File boundary, and the
   concept boundary that matters more: fix retry handling, not validation; add
   the parser case, not a parser redesign. For example ceiling ~400 lines of production
   diff or one module's behaviour, whichever is smaller. Migrations, generated
   clients, and mechanical renames can be larger, but that is a claim the human
   accepts in the plan, never a default you drift into. About to exceed the
   budget, stop and say so.
3. **One slice, then stop.** One behaviour change, tests covering only it. No
   opportunistic cleanup, reformatting, new dependencies, or quiet edits to
   logs, metrics, and error messages. End the turn even when the next layer is
   obvious.
4. **Report scope.** Scope, Changed, Not changed, Validation, Follow-ups. "Not
   changed" carries the most weight.
5. **Stack the rest.** Ordered layers, split by reviewer audience rather than
   by size, each naming what it publishes for the layer above. Present the
   table, get it agreed, build the first, stop.

Never collapse 1 and 3, and never run the stack in one turn. Both hand the
human one indivisible diff, which is the failure this skill exists to prevent.
The agent drafts the patch; the human owns its scope.
