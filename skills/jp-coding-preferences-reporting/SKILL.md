---
name: jp-coding-preferences-reporting
description: Use when reporting finished code changes back to the user, so they can review them in a sensible order.
---

# Reporting changes

Write the scope report, then these.

- **Give a reading order, not a file list.** Order by consequence, and name the
  question each file answers. The safety-critical seam comes before the file of
  one-line error classes.
- **Indicate importance.** Indicate which parts are critical to the architecture
- **Say where to push.** Name the part you would defend weakest, before it gets
  found. If you changed your mind mid-implementation, say that too.
- **Say what to skip, and why.** "Every body raises `NotImplementedError`, so
  there is no logic to check" saves more time than any summary.
- **Name the decision being asked for.** Approve the shape, approve the
  behaviour, or choose between two options.

Never pad "where to push" to look thorough. One real weakness beats four
hedges.
