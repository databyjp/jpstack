---
name: gated-development
description: >-
  Use for non-trivial codebase changes where misunderstanding or a large diff
  would make review or rework expensive. Agree on the outcome, then use
  supervised checkpoints or an opt-in bounded execution envelope. Do not use
  when code is only a means to produce a non-code artifact.
---

# Evidence-first gated development

The human approves the Product outcome before implementation. `Supervised` mode
requires approval for one executable checkpoint at a time. Opt-in `Bounded` mode
allows several independently testable checkpoints within one approved execution
envelope. Both modes preserve Product boundaries, ask-first decisions, and
evidence-mapped completion. Prefer working evidence over speculative design.

## Choose a lane

- **Small:** obvious, low-risk, and easy to review. Implement directly.
- **Gated:** everything else. Follow this skill.

State the recommended lane. When uncertain, use Gated.

## Choose a supervision mode

Use `Supervised` by default. Recommend `Bounded` only when the Product contract
is stable, the work needs several checkpoints, the allowed scope and validation
surfaces are concrete, and unresolved ask-first decisions are unlikely. Keep
short, exploratory, ambiguous, or externally risky work in `Supervised`.

The human chooses the mode. A Bounded approval packet contains:

- the complete Product contract;
- the planned checkpoint sequence and allowed files, components, or operations;
- permitted local and external actions;
- the validation plan and required evidence;
- Product, interface, schema, security, privacy, credential, spending,
  destructive-action, and external-effect conditions that require interruption;
- checkpoint, retry, cost, duration, and no-progress budgets that apply;
- the conditions for completion, interruption, or failure.

State exact providers, targets, regions, cost caps, cleanup duties, and retained
evidence for any authorized external action. Permission for one target or action
does not imply permission for another.

A Bounded approval applies only to its Product task and the active Pi run. Do not
carry it into a new outcome, session, fork, or restart, and do not reconstruct it
when the approved packet is unavailable. Bounded mode adds no persistence or
automatic settle-loop continuation.

## Development loop

1. Establish the Product contract and supervision mode.
2. Identify the riskiest current assumption or next observable behavior.
3. Define one executable checkpoint and apply the split test.
4. In `Supervised`, get explicit approval for its contract and review target. In
   `Bounded`, confirm that it fits the approved packet.
5. Implement, validate, and map the evidence to the Product contract.
6. In `Supervised`, stop. In `Bounded`, continue only under the bounded-execution
   rules below.

If implementation exposes a choice not already settled by the approved contract
or Bounded packet, ask first when it affects user-visible behavior, a persisted
schema or public interface, introduces a significant dependency or architectural
seam, affects security, privacy, credentials, destructive action, external
effects, or meaningful cost, would materially constrain later retained work or
make rejecting the choice require substantial rework, or affects most of the
proposed change.

Otherwise make and record an assumption that is cheap to reject at the next
review: it creates no unauthorized external effects, does not materially
constrain later work, and can be discarded without substantial rework. Git
reversibility alone does not satisfy this test.

A decision packet contains the decision, recommendation, main trade-off, and one
question. Ask the user for concrete choices without repeating settled background.
Clarification is not implementation approval.

## Product contract

Present one compact approval request containing:

- **Outcome:** the problem and user-visible result, stated as black-box behavior
  that a user can verify without knowing the implementation
- **Non-goals:** adjacent behavior that this task will not deliver
- **Must-have behaviors:** the complete set of approved behavior that requires
  evidence before claiming the Product outcome is complete
- **Exit predicate:** the checkable condition that establishes the outcome
- **Validation surface:** the intended user-facing entrypoint or closest
  executable surface that can establish the exit predicate

Keep workflow and technical design out unless the user made them Product
constraints. Distinguish must-have behavior from suggestions and optional
follow-ups. In `Supervised`, stop for one explicit Product-contract approval
before designing or requesting approval for a checkpoint. In `Bounded`, include
the Product contract in the Bounded packet; approval of that packet is also
Product-contract approval.

The Product contract defines the task boundary. Start a new task only when the
outcome or non-goals materially change. A changed checkpoint, implementation
path, or validation method remains in the same task while the outcome and
non-goals remain fixed. Revise the affected contract with approval when the
change crosses an ask-first boundary. Do not carry approval into an adjacent
Product outcome.

## Select verification evidence

For each must-have behavior, choose the cheapest existing executable check whose
observations fully support the claim. Cost includes runtime, external effects,
human judgment, and maintenance. Prefer a compiler or static check for a source
invariant, a unit test for isolated behavior, an integration or acceptance test
for interactions it actually exercises, and the built product entrypoint when
the claim depends on packaging, process I/O, persistence, or external systems.
Do not require a higher-level run merely because behavior is user-visible when a
lower-level check establishes the same observations.

Treat a check as partial evidence when it bypasses behavior named in the Product
contract. Name the uncovered behavior, such as entrypoint wiring, artifact
identity, lifecycle, side effects, or retained state. Add only the smallest check
that closes that gap. Several checks may cover different must-have behaviors;
one broad product run does not compensate for an unobserved behavior.

