---
name: gated-development
description: >-
  Use for non-trivial codebase changes where misunderstanding or a large diff
  would make review or rework expensive. Agree on the outcome, then use small
  approved probes and production slices to develop with evidence. Do not use
  when code is only a means to produce a non-code artifact.
---

# Evidence-first gated development

The human approves the product outcome and each implementation budget. Prefer
working evidence over speculative design.

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
5. Implement, validate, and review the evidence.
6. Record durable decisions, then choose the next step.

Ask first when a choice affects user-visible behavior, an irreversible schema
or public interface, security, privacy, destructive action, meaningful cost, or
most of the proposed change. Otherwise state a reversible assumption and use a
probe.

A decision packet contains the decision, recommendation, main trade-off, and one
question. Use `ask_user_question` for concrete choices. Do not repeat settled
background. A decision answer is clarification, not implementation approval.

When presenting a final decision record, mention once that Plannotator users can
run `/plannotator-last`. Its feedback is clarification, not approval.

## Product outcome

Agree on the problem, user-visible outcome, and non-goals. Write the outcome as
black-box behavior: could the user verify each statement without knowing which
modules, repositories, files, or agents implement it? If not, defer it to a
design packet.

Product outcomes describe what the user does, receives, or retains, not workflow
steps. Technical details belong here only when the user made one a product
constraint. Stop for explicit Product approval.

## Conditional design

Use a design packet only when the next safe change depends on it:

- **System:** contracts, data flow, dependencies, external systems, or failures.
- **Program:** interface and ownership, durable data and locations, or
  enforcement and recovery. Use `codebase-design` for an interface or seam.

Show file trees, signatures, invariants, or errors only when they constrain the
next change. Prefer executable sources of truth such as a compiling interface,
contract test, narrow adapter, dry run, or walking skeleton.

## Change types

### Probe

A probe answers one named question with the smallest reversible end-to-end
change. It may be hard-coded or incomplete, but must state whether its code will
be retained, revised, or discarded. Stop when the question is answered.

### Production slice

A production slice delivers one retained observable behavior. Split
independently rejectable behaviors. Defer generalization, variants,
documentation, migration, cleanup, and hardening unless required.

For either change type, state:

- question or observable behavior
- assumption and approved constraints
- automated test, manual probe, and stop condition
- expected files
- exclusions and deferred work
- review budget

Prefer 20-50 changed lines for a probe and 100-200 for uncertain production
work, but use less whenever possible. Larger budgets require explicit approval.

## Execution

Restate the approved change, then:

1. Implement only its smallest end-to-end path.
2. Stop for a new decision if an approved constraint, file set, or budget must
   change.
3. Run the agreed test and probe, or state why one cannot run.
4. Check the final diff for changes outside the approved scope.
5. Report the evidence and stop for review.

Do not begin another change without approval.

## Example

For a graphics workflow:

- **Product:** One request from `video-producer` returns a reviewable graphic
  owned by the selected video project.
- **Not Product:** The producer creates a canonical brief and delegates it to a
  designer without copying it between repositories.

After Product approval, state the design assumption: the agent harness can
discover the project designer and start it in the designer repository. Propose a plan-only probe that
adds the minimum agent profile. Stop when it reads the designer instructions and
returns without writing files. Retain the profile if the probe succeeds;
otherwise revise or discard it. Defer rendering, output paths, variants, and
documentation until delegation works.

## Review report

Use `jp-coding-preferences-reporting`. Report scope, reading order, unchanged
behavior, validation, the weakest point, the requested decision, and follow-ups.
