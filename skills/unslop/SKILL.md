---
name: unslop
description: Reviews and revises substantial human-facing prose for concision, specificity, and natural language. Use when writing prose such as long outputs, documents, or even code comments.
---

# Unslop

Revise the draft without changing its facts, intent, technical meaning, required format, or requested voice.

## Revision pass

- Start with the answer or necessary context. Delete openings such as "Of course!", "Great question!", and "You're absolutely right!"
- Cut sentences that do not help the reader act or understand. Delete "It is important to note that." Replace "In order to" with "To" and "due to the fact that" with "because."
- Replace praise and mood with facts. Rewrite "This pivotal release showcases the team's groundbreaking work" to name the release, the change, and who made it.
- Name mechanisms and measurements. Replace "SQL you can read" with "`.toSQL()` returns the exact string sent to the database." Replace "performance improved significantly" with the measured change.
- Name the source of attributed claims. Replace "Experts believe" or "Industry reports suggest" with a named source and citation. Delete the claim if no source is available.
- Replace vague participial phrases with actions or results. Rewrite clauses built around "highlighting," "ensuring," "reflecting," "showcasing," or "fostering" so they state what happened.
- Prefer plain verbs and words when they preserve meaning. Replace "serves as" with "is," "utilize" with "use," and "facilitate" with "help." Keep established technical terms when a simpler word would be less precise.
- Remove stock structures. State the point instead of writing "not just X, but Y." Do not invent a third item to make a group of three. Use "from X to Y" only when X and Y are endpoints on a meaningful scale.
- Keep terminology stable. Do not call the same person "protagonist," "main character," "central figure," and "hero" in one passage.
- Split sentences that require backtracking. Prefer "The loader parses the file. The compiler validates each query" to a sentence that buries both actions in subordinate clauses.
- Prefer active voice when the actor matters. Replace "queries are validated" with "the compiler validates queries." Keep passive voice when the actor is unknown or irrelevant.
- Remove formatting habits that do not aid navigation. Replace "**Performance:** Performance improved" with a direct sentence. "**Schema in TypeScript.** Tables live in one file." is acceptable because the second sentence adds information.
- Use sentence-case headings, straight quotes, and no decorative emojis or em dashes. Use colons for lists or examples, not in place of a sentence break.
- Delete canned endings such as "I hope this helps," "Let me know if you need anything else," and "The future looks bright." End with the result, decision, or next step.

## Final check

- Does every sentence add a fact, decision, instruction, example, or necessary context?
- Could any sentence appear unchanged in another project's documentation? If so, make it specific or delete it.
- Are claims tied to evidence or a named source?
- Did the revision preserve exact quotations, identifiers, technical terms, required formats, and the user's voice?
