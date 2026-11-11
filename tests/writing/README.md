# Writing evaluation

Use these cases when changing `pi-agent/APPEND_SYSTEM.md`, the Language section of `pi-agent/AGENTS.md`, `skills/unslop/SKILL.md`, or `skills/jp-coding-preferences-reporting/SKILL.md`. They check whether the instructions reduce reading effort while preserving meaning. They are manual evaluation fixtures, not an automated test suite or evidence that a prompt change improves model output.

The cases address the communication problems discussed in [Zonder Labs' post](https://zonderlabs.com/slop), with additional checks for factual fidelity and overediting. All case text is original. Do not put these cases or the reviewer expectations into the instructions being evaluated.

The [2026-11-11 subagent pilot](results/2026-11-11/README.md) records an initial comparison, a second instruction revision, and a check on independently authored cases. Its raw record includes frozen instruction text, generated responses, blind labels, and reviewer judgments.

## Compare two instruction sets

1. Save the baseline and candidate instruction files, their revisions or diffs, model identifier, and generation settings. Use the same model and settings for both. Keep unrelated system instructions identical.
2. Use a fresh conversation for each case and instruction set. Load `APPEND_SYSTEM.md` and the Language section of `AGENTS.md` for every case. Load `unslop` for cases 2, 4, 5, 6, and 7; load the reporting skill for cases 3 and 8. Do not add other skills, tools, repository exploration, or extra editing turns. This isolates the writing rules; follow with normal stack sessions to check skill discovery and interaction with other instructions.
3. Send only the case's prompt, including its facts and draft where present. Hide the reviewer expectations from the generating model. Save the responses verbatim. Never replace a poor response with a hand-edited version.
4. Show the prompt and two responses to a reviewer as A and B, randomizing their order and hiding which instructions produced each. Judge each dimension below as better, tied, or worse, citing a sentence that explains the judgment. If using a model reviewer, use a separate conversation with no candidate instructions loaded. Human preference remains the deciding check.
5. Repeat with at least three independent generations per case before describing a trend. Record model, case, run, A/B mapping, judgments, and any changed facts. Report ties, regressions, and the number of runs alongside wins. These small samples guide iteration; they do not establish a general improvement rate.

Review these dimensions separately:

| Dimension | Question |
| --- | --- |
| Actors and actions | Can I tell who or what does each relevant action? |
| Specificity | Do the names, references, and relationships have a clear meaning in the supplied context? |
| Flow and emphasis | Can I find the main point and follow its explanation without rereading? |
| Fidelity | Did the response preserve the facts, conditions, technical terms, uncertainty, and requested format? |
| Proportion | Does the response include enough explanation without unnecessary headings, excerpts, recaps, or tasks for the reader? |

A factual change or unsupported claim fails fidelity even if the response reads better. Do not use word count, banned-word counts, passive-voice counts, or punctuation as a proxy for clarity. Do not require a particular reference answer or wording.

For the first iteration, run every case. On later iterations, rerun failures and relevant cases, keeping at least one preservation case (6 or 7). When a real stack output disappoints, save its prompt, necessary context, and the reader's specific difficulty as a new case. Keep some new cases out of the next prompt revision to check whether the guidance transfers beyond its examples.

## Using subagents

When the user authorizes subagent evaluation, give each generator a fresh context with only its assigned instruction version and one case prompt. Do not pass the editing conversation, variant rationale, reviewer expectations, or other responses. Allow file tools only to read the assigned input and save the response; the task's described actions are fictional and must not be executed.

Use separate fresh reviewers, randomize A/B labels for each pair, and keep the label key and instruction versions hidden. Have reviewers cite specific wording and record ties and disagreements. An independent case author can prepare harder cases while the editor revises the instructions; freeze the next version before reading those cases.

Keep generated outputs verbatim and store snapshots or hashes sufficient to identify every tested instruction version. Record shared host instructions and unavailable model/settings metadata as limitations. Same-model generation and judging can share blind spots, so retain both responses for human review. Use several independent generations to distinguish a repeatable effect from one favorable sample. Do not keep adding rules in response to every isolated preference.

## Cases

### 1. Progress update

Prompt:

```text
Write a progress update for the user. The build finished successfully. Integration
tests are still running. Their result determines whether the change is ready.
You have no test result yet and no other work to report. Do not ask a question.
```

Reviewer expectations: distinguish the completed build from the pending tests. State the dependency directly. No readiness claim, invented elapsed time, recap, or claim that nothing else depends on anything. A short update is sufficient.

### 2. Actions hidden in nouns

Prompt:

```text
Rewrite this explanation for a developer who is new to the project.

Facts: load_config reads a YAML file. It passes the parsed values to
validate_config. validate_config rejects unknown keys before the server starts.
No other behavior is established.

Draft: "Startup configuration ingestion is followed by unknown-key rejection
through the validation layer, providing a robust server-readiness foundation."
```

Reviewer expectations: name the functions and their actions, preserve their order, and explain unknown-key rejection. Remove the unsupported judgment about robustness without inventing defaults, error messages, or guarantees.

### 3. Report a consequential code change

Prompt:

```text
Report this completed change to the user. Give enough information to review it.
Do not request approval; the user already authorized the change.

Before: retry_invoice in billing.py retried all failed requests.
After: it retries only when the provider explicitly rejects a request with 429.
It no longer retries after a timeout because the provider may have accepted the
invoice before the connection timed out. The provider has no idempotency-key
support. A caller now receives DeliveryUnknown after a timeout and must check
delivery status before trying again. Existing 429 retries still use backoff.

Review locations: billing.py:80 (retry_invoice), errors.py:12 (DeliveryUnknown),
tests/test_billing.py:40 (timeout test), tests/test_billing.py:65 (429 test).
Both tests passed locally. No live provider request was made. These locations
are all the source detail available; do not invent signatures or code excerpts.
```

Reviewer expectations: lead with the changed timeout behavior and consequence for callers. Explain the retry condition and why it matters. Point review toward that behavior, preserve uncertainty about delivery, distinguish local tests from live verification, and avoid asking for an already settled decision. Do not invent a signature to satisfy the reporting skill.

### 4. Measurement and prediction

Prompt:

```text
Rewrite this performance update using only the supplied facts.

Facts: In one local run on a synthetic dataset, median query time fell from
20 ms to 16 ms after changing the index. No production measurement exists.
The team suspects cache behavior explains the change but has not tested that.

Draft: "The index unlocks a decisive query-path win. Cache alignment is the
remaining story, and production should inherit the same performance envelope."
```

Reviewer expectations: retain the median, units, dataset, and local scope. Distinguish the measurement from the cache hypothesis. Remove the unsupported production prediction. Do not generalize to all queries or label an untested cause as established.

### 5. Standalone plan and information order

Prompt:

```text
Write a short standalone plan for a maintainer who has not read this chat.

Today read_settings opens settings.json on every request. Some requests need
only a setting name, but opening and parsing still happen each time. We propose
loading settings once when the service starts. A user edit to settings.json
would then take effect after a restart. No implementation or benchmark exists.
Ask the maintainer to decide whether requiring a restart is acceptable.
```

Reviewer expectations: establish the current behavior before explaining the proposal and its trade-off. Make the restart consequence explicit and ask that concrete decision. Do not invent latency figures, watcher support, a rollout plan, or completed work. Headings are optional.

### 6. Preserve useful passive voice and uncertainty

Prompt:

```text
Revise only where needed for clarity. Keep exactly two sentences. Do not infer
who performed the deletion.

"The archive was deleted at 14:05 UTC. The audit log does not identify who
deleted it."
```

Reviewer expectations: leaving the text unchanged is acceptable. Keep the time and unknown actor. Do not claim that the service, administrator, or writer deleted it, or that a missing log proves a particular cause.

### 7. Preserve technical meaning and required format

Prompt:

```text
Revise this note for clarity for a database engineer. Return the same JSON
object shape, with no text outside it. Keep the SQLSTATE identifier and exact
quoted message unchanged.

{"note":"At SERIALIZABLE isolation, PostgreSQL may abort a transaction with SQLSTATE 40001. Retry the whole transaction, not just the last statement.","message":"could not serialize access due to concurrent update"}
```

Reviewer expectations: preserve the technical terms, qualified "may," transaction scope, JSON keys, and exact message. An unchanged response is acceptable. Do not simplify the isolation level into a vague phrase or turn the possible abort into a guaranteed one. Useful contrasts should survive.

### 8. Small change without a report template

Prompt:

```text
Report this completed documentation fix. README.md:18 said "pip instal"; it now
says "pip install". No code changed. You checked the resulting command spelling
in the diff. No commands were executed. There is no decision or follow-up.
```

Reviewer expectations: a sentence can cover the correction and check. Do not add a reading order, excerpt, headings, speculative risks, test claims, or a request for the user to verify it. Do not omit the correction's location just to shorten the response.
