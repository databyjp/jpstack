# jpstack improvement handoff

## Status

The Product contract, task-boundary rule, and evidence mapping were implemented in commit `79b55c3`. Commit `07df5f1` added proportional verification selection and compressed this roadmap. The working tree adds the S09 case study, an opt-in Bounded mode, and eight bounded-mode evaluation cases. The remaining work should proceed as separate executable checkpoints.

This handoff proposes independently testable improvements to `jpstack`. The main goal is to reduce low-value human supervision by moving decisions to the start of a task, grouping related decisions, and allowing bounded execution between human reviews. It does not propose a broad autonomous orchestrator or a sticky workflow router.

## Evidence from the session audit

A read-only audit screened 465 Pi session headers and analyzed the 20 newest eligible non-trivial task groups, covering 63 linked session files.

Key results:

- Median user turns before implementation: 1, range 0-4.
- Approval-only continuation turns: 40 across 8 session groups.
- The linked session chain labeled S09 accounted for 27 of the 40 turns.
- S09, S10, and S13 accounted for 86 of 124 substantive Product-decision turns under the original grouping.
- Scope corrections: 3 of 20 original groups.
- Supported false-completion cases: 2 of 20 original groups.
- Reviewer-requested rework: 2 of 20 original groups.
- Full requested-behavior coverage: 11 of 20 original groups.
- Product-surface validation: 5 of 20 original groups.
- Incomplete groups: 4 of 20.

The S09 case study found that its 23-session lineage contained at least seven Product tasks. Of its 27 approval-only turns, 13 were conservative candidates for bounded continuation and 14 approved a new Product outcome or crossed an ask-first boundary. See `references/s09-bounded-autonomy-case-study.md`.

The evidence supports two conclusions:

1. Session lineage is not a task boundary. Do not use S09's 27 turns as a single-task autonomy baseline. Evaluate bounded mode against the 13 reclassified continuation turns while preserving all 14 Product and ask-first gates.
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
- `references/s09-bounded-autonomy-case-study.md`
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

The five phases below organize the work. They do not permit combining implementation checkpoints. Complete and evaluate each named checkpoint before starting the next one.

### 1. Keep the completed Product contract as the foundation

Commit `79b55c3` added one Product-contract approval containing the outcome, non-goals, must-have behaviors, exit predicate, and validation surface. It also requires evidence for every must-have behavior before claiming Product completion and starts a new task only when the outcome or non-goals materially change.

`Supervised` remains the default. `Bounded` is available only through an explicit task-scoped approval packet.

### 2. Design and evaluate bounded mode

**Purpose:** Replace serial continuation approvals with one structured approval for eligible long-running work.

This phase contains four separate checkpoints:

1. **Completed:** Add a verification-selection rule to `gated-development`. The agent chooses the cheapest existing executable surface that establishes each must-have behavior and does not create a verification skill that merely wraps an existing test suite.
2. **Completed:** Perform the focused S09 case study. `references/s09-bounded-autonomy-case-study.md` reclassifies approvals, identifies Product boundaries, and defines sanitized fixtures.
3. **Deferred:** Do not build a general Pi SDK or RPC evaluation runner unless repeated manual comparisons become expensive or inconsistent. The current cases use isolated `pi --mode json` invocations and direct human assessment.
4. **Completed:** Add an opt-in `Bounded` mode while retaining `Supervised` mode. The human approves one task-scoped packet containing the Product contract, allowed scope, permitted actions, verification plan, ask-first conditions, external-effect permissions, and retry and no-progress budgets.

A verification skill is justified only when it captures reusable operational knowledge that existing tests or commands cannot express safely, such as instance identification, external infrastructure, readiness, credentials, retained evidence, or cleanup. Use a one-off check when reuse is unlikely.

Bounded execution initially applies only while the current Pi run remains active. It must interrupt for user-visible behavior changes, public interfaces, persisted schemas, security or privacy decisions, credentials, meaningful spend, irreversible or externally visible effects, material scope expansion, or choices that make retained work expensive to reject.

**Primary assertion:** An eligible task completes several in-envelope checkpoints after one approval, while every seeded ask-first decision interrupts execution.

**Synthetic result:** The baseline passed 6 of 8 S09-derived cases; the candidate passed 8 of 8. All 12 existing controls passed after one retained-test clarification. The candidate's clear gains were continuing after a completed checkpoint and recording each authorized external action separately. No seeded Product, schema, security, external-effect, or no-progress stop was suppressed. This supports an opt-in real-work trial, not a default-mode change.

### 3. Trial bounded mode on real multi-checkpoint Product tasks

Use bounded mode on 5 to 10 Product tasks expected to require several checkpoints. Keep short or ambiguous tasks in `Supervised` mode as a comparison group.

