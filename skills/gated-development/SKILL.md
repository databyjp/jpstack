---
name: gated-development
description: >-
  Use for non-trivial codebase changes where misunderstanding or a large diff
  would make review or rework expensive. Design with the user, then implement
  one approved slice at a time. Do not use when code is only a means to produce
  a non-code artifact.
---

# Gated development

The human approves the design and each implementation slice.

## Choose a lane

- **Small:** obvious, low-risk, and easy to review. Implement directly.
- **Gated:** everything else. Follow the gates below.

State the recommended lane. When uncertain, use Gated.

## Gate protocol

Run Product, System, Program, Slice, and Execution in order. Use only approved
prior decisions and read-only tools until Execution.

For each gate:

1. Identify only the decisions that block the next gate. Defer decisions that
   can safely wait for a later gate.
2. Present one decision packet: the decision, recommendation, main trade-off,
   and one focused question. Use `ask_user_question` for two to four concrete
   choices.
3. Record the answer in a decision ledger. In later rounds, show only changed
   entries and the next open decision.
4. Once settled, show the compact ledger and deferred decisions, then ask for
   explicit gate approval.

Do not ask ceremonial questions when the prompt or an approved decision already
provides the answer. Clarification is not approval, and the final ledger must
not introduce decisions. Do not repeat one contract as a file tree, call path,
invariant list, and error table unless each view helps decide something.

When presenting a final gate ledger, mention once that Plannotator users can run
`/plannotator-last`. Its feedback is clarification; approval remains explicit.

### Example

For a request to delegate graphic creation between repositories, start with this
Product decision packet:

- **Decision:** Should the first milestone prove one real handoff?
- **Recommendation:** Yes. One request should produce a project-owned graphic
  while standalone designer use still works.
- **Trade-off:** This tests the workflow early but requires orchestration design.
- **Question:** Approve a one-graphic pilot?

Do not include exact output paths, agent configuration, or missing-file checks
in this gate. Those belong to System or Program.

A narrow first slice could prove that the producer invokes the designer in
plan-only mode and that the designer reads its repository instructions. Defer
rendering, output-path validation, variants, and documentation.

### Product gate

Agree on the problem, user-visible outcome, and non-goals. Include only
criteria a user can evaluate without knowing the implementation.

Defer paths, filenames, repository placement, invocation mechanics, validation
cases, and recovery mechanics unless the user explicitly made one a product
constraint. Stop for approval.

### System gate

Agree on changed contracts, data flow, dependencies, external systems, and
failure paths. Separate open choices from recommendations.

Do not propose files, internal types, or slices. Stop for approval.

### Program gate

Agree on the implementation shape. Use `codebase-design` when designing an
interface or seam. Resolve these separately when they are independent:

- interface, ownership, and call path
- durable data, file locations, and naming
- enforcement, errors, and recovery

Show file trees, signatures, invariants, or error cases only when they constrain
implementation or expose a choice. Treat an invariant as an open decision if
the design cannot enforce or probe it.

Do not plan slices. Stop for approval.

### Slice gate

Propose ordered vertical slices. Each slice must deliver one observable behavior
or test one risky assumption with the smallest end-to-end probe. Split
independently rejectable behavior. Defer generalization, variants,
documentation, migration, cleanup, and hardening unless required by the slice.

For each slice, state:

- behavior or assumption
- automated test, manual probe, and stop condition
- expected files
- exclusions and deferred behavior
- review budget

Prefer 100-200 lines for uncertain work, and less when a smaller probe suffices.
Larger budgets require explicit approval. Stop for approval of the slice plan.

## Execution gate

Restate the approved slice using the five fields above, then:

1. Implement only its smallest end-to-end path.
2. Stop and return to the relevant gate if a contract, file, or budget must
   change.
3. Run the agreed test and probe, or state why a probe cannot run.
4. Check the final diff for changes outside the approved scope.
5. Report the result and stop for review.

Do not begin another slice without approval.

## Review report

Use `jp-coding-preferences-reporting`. Report scope, reading order, unchanged
behavior, validation, the weakest point, the requested decision, and follow-ups.
