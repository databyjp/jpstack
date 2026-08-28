---
name: gated-development
description: >-
  Use for non-trivial codebase changes where misunderstanding or a large diff
  would make review or rework expensive. Agree on the outcome, then implement
  one approved executable checkpoint at a time. Do not use when code is only a
  means to produce a non-code artifact.
---

# Evidence-first gated development

The human approves the Product outcome and one executable checkpoint at a time.
A checkpoint gathers evidence toward the outcome; it need not prove the whole
outcome. Prefer working evidence over speculative design.

## Choose a lane

- **Small:** obvious, low-risk, and easy to review. Implement directly.
- **Gated:** everything else. Follow this skill.

State the recommended lane. When uncertain, use Gated.

## Development loop

1. Agree on the Product outcome.
2. Identify the riskiest current assumption or next observable behavior.
3. Define one executable checkpoint and apply the split test.
4. Get explicit approval for its contract and review budget.
5. Implement, validate, report the evidence, and stop.
6. Record durable decisions, then propose the next checkpoint.

Ask first when a choice affects user-visible behavior, an irreversible schema or
public interface, security, privacy, destructive action, meaningful cost, or
most of the proposed change. Otherwise state a reversible assumption.

A decision packet contains the decision, recommendation, main trade-off, and one
question. Ask the user for concrete choices without repeating settled background.
Clarification is not implementation approval.

## Product outcome

Agree on the problem, user-visible outcome, and non-goals. State them as
black-box behavior that a user can verify without knowing the implementation.
Keep workflow and technical design out unless the user made them product
constraints. Stop for explicit Product approval.

## One-checkpoint rule

A checkpoint has one primary executable assertion. It may contribute only part
of the evidence needed for the Product outcome.

Apply this split test before seeking approval:

> Could two claimed results fail independently while either result would still
> provide useful evidence?

If yes, split them and propose only the riskier or prerequisite checkpoint. If a
component can be removed while the primary assertion remains testable, remove it.
Cross seams only when the assertion requires their interaction. Include an
unproven supporting capability only when it is the minimum prerequisite needed
to observe the assertion.

## Checkpoint kinds

- **Capability probe:** tests one uncertain mechanism, dependency, compatibility
  claim, or performance property. It may stop at one seam and use a disposable
  executable harness.
- **Integration probe:** tests one uncertain interaction between named parts.
  Exercise one behaviorally trivial path; stub parts outside that interaction.
- **Production slice:** delivers one retained observable behavior through the
  minimum path it inherently requires.

Split independently rejectable behavior. Defer generalization, variants,
documentation, migration, cleanup, and hardening unless the primary assertion
requires them.

"Probe" describes the experiment, not the implementation. Do not use `Probe`,
`runProbe`, or similar lifecycle names for retained modules, interfaces, or
directories. Name retained code by its capability. A disposable probe may use a
script entry point without introducing a reusable interface.

## Conditional design

Use a design packet only when the next checkpoint depends on a contract,
interface, ownership, data location, or failure decision. Use `codebase-design`
when choosing an interface or seam.

Show file trees, signatures, invariants, or errors only when they constrain the
checkpoint. Prefer executable sources of truth such as a compiling interface
with a real caller, contract test, narrow adapter, dry run, or walking skeleton.
Do not add a module seam merely to wrap a probe.

## Checkpoint contract

Present this compact contract for approval:

- **Kind:** capability probe, integration probe, or production slice
- **Primary assertion:** one falsifiable pass/fail claim
- **Validation:** one primary command or observation
- **Expected files:** closed list
- **Do not implement:** named adjacent and downstream behavior
- **Stop when:** evidence passes, fails, or the budget expires
- **Disposition:** discard, rewrite for production, or retain
- **Review budget:** cap for normally formatted human-authored code; name
  generated exclusions

The review budget limits size after the checkpoint passes the split test. Prefer
20-50 changed lines for a probe and 100-200 for uncertain production work, but
use less when possible. Never compress formatting to meet the cap. If readable
code or the expected file set exceeds approval, reduce scope or ask to expand it
before continuing.

## Execution

Restate the approved contract, then:

1. Implement only what the primary assertion requires.
2. Track actual files and normally formatted human-authored changed lines.
3. Stop before further edits if a constraint, file set, assertion, or budget must
   change. Ask whether to trim the checkpoint or expand approval.
4. Run the approved validation, or state why it cannot run.
5. Map every changed file to the primary assertion. Revert unrelated changes.
6. Classify each approved constraint as passed, failed, or deferred. Confirm that
   every `Do not implement` item remains absent.
7. Report the evidence and stop. Do not inspect, design, or implement another
   checkpoint in the same turn.

## Split example

Too broad: prove corpus growth, map budgeting, omitted-detail recovery, and
provenance in one probe.

Focused: prove that filtered hybrid retrieval returns one expected source-linked
KI within a limit of three. Defer growth and maps. Test their interaction later
only when that interaction becomes the primary uncertainty.

## Review report

Use `jp-coding-preferences-reporting`. In addition, compare approved and actual
files and review size, report the primary assertion as passed, failed, or
unverified, and confirm excluded behavior remains absent.