Measure bounded-eligible continuation turns, preserved Product and ask-first gates, substantive decisions, scope corrections, false completion, reviewer-requested rework, validation coverage, and incomplete tasks. Promote bounded mode only if bounded-eligible continuation turns fall by at least 50% without suppressing a required gate or increasing scope corrections, false completion, or rework.

This phase decides whether durable task state and automatic continuation are worth their implementation cost. Do not infer that decision from synthetic fixtures alone.

### 4. Build the continuation foundation

Begin this phase only if the bounded-mode trial succeeds. Implement its parts as separate checkpoints:

1. Complete the bundled-extension tests and root validation command described under maintenance.
2. Add a branch-aware task-state extension, separate from `mindful-session`. Persist the Product contract, autonomy envelope, active checkpoint, attempts and budgets, evidence, pending decision, next action, and task state.
3. Add artifact-bound evidence receipts containing the task and checkpoint ID, Git HEAD, staged and unstaged diff digest, relevant untracked-file manifest, validation command or scenario, result, timestamp, and artifact paths. Mark evidence `STALE` when the artifact identity changes.

Use these task states:

- `ACTIVE`: work remains and the autonomy envelope permits another action,
- `WAITING`: continuation requires human input or an external condition,
- `VERIFIED`: the exit predicate passed and all required evidence is current,
- `FAILED`: the task did not satisfy its contract and no permitted recovery remains,
- `CANCELLED`: the user ended the task.

Give each required check a separate evidence verdict: `NOT_RUN`, `PASSED`, `FAILED`, `INCONCLUSIVE`, or `STALE`. A failed check does not make the task `FAILED` while an in-envelope recovery remains.

**Primary assertion:** Reload, resume, compaction, forks, and branch switching restore only the active branch's task state, and any relevant artifact change invalidates prior verification.

### 5. Add guarded continuation, then reassess optional orchestration

Use Pi's settle lifecycle hook to continue only when the task is `ACTIVE`, no user decision is pending, the previous turn completed normally, new progress or evidence was recorded, and budgets remain.

Stop when the task reaches another state, an ask-first condition occurs, two iterations produce no progress, or a budget expires. A failed or stale evidence verdict may continue only when the approved envelope permits repair or revalidation.

**Primary assertion:** Eligible tasks continue across automatic turns until a defined stop condition, with zero unbounded runs.

**Promotion rule:** At least 80% of eligible fixtures reach `VERIFIED`, `WAITING`, `FAILED`, or `CANCELLED` without another user turn. Confirm this behavior in real tasks before changing the default.

After the next 20-task audit, decide whether evidence supports selective fresh-session behavioral verification or small task-scoped workflow profiles. Do not add either by default. Retain a fresh verifier only when it finds defects missed by self-review or measurably reduces human verification time. Add profiles only if routing remains an observed problem.

## Maintenance and investigations

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

### Completed investigation: focused S09 case study

`references/s09-bounded-autonomy-case-study.md` records the result. The 23 linked sessions contained at least seven Product tasks, so the original grouping overstated one task's continuation burden. The study reclassifies 13 of 27 approval-only turns as bounded-eligible, preserves 14 Product or ask-first gates, and defines sanitized fixtures for task boundaries, security stops, persisted outcome semantics, stale evidence, grouped external-run approval, and no-progress stops.

### Investigation: improve future audit grouping

The audit had low confidence for the longest linked task groups. Define a repeatable grouping rule based on Product outcome and verification contract, not session linkage alone. A resumed session may continue one task; a new outcome within the same session should begin another task record.

## Recommended execution order

1. Trial bounded mode on real Product tasks that need several checkpoints and compare it with supervised work.
2. If the trial succeeds, test the extensions, add branch-aware task state, and add artifact-bound receipts as separate checkpoints.
3. Add guarded continuation behind an opt-in flag and evaluate its stop behavior.
4. Re-audit 20 tasks before deciding on an evaluation runner, fresh behavioral verification, or workflow profiles.

Each phase has its own promotion gate. Do not begin its runtime machinery merely because the preceding skill prose is complete.

## Measures for the next audit

Use the previous 20-task audit as the baseline. Compare:

| Measure | Baseline | Initial target |
| --- | ---: | ---: |
| Full requested-behavior coverage | 55% | At least 80% |
| Supported false-completion cases | 10% | 0 |
| Tasks without a terminal report | 20% | Below 10% |
| Bounded-eligible continuation turns | S09 had 13 after reclassification | Reduce by at least 50% |
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
- `tdd` for the extension tests and task-state behavior,
- `codebase-design` before choosing the task-state interface or seam,
- `code-documentation` when adding the model-callable task-state interface,
- `domain-modeling` only if a hard-to-reverse task-state or receipt decision warrants an ADR,
- `unslop` when revising skill prose or durable documentation.

Use `show-me` if a lifecycle or branch-state diagram would reduce review effort.
