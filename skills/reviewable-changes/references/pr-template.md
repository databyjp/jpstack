# PR description template

A PR description should make review easier, not narrate that work happened. Reviewers need handles: a declared scope they can check the diff against, explicit boundaries so drift is visible, and commands they can actually run.

Fill this out from the scope report produced at the end of the implementation slice.

---

## Template

```markdown
## Scope

<One or two sentences: what behaviour changes, and where. Name the module.>

## Changed

- <behaviour change, stated as behaviour rather than as edits>
- <test added or updated, and what it covers>

## Not changed

- <adjacent behaviour a reviewer might reasonably fear you touched>
- <public API / logging / metrics / schema / retry behaviour, as applicable>

## Validation

- Focused: `<command that exercises exactly this change>`
- Broader: `<suite or check command>`
- <manual verification steps, if the change is user-facing>

## Review notes

- <which parts are mechanical vs semantic, if the diff mixes them>
- <anything you want the reviewer to look at hardest>

## Follow-ups (not in this PR)

- <cleanup spotted and deliberately left alone>
- <adjacent instance of the same bug, with location>

## AI assistance

- <what the agent did: investigated X, drafted the patch for Y>
- <what the human decided: selected the scope, reviewed the final diff>
```

For a stacked PR, add a stack map and reading order at the top:

```markdown
Stack: #101 (data) ← #102 (api) ← **this PR** (wiring) ← #104 (ui)
Read top-down for context; review bottom-up.
```

---

## Worked example

```markdown
## Scope

Fixes acceptance of expired sessions at the exact expiry boundary in `SessionValidator`.

## Changed

- Sessions whose expiry equals the current timestamp are now rejected (was accepted).
- Added `test_rejects_expired_session_at_boundary`.

## Not changed

- Session refresh behaviour.
- Token parsing.
- Logging, metrics, and public method names.
- Database schema.

## Validation

- Focused: `pytest tests/test_sessions.py::test_rejects_expired_session_at_boundary -q`
- Broader: `make check`

## Review notes

- One-character semantic change (`>` → `>=`); the rest of the diff is the new test.

## Follow-ups (not in this PR)

- `TokenValidator.is_valid` has the same off-by-one shape at line 84 — worth checking separately.

## AI assistance

- Agent traced the session validation path and drafted the fix and test.
- Human selected the scope and reviewed the final diff.
```

---

## Pre-submit checklist

Run through this before opening the PR. Anything failing is a reason to slice, not a reason to add a caveat to the description.

**Scope**
- [ ] The diff matches the budget agreed in the plan.
- [ ] No opportunistic cleanup, reformatting, or renames rode along.
- [ ] No new dependencies, unless that was the task.
- [ ] Generated files, lockfiles, and build config are untouched, or the generator command is named.
- [ ] The change stays within one ownership area, or the split by owner is explained.

**Evidence**
- [ ] Some test fails without the production change.
- [ ] Tests were not rewritten more heavily than the production code.
- [ ] The focused command is real and was actually run.
- [ ] The title describes what the diff mostly is.

**Reviewability**
- [ ] Mechanical and semantic changes are separated, or clearly labelled.
- [ ] The "Not changed" list names the boundaries a reviewer would worry about.
- [ ] Follow-ups are listed rather than implemented.
- [ ] No TODOs left that are actually unresolved design questions.
