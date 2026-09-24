---
name: reference-survey
description: >-
  Design a seam from comparative evidence: survey two or three real
  implementations of the same problem, then distill a decision rule from where
  they agree and disagree. Use when a seam or interface decision depends on
  territory the codebase has not built before, or when the user asks how
  established systems handle a design situation.
---

# Reference survey

When a seam decision depends on territory the codebase has never built, don't design it in a vacuum and don't copy a single prior art. Survey two or three real implementations of the same problem and distill the comparison into one decision rule.

Before carrying out searches, ask the user for permission, and if they know of particular implementations to survey, or candidates.

This complements `codebase-design`'s design-it-twice pattern: that pattern generates alternatives for your own interface; a survey supplies external evidence for what actually varies across the seam.

## Method

**Pick implementations, not narratives.** Two or three systems known to solve the same problem: an installed dependency, a source clone on disk, or a well-documented repository. Prefer source over documentation. Seams show in import graphs, process boundaries, and what each module refuses to know, not in READMEs.

**Answer the same three questions for each implementation:**

1. Where is the seam, and what is the complete contract across it?
2. What does the framework standardize, and what does each caller author?
3. Where does the framework end: process boundary, subprocess, plugin, generated code?

**Classify, then distill.** Agreements are table stakes. The signal is deliberate disagreement: each differing stance is a trade-off someone paid for. Reduce the differences to the one dimension that matters, and phrase it as a decision rule in one sentence, for example: "standardize the context, not the checks." Do not adopt one implementation wholesale; the rule explains why the chosen stance fits this codebase.

**Keep it local.** Never import another system's vocabulary into the project's glossary. Translate findings into `codebase-design` terms (seam, interface, adapter) and the project's domain language.

## Output

State the decision rule first, then the evidence per implementation as file paths, not impressions. Name the trade-off the chosen stance accepts. If the choice is load-bearing and hard to reverse, offer an ADR via `domain-modeling` so future surveys don't re-litigate it.
