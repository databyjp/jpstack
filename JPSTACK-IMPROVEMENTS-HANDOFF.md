# jpstack improvement handoff

## Status

Planning only. No workflow or extension changes have been implemented from this discussion.

This handoff proposes independently testable improvements to `jpstack`. The main goal is to reduce low-value human supervision by moving decisions to the start of a task, grouping related decisions, and allowing bounded execution between human reviews. It does not propose a broad autonomous orchestrator or a sticky workflow router.

## Evidence from the session audit

A read-only audit screened 465 Pi session headers and analyzed the 20 newest eligible non-trivial task groups, covering 63 linked session files.

Key results:

- Median user turns before implementation: 1, range 0-4.
- Routine continuation approvals: 40 across 8 tasks.
- One long task, S09, accounted for 27 of the 40 approvals.
- S09, S10, and S13 accounted for 86 of 124 substantive product-decision turns.
- Scope corrections: 3 of 20 tasks.
- Supported false-completion cases: 2 of 20 tasks.
- Reviewer-requested rework: 2 of 20 tasks.
- Full requested-behavior coverage: 11 of 20 tasks.
- Product-surface validation: 5 of 20 tasks.
- Incomplete tasks: 4 of 20 tasks.

The audit supports two conclusions:

1. Repeated approval is mainly a long-task problem. Excluding S09 leaves 13 routine approvals across 19 tasks. Do not relax supervision for every task based on this sample.
2. Verification coverage is the broader problem. Both false-completion cases relied on evidence that did not support the reported result. Product execution found gaps that focused tests missed, but product execution alone did not guarantee full requirement coverage.

## Existing material

Read these sources before changing the workflow:

- `skills/gated-development/SKILL.md`
- `skills/gated-development/evals/evals.json`
- `skills/tdd/SKILL.md`
- `skills/jp-coding-preferences-reporting/SKILL.md`
- `pi-extensions/mindful-session/README.md`
- `pi-extensions/mindful-session/index.ts`
- `references/loops-you-can-trust.md`
- `references/the-complete-guide-to-pstack-pt-1.md`
- `references/the-complete-guide-to-pstack-pt-2.md`

Preserve these jpstack properties:

- one primary falsifiable assertion per checkpoint,
- explicit exclusions and stop conditions,
- tests through public interfaces,
- conditional rather than mandatory design work,
- separate Standards and Spec review axes,
- concise completion reports organized for human review.

## Pstack-inspired changes

Implement and evaluate these changes one at a time. Each step should remain useful if later steps are rejected.

### 1. Strengthen task completion and task boundaries

**Purpose:** Define explicit task-level completion and stopping semantics before automating continuation.

Update `skills/gated-development/SKILL.md` so one Product-contract approval includes:

- one Product outcome,
- explicit non-goals,
- an approved must-have behavior checklist,
- a checkable exit predicate,
- the intended validation surface.

Do not claim Product completion unless the exit predicate passes and every must-have behavior has current evidence from the approved validation surface. Suggestions and optional follow-ups do not block completion unless the Product contract includes them as must-have behavior.

Add a task-boundary rule. Start a new task only when the Product outcome or non-goals materially change. A changed checkpoint, implementation path, or validation method remains in the same task while its outcome and non-goals remain fixed. Do not carry approval into an adjacent Product outcome.

Add sanitized evaluation cases based on the audit:

- Product framing omits the must-have checklist, exit predicate, or validation surface. Expected action: request one complete Product-contract approval before checkpoint design.
- A configuration name suggests third-party behavior, but no authoritative source verifies it. Expected action: report the missing evidence without claiming Product completion.
- Focused tests pass, but the requested operational path has not run. Expected action: treat the tests as partial evidence.
- An approved must-have behavior has no evidence entry. Expected action: name the missing evidence without claiming Product completion.
- The validation method changes while the Product outcome remains fixed, and adjacent behavior is requested. Expected action: revise the current task's validation and create a new Product contract only for the adjacent outcome.

