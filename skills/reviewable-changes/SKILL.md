---
name: reviewable-changes
description: >-
  Use this skill when writing code another person will have to review —
  implementing a feature, fixing a bug, refactoring, adding a module or
  integration, or preparing a pull request. Its job is to keep each change small
  enough that one person can actually hold it in their head — one slice per turn,
  stopping between them, rather than a correct-looking diff nobody can check. It
  does that by investigating before editing, holding a declared diff budget,
  leaving opportunistic cleanup out, agreeing the signature before the
  implementation whenever a slice creates a new boundary, reporting scope
  explicitly, and decomposing anything larger into an ordered stack of dependent
  PRs delivered one at a time. Reach for it when the task sounds broad
  ("add search", "migrate X", "build the backend for Y"), when a working diff has
  spread across several files or concerns, or when asked to split, slice, or
  salvage a diff that got too big — even if the user never says "PR", "scope", or
  "review". Not for reviewing someone else's PR, writing commit messages, or
  resolving merge conflicts.
---

# Reviewable Changes

Producing code is cheap; reviewing it is not. The bottleneck in AI-assisted engineering is the human review budget, so aim for diffs where a reviewer can see the intent, bound the behaviour change, check the evidence, and decide.

**The size of the change is the constraint that everything else serves.** A person can hold a few hundred lines in their head at once. Past that, review degrades into skimming and approval stops meaning anything — so an oversized diff has already failed, however well-placed its seams are, however honest its tests are, however carefully its scope is reported. Where any instruction below seems to compete with keeping the change small, keeping it small wins.

Good design does not earn extra size. It is the most common way this goes wrong: the work is going well, the next layer is obvious, and shipping it now feels efficient. It is not efficient. It moves the cost onto the one person in the loop who cannot parallelise.

## The core loop

1. **Plan before editing.** Report the plan — including signatures, if the slice creates a new boundary. No edits in the investigation turn.
2. **Set a diff budget.** Files, concept boundary, validation command, before writing code.
3. **Implement one slice, then stop.** One behaviour change, one validation command, no opportunistic cleanup. End the turn there.
4. **Report scope.** What changed, what deliberately did not, what is left over.
5. **Stack the rest.** More than one slice means ordered dependent layers, delivered one per turn — never all of them at once.

Never collapse 1 and 3. That is how a small request becomes a 1,500-line pull request: the agent discovers a large plan and immediately starts executing it, and by the time a human sees it, rejecting the scope means throwing away work that is partly good.

Never run the stack in one turn either. Planning five layers and then building all five fails in exactly the same way as never planning, because the human still receives one indivisible diff. Each layer is its own turn, its own review, and its own chance to be told the design is wrong while changing it is still cheap.

## Step 1 — Investigate, then stop

Beyond a one-line fix, the first turn produces a plan and no edits:

- the root cause, or the mechanism to change,
- the files you would touch, and which you would not,
- the smallest safe slice,
- what test should fail before the fix (for bugs),
- the validation command.

Then wait for the human to confirm scope. A wrong plan costs a paragraph here and a diff later.

Skip only for the genuinely trivial: a typo, a version bump, a one-line guard the user already described precisely.

**If the slice creates a new seam** — a boundary later code will depend on (new module or service, first integration with an external system, an extraction, a new layer where none existed) — the plan also carries the types crossing it, the signatures including error cases, which way dependencies point, and what the caller is deliberately prevented from seeing. Bodies stay empty until that is agreed: an interface is cheap to review and expensive to reverse, and a wrong one gets paid for in every slice built above it. Most new files create no seam — a fifth endpoint inherits its contract from the four before it. Details in `references/contract-first.md`.

## Step 2 — Set the diff budget

Declare the shape before the diff exists, so the reviewer can check the patch against a contract instead of guessing at one.

- **File boundary:** edit only files under `<dir>`; no generated files, build config, lockfiles, or API clients.
- **Concept boundary** (the important one): fix retry handling, not validation; add the parser case, not a parser redesign; improve the error message, not the error taxonomy.
- **Which axis:** a new-seam slice is reviewed on its interface, a behind-seam slice on its behaviour diff. Do not mix them in one patch — the reviewer cannot tell which question they are being asked.

**Default ceiling: roughly 400 lines of production diff, or one module's worth of behaviour — whichever is smaller.** Past that a reviewer is skimming, and a skimmed approval is worth nothing. Some changes are legitimately larger: migrations, generated clients, mechanical renames. But "legitimately large" is a claim you make in the plan and the human accepts, never a default you drift into while the work is going well.

