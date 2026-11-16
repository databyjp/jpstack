---
name: jp-coding-preferences-reporting
description: Use when reporting finished code changes so the user can understand and review the result.
---

# Reporting changes

Give brief previous-behavior context when the reader needs it, then state what changed and why. Skip context already established. Use first person for your work, precise technical terms, and explicit causal links. Put a release recommendation or direct answer first when that is the reader's immediate task.

- Show a useful source excerpt, signature, or diff when it helps review. Use `show-me` shapes where appropriate. Let code carry the mechanism and keep the prose to intent, consequences, and reasoning it does not convey. Do not repeat a visible diff, explain every line, label an obvious excerpt, or invent source. Keep excerpts within roughly one screen.
- Use bullets for distinct changes, steps, responsibilities, or review locations. Give a reading order for consequential changes, tying each location to what the reader should inspect. A simple fix does not need a file inventory or mandatory headings.
- State the actual checks and results precisely. Avoid a routine list of everything untested. Include an evidence gap when it changes a requested readiness decision, and never imply a broader result than the check supports. Separate suspected causes and predictions from observations.
- Name risks as conditions and consequences. Preserve meaningful compatibility changes and technical cautions. Do not add speculative risks or routine implementation history. Mention unchanged behavior only when it affects understanding or review.
- Finish with a concrete decision when one remains. Otherwise stop after the useful result and check information; do not manufacture a recap or task for the user.

Apply the always-on writing rules and use `unslop` for a fuller clarity pass. These are coverage checks, not a report template.
