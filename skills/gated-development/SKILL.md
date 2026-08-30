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
4. Get explicit approval for its contract and review target.
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

- **Capability checkpoint:** proves one uncertain mechanism using the intended
  production stack when known. Keep its behavior narrow and retain the code.
- **Disposable spike:** answers a question whose code should not enter the
  product. Use one only when throwaway work is materially cheaper or production
  concerns would obscure the evidence.
- **Integration checkpoint:** tests one uncertain interaction between named
  parts. Exercise one behaviorally trivial path; stub parts outside it.
- **Production slice:** delivers one retained observable behavior through the
  minimum path it inherently requires.

Default to retained code. When the intended language, SDK, and lasting
responsibility are known, use them unless the primary assertion concerns a
lower-level protocol. Do not choose raw HTTP, a temporary language, or a
throwaway harness merely to reduce the file or line budget.

Split independently rejectable behavior. Defer generalization, variants,
standalone documentation, migration, cleanup, and hardening unless the primary
assertion requires them.

Docstrings and comments needed to understand or safely change retained code are
part of the implementation, not deferred documentation. Prefer clear names and
types; use the `docstrings` skill for non-obvious contracts or local constraints.

Checkpoint kinds describe the change, not the implementation. Name retained
modules, interfaces, and directories by their capability, not `Probe` or another
lifecycle term. A disposable spike may use a script entry point without a
reusable interface.

## Conditional design

Use a design packet only when the next checkpoint depends on a contract,
interface, ownership, data location, or failure decision. Use `codebase-design`
when choosing an interface or seam.

Show file trees, signatures, invariants, or errors only when they constrain the
checkpoint. Prefer executable sources of truth such as a compiling interface
with a real caller, contract test, narrow adapter, dry run, or walking skeleton.
Do not add a module seam merely to wrap a checkpoint.

## Checkpoint contract

Present this compact contract for approval:

- **Kind:** capability checkpoint, disposable spike, integration checkpoint, or
  production slice
- **Primary assertion:** one falsifiable pass/fail claim
- **Implementation path:** intended language and significant dependencies;
  explain any departure from the planned production stack
- **Validation:** one primary command or observation
- **Expected files:** closed list
- **Do not implement:** named adjacent and downstream behavior
- **Stop when:** evidence passes, fails, or scope must materially expand
- **Disposition:** retain, or discard with a concrete reason retained code would
  cost more or weaken the evidence
- **Review target:** approximate size of normally formatted maintained code;
  name generated artifacts excluded from review

The expected-file list constrains scope, not project structure. Include ordinary
configuration, dependency, source, and test files when retained code needs them.
The review target estimates cognitive load after the checkpoint passes the split
test. Prefer roughly 20-50 changed lines for a disposable spike and 100-200 for
uncertain retained work, but size varies with language and scaffolding. The target is not
a quota. Do not compress formatting or choose a less suitable implementation to
meet it. A modest overrun does not require approval. Stop when growth introduces
a new responsibility, independently rejectable behavior, unexpected file
category, or materially larger review surface.

## Execution

Restate the approved contract, then:

1. Implement only what the primary assertion requires.
2. Track actual files and the approximate maintained-code review surface.
3. Stop before further edits if the primary assertion, approved constraints, or
   conceptual scope must expand. Ordinary scaffolding and modest size variance
   do not require approval.
4. Run the approved validation, or state why it cannot run.
5. Map every changed file to the primary assertion. Revert unrelated changes.
6. Classify each approved constraint as passed, failed, or deferred. Confirm that
   every `Do not implement` item remains absent.
7. Report the evidence and stop. Do not inspect, design, or implement another
   checkpoint in the same turn.

## Split example

Too broad: prove corpus growth, map budgeting, omitted-detail recovery, and
provenance in one checkpoint.

Focused: using the intended SDK, prove that filtered hybrid retrieval returns one
expected source-linked KI within a limit of three. Defer growth and maps. Test
their interaction later only when that interaction becomes the primary
uncertainty.

## Review report

Use `jp-coding-preferences-reporting`. In addition, compare approved and actual
files and review surface, report the primary assertion as passed, failed, or
unverified, and confirm excluded behavior remains absent.