Use a one-off command or observation for a non-recurring operational check.
Create reusable verification support only when repeated checks depend on
operational knowledge that ordinary tests or commands do not safely capture,
such as exact instance or artifact selection, external infrastructure,
readiness, credentials, retained evidence, stale-state detection, or cleanup. Do
not create a verification skill merely to wrap an existing test suite.

Keep external actions within the Product contract's ask-first boundaries. Revise
the approved validation surface when evidence reveals a gap, but do not create a
new task unless the Product outcome or non-goals change.

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
  concerns would obscure the evidence. Do not use one when a narrow retained
  test can guard an intended dependency or Product invariant.
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

Interface documentation and comments needed to understand or safely change
retained code are part of the implementation, not deferred documentation.
Prefer clear names and types; use the `code-documentation` skill for interface
contracts, rationale, dependencies, and local constraints.

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
- **Stop when**: evidence passes, fails, scope must materially expand, or an unresolved choice crosses the ask-first boundary
- **Disposition:** retain, or discard with a concrete reason retained code would
  cost more or weaken the evidence
- **Review target:** approximate size of normally formatted maintained code;
  name generated artifacts excluded from review

The expected-file list constrains scope, not project structure. Include ordinary
configuration, dependency, source, and test files when retained code needs them.
The review target estimates cognitive load after the checkpoint passes the split
test.

For a disposable spike, prefer the smallest experiment that answers its one question. For uncertain retained work, roughly 100–200 changed lines is a useful review target, but size varies with language and scaffolding. The target is not a quota.

Do not compress formatting or choose a less suitable implementation to
meet it. A modest overrun does not require approval. Stop when growth introduces
a new responsibility, independently rejectable behavior, unexpected file
category, or materially larger review surface.

## Execution

For each checkpoint, restate or record its contract, then:

1. Implement only what the primary assertion requires.
2. Track actual files and the approximate maintained-code review surface.
3. Stop before further edits if the primary assertion, approved constraints, or
   conceptual scope must expand. Ordinary scaffolding and modest size variance
   do not require approval.
4. Run the approved validation, or state why it cannot run.
5. Map every changed file to the primary assertion. Revert unrelated changes.
6. Classify each approved constraint as passed, failed, or deferred. Confirm that
   every `Do not implement` item remains absent.
7. Map the checkpoint evidence to the must-have behaviors it supports. Name each
   must-have behavior that still lacks evidence.
8. Claim that the Product outcome is complete only when the exit predicate
   passes and every must-have behavior has current evidence from the approved
   validation surface.

In `Supervised`, report the checkpoint evidence and stop. You may identify the
likely next checkpoint from evidence already gathered, but do not investigate,
design, or implement it before review.

In `Bounded`, continue without another approval only when the next checkpoint is
listed in the packet or is a narrower repair or revalidation of a listed
checkpoint, all actions remain within the approved scope and permissions, no
ask-first condition is unresolved, and every applicable budget remains. Before
continuing, record the completed checkpoint's contract, artifact changes,
evidence result, consumed budgets, retries, and reason for continuing. For
grouped external actions, record the result and consumed budget of each action
separately.

An artifact change already approved by the packet may make earlier evidence
stale. Require fresh validation for the changed artifact, but do not interrupt
when that validation is listed in the packet and its budgets remain.

A Bounded iteration records progress only when it changes an in-scope artifact
or produces new evidence that changes what is known. Stop after two consecutive
iterations without progress, or sooner when the approved packet has a stricter
limit. Do not offer an equivalent retry as recovery unless new evidence makes it
materially different. A failed or inconclusive check permits another attempt
only when the packet allows the repair and its retry budget remains.

Interrupt Bounded execution when:

- the Product outcome or non-goals change;
- the next useful checkpoint is outside the packet;
- an unresolved choice crosses an ask-first boundary;
- an external action lacks exact permission or would exceed its limit;
- evidence invalidates an approved safety, scope, or validation assumption;
- progress, retry, cost, duration, or checkpoint budget is exhausted; or
- the user interrupts.

When Bounded execution completes or interrupts, report all checkpoint results,
the evidence mapped to each must-have behavior, consumed budgets, the stop
reason, and any decision now required.

## Split example

Too broad: prove corpus growth, map budgeting, omitted-detail recovery, and
provenance in one checkpoint.

Focused: using the intended SDK, prove that filtered hybrid retrieval returns one
expected source-linked KI within a limit of three. Defer growth and maps. Test
their interaction later only when that interaction becomes the primary
uncertainty.

## Review report

Use `jp-coding-preferences-reporting`. In addition, compare approved and actual
files and review surface, report each primary assertion as passed, failed, or
unverified, map new evidence to the Product contract, name must-have behavior
that remains unverified, and confirm excluded behavior remains absent. For
Bounded work, also report why each continuation was permitted and which budget
stopped or completed the run. Do not claim Product completion unless the exit
predicate and every must-have behavior have current evidence from the approved
validation surface.
