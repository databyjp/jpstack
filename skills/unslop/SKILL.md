---
name: unslop
description: Drafts and revises human-facing prose so readers can follow the actors, actions, relationships, and point. Use for substantial explanations, reports, documents, plans, or comments, and when asked to improve unclear writing.
---

# Unslop

Reduce the work the reader must do to understand the text. Preserve facts, intent, technical meaning, uncertainty, required format, and the requested voice. Clear writing may need more words. Do not turn a revision into a shorter but less informative claim.

## Revision sequence

Work through these questions in order. Rewrite the draft rather than appending a critique or exposing the editing checklist, unless the user asks for one.

### What does the reader need to learn?

Identify the intended reader and the question the text should answer. Lead a reply with the answer, finding, or result. Give a standalone document enough current-state context to make its problem and proposal understandable.

Distinguish existing behavior, proposed changes, and completed work. State a document's status once, then keep the tense consistent. Include background that explains a consequence or decision; remove the history of how the writer arrived there unless it changes the reader's judgment.

Choose the main point by the reader's task. In a change report, a direct account of what changed and why is often the clearest opening; explain relevant caller consequences nearby. Do not impose a caller-first formula or split a clear change-and-reason sentence merely to make sentences shorter. Describe a proposal with wording such as "The service would load..."; reserve imperatives for actual instructions. Do not add implementation or verification tasks to an explanation unless they serve the request.

### Who does what?

Find the person, component, or process involved and the action it performs. Usually put that actor in the grammatical subject and the action in the verb. Look for actions hidden in nouns such as "validation," "coordination," or "execution"; restore the verb when doing so clarifies the sentence.

Given that the queue dispatches jobs and retries failures:

- Before: "Retry coordination is handled through the queue's ownership of dispatch."
- After: "The queue dispatches jobs and retries failed jobs."

Do not mechanically ban nouns or passive voice. "The token expires after ten minutes" names the right subject. "The backup was deleted at 09:00; the logs do not identify who deleted it" preserves an unknown actor. Never invent an actor to make a sentence active. Use first person for your own work and imperatives for instructions.

### What exactly does this mean?

Use the names in the code or domain model. Keep established technical terms when they add precision, and explain unfamiliar ones at first use. Keep terminology stable rather than rotating synonyms for variety.

Unpack noun clusters into relationships: who calls what, which value changes, where data goes, or under what condition behavior occurs. Replace invented labels and decorative metaphors with those relationships. A familiar technical word can still be vague in an unfamiliar combination.

Given a test of a server that closes the old session before assigning the new one:

- Before: "The session ownership handoff seam now has cleanup coverage."
- After: "The test checks that the server closes the old session before assigning the new one."

Give pronouns an unmistakable referent. Replace "this fixes it" with the specific cause and effect when several things could be meant. Prefer plain words when they preserve meaning; do not replace precise terms with generic words such as "thing" or "handling."

### Can the reader follow the point on one reading?

Begin with something already introduced, then add the new information. Keep subjects close to their verbs, conditions close to the behavior they control, and causes close to their consequences. Split a sentence when qualifiers or nested clauses force the reader to backtrack. Keep a longer sentence when its relationships are easy to follow.

Given that the cache holds a client, refresh keeps that client, and only its constructor reads the timeout:

- Before: "Unless the cache, whose entries survive refresh, has been cleared, the new timeout setting, which only the constructor reads, will not take effect."
- After: "The client reads the timeout only when it is created. Refreshing the cache keeps the existing client, so changing the timeout requires creating a new client."

Put the useful claim in the main clause. Delete empty judgments such as "This gives us a robust foundation" or state the supported consequence. Do not add a conclusion that merely repeats the preceding paragraph.

### What does the evidence establish?

Preserve the scope, units, conditions, and uncertainty of each claim. Separate an observed result from a suspected cause or a prediction. Do not turn "may fix" into "fixes," local measurements into general performance claims, or one passing test into proof of the whole workflow. Do not add a cause, measurement, or guarantee to make a rewrite sound concrete.

State which path or condition a change addresses. Removing one cause of a failure does not establish that the failure is impossible. Preserve an explicit technical caution when it prevents a plausible mistake, even if a shorter positive instruction would logically imply the same constraint.

Replace praise and unsupported intensity with observations. Name the source of attributed claims. If the evidence is missing, qualify or remove the claim rather than inventing support. State established facts directly; attach uncertainty to the claim that is uncertain.

### Does the presentation help?

Use paragraphs for connected explanations, lists for parallel items or steps, and headings for navigation. Avoid making each sentence a bullet or each paragraph a labeled section. Use an example or visual when it resolves something prose alone leaves difficult; do not add one just to fill a template.

Remove filler openings, canned closings, repeated summaries, and stock contrasts such as "not just X, but Y." Do not invent a third item to complete a group. Preserve useful contrasts and lists when the subject calls for them.

Use sentence-case headings, straight quotes, and no decorative emojis or em dashes in authored prose. Preserve exact quotations and required formats. Apply these preferences after resolving meaning; punctuation and word substitutions cannot repair an unclear explanation.

## Final check

Read once without relying on the writer's working context:

- Can the reader identify the actors, actions, and relationships without translating abstract phrases?
- Is the main point easy to find, with enough context to understand why it matters?
- Are facts, proposals, interpretations, and predictions distinguishable, with their scope intact?
- Does each sentence add information, explain a relationship, or provide necessary context?
- Did the revision preserve technical meaning, useful terminology, uncertainty, required formats, and the requested voice?

For changes to these instructions, use the cases in [the writing evaluation](../../tests/writing/README.md). The approach draws on [Zonder Labs' discussion of unclear AI writing](https://zonderlabs.com/slop); the examples here are original.