Do not add a task-status enum at this stage. Human approval still gates each checkpoint, so the report can state whether the exit predicate passed, which evidence is missing, what blocks progress, and the next permitted action directly.

**Primary assertion:** The skill does not claim Product completion when the exit predicate or any must-have behavior lacks evidence from the approved surface.

**Promotion rule:** Existing gated-development cases still pass, and the new regression cases pass across repeated runs.

### 2. Establish one reusable product-surface verification contract

**Purpose:** Give longer runs a trustworthy way to decide whether they are done.

Pilot this in one representative application before adding a general generator. Create a project-local `verify-<product>` skill with:

- `Doctor`: identifies the intended build and running instance.
- `Launch`: starts the product and waits for a readiness predicate.
- `Drive`: performs one load-bearing user action through the real entrypoint.
- `Evidence`: records resulting state, required side effects, and artifact locations.
- `Cleanup`: removes only state created by the verification run.

Map every requested behavior to a concrete observation. A successful command exit is not sufficient when the outcome includes persistence, retention, safety, or final-state behavior.

Seed one fault that focused tests do not catch and confirm the verifier fails. Generalize the pattern into a jpstack skill only after it succeeds in two projects.

**Primary assertion:** The verifier catches the seeded product-path fault and distinguishes the intended instance from a stale or incorrect one.

**Promotion rule:** The scenario runs from a clean checkout without human help and retains reproducible evidence after cleanup.

### 3. Front-load supervision with a bounded autonomy envelope

**Purpose:** Replace serial checkpoint approvals with one structured approval for long-running work.

Add an opt-in `Bounded` mode to gated development. Retain the current checkpoint-by-checkpoint flow as `Supervised` mode.

Before implementation, present one compact decision packet containing:

- outcome and non-goals,
- allowed file or responsibility scope,
- exit predicate,
- must-have behavior evidence checklist,
- verification surface,
- actions allowed without asking,
- ask-first conditions,
- external-effect permissions,
- retry and no-progress budgets.

Group all known blocking questions into this packet. Do not ask serial questions that could have been identified during framing. During execution, record cheap reversible assumptions for review rather than interrupting the run.

Ask first when a decision affects user-visible behavior, a public interface, a persisted schema, security or privacy, credentials, meaningful spend, irreversible or externally visible effects, material scope expansion, or a choice that would make retained work expensive to reject.

This policy allows the agent to execute several checkpoints without further human input while the Pi run remains active. It does not restart the agent after Pi settles or the process exits.

**Primary assertion:** A long task can complete several in-envelope checkpoints after one approval, while every ask-first decision still interrupts execution.

**Promotion rule:** In a matched trial, routine approvals in long tasks fall by at least 50% without increasing scope corrections, false completion, or reviewer-requested rework.

### 4. Add branch-aware task state

**Purpose:** Store the approved envelope, stopping semantics, and evidence as branch-aware structured state that Pi lifecycle hooks can inspect across turns, compaction, resume, and forks.

Create a separate task-state extension. Do not add this responsibility to `mindful-session`: private human notes and model-visible execution state have different interfaces.

The task-state module should expose a small model-callable interface and hide session-entry reconstruction. Its branch-local snapshot should contain:

- active outcome,
- non-goals and approved scope,
- current checkpoint,
- exit predicate,
- must-have behavior evidence checklist,
- attempts and budgets,
- evidence receipts,
- blocker or pending decision,
- next action,
- task state.

Use these task states:

- `ACTIVE`: work remains and the autonomy envelope permits another action,
- `WAITING`: continuation requires human input or an external condition,
- `VERIFIED`: the exit predicate passed and all required evidence is current,
- `FAILED`: the task did not satisfy its contract and no permitted recovery remains,
- `CANCELLED`: the user ended the task.

Give each required check a separate evidence verdict: `NOT_RUN`, `PASSED`, `FAILED`, `INCONCLUSIVE`, or `STALE`. A failed check does not make the task `FAILED` while an in-envelope recovery remains. Treat a blocker as a reason for `WAITING`, not as another task state.

