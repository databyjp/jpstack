# Writing evaluation, 2026-11-11

The working instructions are now **v3**, revised after 33 fresh subagent outputs, three rounds of blind model review, and one explicit user preference. The pilot found useful changes and residual weaknesses. It does not establish a repeatable improvement across models or tasks.

## What changed

- **v1** replaced a flat editing checklist with a revision sequence, added concrete actor/action and relationship checks, and made examples, reading orders, and follow-up requests conditional. It also replaced terminology examples that could encourage abstract technical labels.
- **v2** emphasized reader consequences, distinguished proposals from instructions, and narrowed risk-reduction claims. It improved the sampled report and plan, but its mandatory caller-first opening overreached.
- **v3** removed that mandatory ordering after the user preferred a direct account of the change and its reason. It retains the proposal, evidence, and reporting improvements and allows the opening to follow the reader's task.

The baseline is repository revision `f065b8b`. The initial revision prepared in the preceding conversation is v1. Frozen text and hashes for every version are in [run.json](run.json); the current files match the v3 snapshot.

## Method

Each sample came from a fresh subagent with no conversation history. Its assigned input contained the relevant frozen instructions and one prompt, without reviewer expectations or other responses. File tools were allowed only to read the input and save one response. No described development actions were executed.

Two separate fresh reviewers per round compared randomized A/B pairs without instruction text or version keys. They assessed actors and actions, specificity, flow, fidelity, and proportion, citing the wording behind their choices. The third round also supplied the user's preference. The independent author of four harder cases had not seen the repository, instructions, or earlier outputs; v2 was frozen before the editor read those cases.

There was **one generated sample per tested case and version**. The reviewers saw the same samples and used the same default model family, so their agreement is not independent human validation. Exact model identifiers and sampling settings were not exposed by the collaboration tools. Shared host instructions remained active, and these instructions were supplied as task guidance rather than installed in Pi or Claude Code. The third-round cases were already known. Results are a pilot, with no repeated-run trend claim.

## Judgments

Each cell gives **newer-version wins / ties / older-version wins**. Counts describe the saved pairs, not an estimated improvement rate. Do not aggregate rows: cases overlap and the last round adds human calibration.

| Comparison | Reviewer A | Reviewer B |
| --- | --- | --- |
| Original vs v1: 8 initial cases | 5 / 3 / 0 | 5 / 3 / 0 |
| v1 vs v2: 4 targeted cases | 2 / 1 / 1 | 2 / 1 / 1 |
| v1 vs v2: 4 held-out cases | 2 / 1 / 1 | 2 / 1 / 1 |
| v2 vs v3: 5 known cases, human calibration | 1 / 3 / 1 | 2 / 2 / 1 |

The initial reviewers both preferred v1 in five pairs and tied three. The clearest differences were less repetition, fewer obligatory report structures, and more ordinary wording. Two identical preservation responses correctly stayed unchanged.

In the second round, both reviewers preferred v2 for the consequential report, short plan, incident diagnosis, and breaking-release report. Both preferred v1 for the trivial correction's paragraphing and the research comparison's more explicit delivery risk. They tied the preservation and cancellation comparisons.

## Human calibration changed the decision

The user preferred this opening:

> I restricted retry_invoice to explicit 429 rejections so a timeout cannot trigger an automatic resend of an invoice the provider may already have accepted.

They preferred it over an opening that began with the caller receiving `DeliveryUnknown` and then explained the reason. Earlier model judgments had favored caller-first emphasis. This local preference justified removing the blanket ordering rule; it does not establish that every report should use first person or start with implementation detail.

Both final reviewers preferred v3's sampled retry report under that calibration. The plan and preservation case tied. The release report split between a tie and a v3 preference. Both preferred v2's cancellation explanation for addressing the immediate race outcomes earlier. No new factual fidelity issue was identified in v3; one reviewer flagged a minor actor attribution in the older cancellation response. Raw annotations are preserved even when reviewers disagreed about severity.

## Remaining weaknesses

- The research comparison's v2 output said SMS idempotency "needs attention," where v1 more directly explained that the handler could not safely absorb redelivery. Compression can still remove useful specificity.
- Cancellation explanations repeated the completion rule across an opening, race explanation, component walkthrough, and ending. The final version did not resolve this consistently.
- The invoice case is now a calibration example, not evidence that v3 generalizes. Further testing should use new real outputs and several fresh generations per relevant case, including a preservation case.

The working version is a candidate for the user's actual models. The next iteration should use human preferences on real stack outputs, retaining successful explanations as examples and keeping some cases out of the prompt-editing process.

## Artifacts

- [Full record](run.json): all 12 cases, 33 verbatim responses, four instruction snapshots, blind keys, all six reviewer records, and the human preference.
- [Samples for human calibration](review-samples.md): two verbatim excerpt pairs. The user selected A in pair 1 during the conversation; pair 2 has no recorded human judgment.
- [Evaluation procedure](../../README.md): the reusable cases and subagent workflow.
