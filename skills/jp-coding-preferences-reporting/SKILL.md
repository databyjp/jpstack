---
name: jp-coding-preferences-reporting
description: Use when reporting finished code changes back to the user, so they can review them in a sensible order.
---

# Reporting changes

Report Scope, Changed, Not changed, Validation, and Follow-ups. Then guide the review:

- **Give a reading order, not a file list.** Order by consequence, and name the
  question each file answers. The safety-critical seam comes before the file of
  one-line error classes.
- **Show the change, don't describe it.** For anything the reviewer must approve
  or might dispute, such as a public interface, schema, error handling, or a
  deletion, include the signature or a 3-15 line hunk inline using the `show-me`
  diff shapes, and reference the rest as `file:line`. Do not re-paste diffs the
  harness already rendered; excerpt only what needs a decision.
- **Budget the excerpts.** Keep the report's excerpted code under roughly one
  screen. Past that, trim excerpts before trimming the reading order.
- **Indicate importance.** Mark architecture-critical or safety-critical parts.
  Omit this when none exist.
- **Name any significant risks.** If there is a weak assumption, unresolved risk, or
  design choice, state it plainly. If you changed your mind during implementation,
  say so. Do not invent a weakness or risk to fill this section.
- **Say what to skip, and why.** "Every method body raises `NotImplementedError`,
  so there is no logic to check" saves more time than a summary.
- **Name the decision, when there is one.** Ask the reviewer to approve the shape,
  approve the behaviour, or choose between options. Otherwise, state what was
  validated and whether any follow-up remains.

One real weakness beats four hedges. Omit the section when there is no credible
weakness.
