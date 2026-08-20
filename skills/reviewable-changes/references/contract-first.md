# Contract-first work

Read this when a slice creates a **new seam** — a boundary that later code will depend on. New module or service, first integration with an external system, an extraction that splits one module into two, a new layer (cache, queue, adapter) where none existed.

Not for adding behaviour behind a boundary that already exists. There, the contract is already in the codebase; inventing a new one is itself the scope creep.

## Contents

- Why the seam is the artifact to review
- What to produce first
- Where to put the seam
- Is the contract its own PR?
- Prove it with one thin slice
- Label the contract provisional
- Guard against designing too much

---

## Why the seam is the artifact to review

Most of this skill is about stopping a patch from sprawling sideways into adjacent code. New-seam work inverts the failure mode: nothing constrains the change, so the *first* implementation silently becomes the architecture. Nobody chose it. It was what got written first, and every later layer is now shaped by it.

The reviewability argument is about reversal cost. An interface is cheap to review and expensive to reverse; an implementation is the opposite. A wrong signature agreed early gets paid for in every slice built on top of it. So the highest-leverage thing to put in front of a human is the signature — one level earlier than the normal loop reaches.

The same decisions embedded in 1,200 lines of working implementation are effectively unreviewable. A reviewer will check whether the code does what it says, not whether the seam was placed correctly, because the second question is too expensive to ask once the code exists.

## What to produce first

The seams, with the bodies left empty:

- type and data-shape definitions,
- public function or method signatures, with doc comments stating the behavioural contract,
- module boundaries and the direction of dependencies between them,
- error and failure cases as part of the signature, not as an afterthought,
- stub bodies that raise "not implemented".

Plus one line that is easy to skip and does the most work: **what the caller is deliberately prevented from seeing.** A seam that hides nothing is not a seam, it is a rename.

## Where to put the seam

The most common misplacement is shaping the boundary like whatever is on the far side of it — an SDK, a wire format, a database driver — instead of like what the caller needs. It is the path of least resistance, because the vendor's shape already exists and the caller's need has to be designed.

The tell shows up in tests. If the fake has to reconstruct a third-party response envelope, the seam is in the wrong place:

```python
# Seam placed at the vendor: the test rebuilds the SDK's shape
class _FakeChat:
    def __init__(self, content):
        class _Completions:
            @staticmethod
            def create(**kwargs):
                return _Response(choices=[_Choice(message=_Message(content))])
        ...

# Seam placed at the caller's need: the fake is the contract
class FakeClassifier:
    def classify(self, email: Email) -> Classification: ...
```

The first version leaks the vendor's shape into every caller and every test. The second lets the vendor change without the application noticing. Ask what the *application* needs to be true, then put the boundary there and let one adapter absorb the vendor's shape behind it.

## Is the contract its own PR?

Splitting the contract into its own PR doubles the review events, which is not always worth it. Decide deliberately:

**Its own reviewed artifact** when the seam spans more than one module, or more than one reviewer audience, or the implementation behind it is large enough that the signature would be lost in the diff.

**In the plan turn instead** when it is a single module with one reviewer. Put the signatures in the Step 1 plan, get agreement there, and ship them with the first implementation. Same discipline, one review event — the plan turn is the cheap place either way.

State which you chose and why. A reviewer who expected a stub PR should not have to work out that the contract is in the plan.

## Prove it with one thin slice

Do not implement every stub at once. Take one real path all the way through the stack — a single endpoint, one record type, one user action — and make it work end to end against the real contract. This is the walking skeleton, and it is what distinguishes a useful contract from a plausible-looking one.

Contracts designed with no implementation pressure are frequently wrong in ways that only surface on first contact: a signature that cannot express an error case, a boundary that forces a caller to reach across two modules, a data shape that needs a field the source cannot supply. One vertical slice finds these while changing them is still cheap.

Only after the slice works should the remaining stubs get filled in. Those fills are usually parallel, low-risk, and easy to review, because the pattern is already established and approved.

## Label the contract provisional

State plainly, in the PR description or the plan, that approving the contract is not freezing it:

```
This defines the seam only; all bodies are stubs. Expect changes once the
first vertical slice lands — in particular the error type on `search()` is
a guess until we see what the data layer can actually distinguish.
```

Naming the parts you are least sure about does real work. It tells the reviewer where to spend attention, and it gives you permission to revise without relitigating the approval. Without it, an approved interface becomes a thing people implement around rather than fix.

## Guard against designing too much

The risk of contract-first is over-abstraction arriving through the front door. Constrain it:

- No interface without a caller in this layer or the next one. Speculative extension points are follow-ups, not contracts.
- One implementation, not a plugin architecture, until a second implementation actually exists.
- Define the subsystem being built, not the general category it belongs to.
- If a stub cannot be described in one sentence without "and", it is probably two.

A narrow interface hiding a deep implementation is not over-abstraction — it is the goal. The smell is generality nobody asked for: unused parameters, config hooks with no caller, a strategy pattern with one strategy.
