---
name: unslop
description: Runs a deliberate revision pass over substantial human-facing prose for concision, specificity, and natural language. Use when writing prose such as long outputs, documents, or even code comments.
---

# Unslop

Run a revision pass over the draft. The rule list is the "Writing style"
section of the global instructions (`pi-agent/APPEND_SYSTEM.md` in jpstack);
this skill is the procedure for applying it deliberately rather than a second
copy of the rules.

## Revision pass

1. Reread the draft as its intended reader, without your working context.
   Expand, ground, or cut any term the reader has not been given.
2. Apply the writing style rules sentence by sentence. Rewrite violations
   rather than flagging them.
3. Do not change facts, intent, technical meaning, required formats, exact
   quotations, identifiers, or the requested voice.

## Final check

- Does every sentence add a fact, decision, instruction, example, or necessary context?
- Could any sentence appear unchanged in another project's documentation? If so, make it specific or delete it.
- Are claims tied to evidence or a named source?
- Did the revision preserve exact quotations, identifiers, technical terms, required formats, and the user's voice?
