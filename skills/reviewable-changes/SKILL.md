---
name: reviewable-changes
description: >-
  Use before working on a codebase, e.g. writing code, or working on coding-related tasks.
  Keeps each change small enough to hold in one head.
  Not for reviewing someone else's PR, writing commit messages, or resolving merge conflicts.
  Not for non-codebase tasks, like creating SVG graphics for example, which involves code but the code isn't the output.
---

# Reviewable changes

Producing code is cheap; reviewing it is not. Follow the below steps so that we can prevent unwanted changes, or going in the wrong direction, before things progress too far.

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