If the implementation is about to exceed the budget, **stop and say so** rather than quietly widening it. Ship what fits, report it, and put the rest in the next slice.

## Step 3 — Implement one slice

- One production behaviour change.
- Tests cover only the behaviour being changed.
- Do not reformat unrelated code, rename public symbols, or add dependencies.
- Do not change logs, metrics, error messages, or data formats unless the task requires it.
- **No opportunistic cleanup.** List it under follow-ups instead. If cleanup is genuinely required to make the change safe, isolate it in its own commit and say why.
- **One layer per turn.** Write the scope report and stop, even when the next layer is obvious and you have already designed it. Knowing what comes next is not a reason to build it now — it is what makes the next turn cheap.

"While I was here" is where small tasks become large reviews: mixing cleanup with a behaviour change means the reviewer can no longer tell mechanical lines from semantic ones.

### Test evidence

The review question is always: *would any test fail without the production change?* For bugs, write the failing test, watch it fail, make the smallest change, then run focused and broad. State the claim concretely:

```
Added `test_rejects_expired_session_at_boundary` — covers the bug because the
old comparison used `>` instead of `>=`.
Focused: pytest tests/test_sessions.py::test_rejects_expired_session_at_boundary -q
Broader: make test-sessions
```

"Added tests" is not reviewable. Tests written to justify the patch they ship with deserve more scrutiny than the patch, not less.

## Step 4 — Report scope

End every slice with a scope report, which becomes the PR description: **Scope** (one sentence), **Changed**, **Not changed**, **Validation** (focused and broader commands), **Follow-ups (not in this PR)**. Full template in `references/pr-template.md`.

**Not changed** carries the most weight. It states which boundaries mattered and makes drift visible — a reviewer who reads "logging and metrics unchanged" will spot a stray logging line immediately.

## Step 5 — Stack the work

More than one slice means an ordered stack, each layer a single concern with one natural reviewer:

| Layer | Ships | Depends on | Reviewer |
|---|---|---|---|
| L0 | types, module boundaries, stubbed signatures (new-seam work only) | main | tech lead |
| L1 | typed data model + seed data + access module | L0 | data owner |
| L2 | validated API endpoint | L1 | backend owner |
| L3 | client wiring against the real API | L2 | frontend owner |
| L4 | UI states and presentation | L3 | UI owner |

Each layer names what it publishes for the layer above; a layer that publishes nothing belongs to the layer below it. Split by *reviewer audience* rather than by size — L3 and L4 split even with a single author. Tell reviewers the direction: **read top-down for context, review bottom-up to build on checkpoints.**

**Present the table, get it agreed, implement L0, and stop.** The table is a plan for several reviews, not a checklist to work through in one turn. A stack delivered all at once is not a stack; it is a large diff with headings.

Git mechanics, `gh stack`, mid-stack rebasing, and slicing an existing diff: `references/stacking.md`.

## Salvaging a diff that is already too big

Do not review it heroically, or ask a human to. Propose a split first, editing nothing: for each patch, its goal, files, behaviour risk, tests, and whether it ships independently. This often reveals that "one small change" was three — add observability, fix the behaviour, clean up the abstraction that hid the behaviour. All three may be worth doing, in three reviews.

## Reviewability smells

Stop and slice rather than pushing harder when:

- The change is bigger than one sitting's review — a reviewer would have to skim to reach the end. This one outranks the rest: fix it by slicing, never by explaining.
- Several layers of a planned stack arrived in a single diff.
- The title says "fix bug" but the diff is mostly refactor.
- Tests were rewritten more heavily than production code.
- Formatting changed in files unrelated to the task.
- A helper carries generality nobody asked for: unused parameters, config hooks with no caller, a strategy pattern with one strategy. (A narrow interface over a deep implementation is the goal, not this smell.)
- A seam is shaped like the thing on the far side of it — an SDK, a wire format, a driver — rather than like what the caller needs. The tell is a test fake that imitates a third-party client.
- Logs, metrics, or error messages changed without being mentioned.
- Build files or lockfiles changed as a side effect of an import decision.
- The summary is confident but names no validation command.
- The patch crosses ownership boundaries.
- TODOs were left behind that are really unresolved design questions.
- A reviewer could not tell which lines are mechanical and which are semantic.

## The human owns the change

The agent drafts the patch; the human owns the pull request, including its scope. Surface scope decisions rather than resolving them silently — leaving work out is reversible in one line, blending it in is not.
