---
name: gated-development
description: >-
  Use for non-trivial codebase changes where misunderstanding or a large diff
  would make review or rework expensive. Agree on the outcome, then use small
  approved probes and production slices to develop with evidence. Do not use
  when code is only a means to produce a non-code artifact.
---

# Evidence-first gated development

The human must approve the product outcome and each implementation budget. Prefer
working evidence over speculative design; avoid waterfall type outputs.

## Choose a lane

- **Small:** obvious, low-risk, and easy to review. Implement directly.
- **Gated:** everything else. Follow the loop below.

State the recommended lane. When uncertain, use Gated.

## Development loop

1. Agree on the Product outcome.
2. Identify the riskiest current assumption or next observable behavior.
3. Choose the shortest safe path to evidence: a probe, a production slice, or a
   necessary design decision.
4. Get approval for the implementation scope and review budget.
5. Implement only to the approved working checkpoint, validate, and review the
   evidence.
6. Record durable decisions, then choose the next step.

Ask first when a choice affects user-visible behavior, an irreversible schema
or public interface, security, privacy, destructive action, meaningful cost, or
most of the proposed change. Otherwise state a reversible assumption and use a
probe.

A decision packet contains the decision, recommendation, main trade-off, and one
question. Ask the user (for example, with `ask_user_question`) for concrete
choices. Do not repeat settled background. A decision answer is clarification,
not implementation approval.

## Product outcome

Agree on the problem, user-visible outcome, and non-goals. State them as
black-box behavior that a user can verify without knowing the implementation.
Keep workflow and technical design out unless the user made them product
constraints. Stop for explicit Product approval.

## Conditional design

Use a design packet only when the next safe change depends on a contract,
interface, ownership, data location, or failure decision. Use `codebase-design`
when choosing an interface or seam.

Show file trees, signatures, invariants, or errors only when they constrain the
next change. Prefer executable sources of truth such as a compiling interface,
contract test, narrow adapter, dry run, or walking skeleton. Do not add a module
seam merely to wrap a probe. Introduce an interface only when it is under review
or the retained capability has a real caller; otherwise use a small executable
harness.

## Change types

### Probe

A probe answers one named question with the smallest executable change. It may
stop at one seam and need not span the product flow. Build only the named
capability and the minimum harness needed to observe it. Do not build downstream
parts merely to make the probe end-to-end. State whether its code will be
retained, revised, or discarded, and stop when the question is answered.

When interaction between proven parts becomes the riskiest assumption, use a
probe that integrates only those parts.

"Probe" describes the experiment, not the implementation. Do not use `Probe`,
`runProbe`, or similar lifecycle names for retained modules, interfaces, or
directories. Name retained code by the capability it provides. A disposable
probe may use a script entry point without introducing a reusable interface.

### Production slice

A production slice delivers one retained observable behavior. Split
independently rejectable behaviors. Defer generalization, variants,
documentation, migration, cleanup, and hardening unless required.

For either change type, state:

- question or observable behavior
- assumption and approved constraints
- validation and stop condition
- expected files
- working checkpoint and deferred downstream work
- review budget

Prefer 20-50 changed lines for a probe and 100-200 for uncertain production
work. Set a review-size cap for normally formatted human-authored code and name
generated exclusions. Never compress formatting to meet the cap. If readable
code exceeds it, reduce scope or get approval before continuing.

## Execution

Restate the approved change, then:

1. For a probe, implement only to its working checkpoint. For a production
   slice, implement the smallest end-to-end path to its observable behavior.
2. Track actual files and normally formatted human-authored changed lines
   against the approval.
3. If an edit reveals that a constraint, file set, or budget was exceeded, stop
   before further edits and ask whether to trim the change or expand approval.
4. Run the agreed test and probe, or state why one cannot run.
5. Reconcile every named constraint and exclusion against the final evidence as
   passed, failed, or deferred. Report the evidence and stop for review.

Do not begin another change without approval.

## Review report

Use `jp-coding-preferences-reporting`. In addition, compare approved and actual
files and review size, and classify each approved constraint as passed, failed,
or deferred.