Use Pi custom entries and tool-result `details` so state can be reconstructed for the active branch. Inject only a compact active contract into model context.

**Primary assertion:** Reloading, resuming, or forking restores the state belonging to that branch without leaking updates from another branch.

**Promotion rule:** Lifecycle tests cover reload, resume, fork, branch switching, malformed entries, and compaction.

### 5. Add guarded automatic continuation

**Purpose:** Continue a bounded task across automatic Pi turns without requiring the user to say "continue."

Add continuation only after the autonomy envelope, verification contract, and branch-aware state have passed their own trials.

Use Pi's settle lifecycle hook to continue only when:

- the task state is `ACTIVE`,
- no user decision is pending,
- the previous turn completed without error or abort,
- the exit predicate remains unsatisfied,
- the previous iteration produced a new progress or evidence receipt,
- retry and continuation budgets remain.

Stop automatic continuation when:

- the task reaches `VERIFIED`, `WAITING`, `FAILED`, or `CANCELLED`,
- an ask-first condition occurs,
- verification is inconclusive and no approved check can resolve it,
- two consecutive iterations produce no new progress evidence,
- a retry or continuation budget expires.

A failed or stale evidence verdict may continue when the autonomy envelope permits repair or revalidation. Move the task to `WAITING` rather than continuing indefinitely when progress needs human input. Pi should continue to own provider-level retries; task-level retries need a separate count.

**Primary assertion:** Eligible `ACTIVE` tasks continue across turns until they reach another task state, while simulated no-progress, abort, and ask-first cases stop.

**Promotion rule:** At least 80% of eligible fixtures reach `VERIFIED`, `WAITING`, `FAILED`, or `CANCELLED` without another user turn, with zero unbounded runs.

### 6. Bind verification evidence to the exact artifact

**Purpose:** Prevent a later edit from inheriting an earlier verification result.

Each verification receipt should include:

- task and checkpoint ID,
- Git HEAD,
- staged and unstaged diff digest,
- relevant untracked-file manifest or snapshot,
- validation command or product scenario,
- timestamp and result,
- artifact paths,
- evidence verdict.

Mark the evidence verdict `STALE` whenever the artifact identity changes.

**Primary assertion:** Any change to a verified input invalidates the previous verdict.

**Promotion rule:** Tests cover committed, staged, unstaged, and relevant untracked changes.

### 7. Add selective fresh behavioral verification

**Purpose:** Replace some human reproduction work with an independent verdict.

Keep the existing Standards and Spec review axes. Add a separate fresh-session Behavioral verifier only for:

- delegated changes,
- user-visible behavior,
- high-blast-radius changes,
- judgment-heavy verification.

Give the verifier only the outcome, artifact identity, verification contract, and repository standards. Do not use a fresh model merely to repeat one deterministic command.

**Primary assertion:** The behavioral verifier either finds an actionable defect missed by self-review or supplies evidence that reduces human verification work.

**Promotion rule:** Retain it only if a 20-change trial produces enough unique findings or saved review time to justify its token and latency cost.

### 8. Build a behavioral evaluation and learning loop

**Purpose:** Evaluate workflow changes instead of promoting them from persuasive prose or one unusual session.

Use Pi SDK or RPC to run old and candidate skill versions against sanitized fixtures in isolated sessions. Store:

- transcript,
- tool use,
- task state and evidence verdicts,
- assertion results,
- duration,
- token or model cost.

Use deterministic checks where possible. Use blinded human review before adding a model judge. Promote a workflow rule only after repeated evidence, a proposed enforcement mechanism, and a passing regression fixture.

**Primary assertion:** A candidate skill can be compared with the current skill on the same fixtures without knowing which output came from which version.

**Promotion rule:** Every default workflow change has failing-before evidence, repeated passing candidate runs, no material control-case regression, and recorded cost.

### 9. Consider small task-scoped workflow profiles only after the above trials

If routing remains a demonstrated problem, test a small set of task-scoped profiles such as investigation, bug, feature/refactor, long-run, review, and artifact-only. A profile should produce a compact task contract and expire with the task.

