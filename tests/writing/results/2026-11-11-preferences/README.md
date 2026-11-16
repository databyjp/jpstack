# Preference-guided writing evaluation, 2026-11-11

Selected the **compact** candidate after six human A/B preferences and 21 fresh subagent samples. The instructions favor connected causal reasoning, established technical terms, brief useful prior-behavior context, lists for distinct steps, and proportionate verification reports. The candidate consolidates overlapping rules in the always-on prompt and two skills.

The baseline is PR commit `87f867e`, the selected version from [the first pilot](../2026-11-11/README.md). This is another screening pilot with one output per case and variant, not a measured general improvement rate.

## Human evidence

The [preference brief](preferences.md) records the interpretation and its limits. [run.json](run.json) preserves the six actual comparison texts and responses.

- The user slightly preferred a longer sentence that made causality explicit and slightly preferred the established term "atomic" to a longer explanation.
- They chose prior behavior before the change in one report opening, bullets for one short process, and a positive scoped test report without an appended untested-workflow disclaimer. No reasons were supplied for these three choices; the interpretation remains local.
- They preferred including code with shorter prose and found the note announcing a schematic excerpt unnecessary. The supplied sketch was not valid standalone Python; this choice does not authorize invented or incorrect source.
- No full-output annotation has been supplied. The complete CSV report remains available for further human feedback.

These preferences do not require a history-first opening, lists, code, or omitted limitations in every response. The selected instructions still preserve the intended audience, actual behavior, uncertainty, and material evidence requirements.

## Variations and method

- **Current:** the exact instruction text in the existing PR.
- **Targeted:** local changes to that text around the six preferences.
- **Compact:** a shorter consolidation of task-report, writing-style, and skill rules around the same preferences. Development workflow and editing discipline remain intact.

Both candidates were frozen before the editor read the new prompts. A separate agent authored six cases without inspecting the repository, instructions, feedback, or previous outputs. They cover a file-watch incident, concurrent reservations, an image-preview fix, an audio workflow, a small breadcrumb fix, and Windows release readiness. A reused JSON/technical-meaning case checks preservation.

Each of the 21 generations used a fresh context, one assigned instruction set, and one prompt. The generators could read their task input and save a response; they could not explore the repository or execute the fictional tasks. Responses are retained verbatim. Two fresh reviewers saw randomized A/B/C labels, the user's exact feedback, and factual expectations, without knowing the instruction versions. Ties were allowed. All agents used the inherited default model; exact model and generation settings were not exposed. Shared host instructions remained active.

## Judgments

Cells show **candidate wins / ties / current-PR wins**, derived from each reviewer's three-way ranking. These describe the saved outputs only; both reviewers assessed the same samples.

| Comparison | Reviewer A | Reviewer B |
| --- | --- | --- |
| Targeted vs current PR | 3 / 3 / 1 | 3 / 2 / 2 |
| Compact vs current PR | 5 / 2 / 0 | 5 / 1 / 1 |

Both reviewers preferred the compact output for the incident explanation, preview-width fix, breadcrumb update, and Windows release decision. They disagreed on the concurrency explanation: one preferred compact, while the other preferred the current PR. For the audio workflow, one tied compact with current and the other preferred compact; both preferred the targeted variant's leaner list. All three preservation outputs tied.

The targeted candidate retained the routine full-suite/browser disclaimer in the breadcrumb update despite the added guidance. Compact omitted it while naming the exact component test command and coverage. All variants retained the missing installed Windows workflow when deciding release readiness. This distinction supports a policy of scoped positive verification without hiding decision-relevant evidence gaps.

Neither reviewer found a substantive fidelity failure in the selected candidate. One reviewer marked the targeted preview explanation's use of "missing" instead of "falsy" as a minor precision issue; the other treated it as style. Their original annotations are retained.

## Remaining questions

- None of the variants included a code block in the cases where source was already supplied. Inline references sometimes conveyed the mechanism adequately. These results do not establish the user's desired code/prose balance for a standalone artifact whose reader has not seen the source.
- Compact's audio walkthrough repeats the controller in several labels and repeats the playable-before-waveform point. The targeted output organized that explanation more economically.
- The concurrency preference split shows that the new instructions do not uniformly outperform the current PR.
- All six new cases were used to select the candidate. A future check should use new real outputs and repeated generations, with human annotation of at least one complete output.

## Artifacts

- [Full record](run.json): original human comparisons, three frozen instruction sets and hashes, seven cases, all 21 responses, anonymous-label key, and both complete reviews.
- [Preference brief](preferences.md): concise interpretation for future editing and review.
- [Reusable evaluation procedure](../../README.md).
