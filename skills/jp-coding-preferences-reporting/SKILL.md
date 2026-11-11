---
name: jp-coding-preferences-reporting
description: Use when reporting finished code changes back to the user, so they can understand the result and review consequential changes in a sensible order.
---

# Reporting changes

Lead with what changed and what that means for the user. Explain the result in terms of actual behavior before introducing implementation detail. For example: "The importer now skips rows with invalid dates and reports their line numbers" tells the reader more than "Import validation has been hardened."

Prefer an opening that names the change and its reason, using first person for your own work: "I restricted retries to explicit rejections so a timeout cannot trigger an automatic resend." Then explain any new error, argument, or behavior the caller must handle. Put a release recommendation or other decision first when that is the reader's immediate task. Do not impose one opening structure on every report. Describe the specific failure path addressed; do not turn removal of one cause into a guarantee that a whole class of failures cannot occur.

Cover the relevant scope, changes, validation, risks, and remaining decisions. These are coverage checks, not headings or a requirement to fill every category. A small fix may need only a short paragraph and the check result. Keep connected reasoning in prose; use a list when the reader needs to compare independent changes or follow a review order.

- **Give a reading order when it helps review.** Order consequential changes by the question each file answers, such as "Read `session.py` first to check when the old session closes; `test_session.py` exercises that sequence." Use names from the code and explain their role. Do not substitute labels such as "the safety-critical seam" for the behavior the reviewer needs to inspect.
- **Explain intent; show mechanisms selectively.** For a public interface, schema, error handling, deletion, or other disputable choice, include a signature or 3-15 line excerpt when it helps assess that choice. Use the `show-me` diff shapes where appropriate and reference the rest as `file:line`. Do not repeat diffs the harness already rendered. Keep excerpts under roughly one screen and explain what the reader should notice.
- **Connect checks to claims.** Say what was run, what passed or failed, and what behavior that checks. Distinguish completed edits from verified outcomes. Keep local measurements, suspected causes, and predictions separate. Name untested behavior when it limits the conclusion; do not imply that one passing test validates an entire workflow.
- **Name consequential risks and decisions.** Explain the condition and consequence directly: "Retries may send an invoice twice because the provider does not accept an idempotency key." State an unresolved design choice or changed assumption when it affects review. Omit speculative risks, generic cautions, and routine implementation history.
- **Mention unchanged behavior only when it matters.** Include it when the reader might reasonably expect it to change or when it limits the result. Say what can be skipped only when that saves meaningful review effort.
- **End when the useful information ends.** Ask for a concrete decision when one remains. Otherwise, finish with the result or validation. Do not manufacture a follow-up, recap, approval request, or task for the user.

Before sending, check that the reader can tell who does what and why it matters without reconstructing your development session. Apply the always-on writing rules; use `unslop` when the report needs a fuller clarity pass.
