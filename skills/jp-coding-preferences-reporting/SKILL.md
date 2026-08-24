---
name: jp-coding-preferences-reporting
description: Use when reporting finished code changes back to the user, so they can review them in a sensible order.
---

# Reporting changes

Report Scope, Changed, Not changed, Validation, and Follow-ups. Then guide the review:

- **Give a reading order, not a file list.** Order by consequence, and name the
  question each file answers. The safety-critical seam comes before the file of
  one-line error classes.
- **Indicate importance.** Mark architecture-critical or safety-critical parts.
  Omit this when none exist.
- **Name the weakest part.** If there is a weak assumption, unresolved risk, or
  design choice, state it plainly. If you changed your mind during implementation,
  say so. Do not invent a weakness to fill this section.
- **Say what to skip, and why.** "Every method body raises `NotImplementedError`,
  so there is no logic to check" saves more time than a summary.
- **Name the decision, when there is one.** Ask the reviewer to approve the shape,
  approve the behaviour, or choose between options. Otherwise, state what was
  validated and whether any follow-up remains.

One real weakness beats four hedges. Omit the section when there is no credible
weakness.