Do not copy Poteto's sticky router or its full playbook catalog. Pi loads skill descriptions into context, and persistent routing creates stale-task risk.

## Bugfixes, maintenance, and investigations

Keep these changes separate from the pstack-inspired workflow experiments so their results are not confounded.

### Maintenance: test both bundled extensions

The repository tests the Python bootstrap and configuration scripts but has no committed tests for either TypeScript extension.

Add tests for:

- `final-stamp` message classification, pending-user flushes, and TUI-only recording,
- `mindful-session` state replay, edits, deletion, invalid indexes, and documented session-global behavior.

Prefer pure reducers for state reconstruction and thin Pi lifecycle wiring. Add one root validation command that runs Python and TypeScript checks.

### Investigation: define the supported runtime

`pi-agent/settings.json` lists optional npm packages and machine-local absolute-path packages, while `add_symlinks.py` deliberately leaves user settings unchanged.

Document which behavior is:

- bundled and installed by jpstack,
- tracked but not installed,
- optional,
- machine-local or experimental.

Do not treat tracked settings as guaranteed jpstack behavior.

### Investigation: perform a focused S09 case study

S09 accounts for 27 of 40 routine approvals, ten scope corrections within its linked chain, and several later evidence failures. Analyze it separately before generalizing from the aggregate sample.

Determine:

- why approvals repeated,
- whether the Product outcome changed,
- where a new task boundary should have been created,
- which decisions could have been front-loaded,
- which questions correctly interrupted work,
- which verification evidence became stale or proved incomplete.

The result should refine the autonomy-envelope and task-boundary fixtures, not become a repository-specific workflow rule by itself.

### Investigation: improve future audit grouping

The audit had low confidence for the longest linked task groups. Define a repeatable grouping rule based on Product outcome and verification contract, not session linkage alone. A resumed session may continue one task; a new outcome within the same session should begin another task record.

## Recommended execution order

- Add the Product contract, must-have evidence mapping, and the task-boundary rule.
- Pilot one product-surface verifier with a seeded fault.
- Trial the bounded autonomy envelope while the current Pi run remains active.
- Re-audit a matched set of long tasks.
- Design and implement branch-aware task state.
- Add guarded continuation behind an opt-in flag.
- Add artifact-bound receipts.
- Trial selective fresh behavioral verification.
- Promote only changes that improve measured outcomes.

Do not combine these implementation steps. Each changes a different control mechanism and needs an independent result.

## Measures for the next audit

Use the previous 20-task audit as the baseline. Compare:

| Measure | Baseline | Initial target |
| --- | ---: | ---: |
| Full requested-behavior coverage | 55% | At least 80% |
| Supported false-completion cases | 10% | 0 |
| Tasks without a terminal report | 20% | Below 10% |
| Routine approvals in long tasks | S09 had 27 | Reduce by at least 50% |
| Tasks with scope correction | 15% | No increase |
| Tasks with reviewer-requested rework | 10% | No increase |

Do not require product-surface validation for every task. Require the chosen validation surface to match the requested behavior.

## Explicit non-goals

Do not add these without separate evidence of need:

- a sticky mega-router,
- mandatory delegation,
- routine multi-model voting,
- a fixed multi-lane plan format,
- Cursor command compatibility,
- Graphite-specific orchestration,
- automatic external actions outside the approved envelope,
- automatic WIP commits,
- transcript scraping for continuity,
- duplicate todo, planning, worktree, or session databases.

## Suggested skills

The next agent should call the Skill tool for:

- `gated-development` before implementing each non-trivial checkpoint,
- `tdd` for the extension tests, task-state behavior, and evaluation runner,
- `codebase-design` before choosing the task-state interface or seam,
- `code-documentation` when adding the model-callable task-state interface,
- `domain-modeling` only if a hard-to-reverse task-state or receipt decision warrants an ADR,
- `unslop` when revising skill prose or durable documentation.

Use `show-me` if a lifecycle or branch-state diagram would reduce review effort.
