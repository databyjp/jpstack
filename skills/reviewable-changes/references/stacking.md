# Stacking and slicing mechanics

Read this when work needs more than one PR, or when a large diff already exists and needs to be broken up.

## Contents

- Choosing the cut lines
- Building a stack from scratch
- `gh stack` reference
- Slicing a diff that already exists
- Handling review feedback mid-stack
- Plain-git fallback (no `gh-stack`)

---

## Choosing the cut lines

A good stack layer is a single concern that could, in principle, be described in one sentence without an "and". Useful cuts, roughly in order of how often they apply:

- **Dependency order** — data model, then API, then wiring, then UI. Each layer imports the one below.
- **Reviewer audience** — if two parts of the diff would be judged by different people, split them, even if one author wrote both.
- **Mechanical vs semantic** — a rename touching 40 files and a behaviour fix touching 3 are both easy to approve separately and hard to approve together.
- **Risk** — isolate anything touching auth, billing, persistence, or concurrency into its own layer so it gets its own scrutiny.
- **Independently shippable** — if a layer can merge and be useful (or at least harmless) alone, that is a strong signal it is a real layer.

Bad cuts to avoid: splitting purely by line count, splitting a single behaviour change across two PRs so neither is testable, or putting tests in a separate PR from the code they cover.

Set the **stack base** deliberately (usually `main`). CI checks and merge rules across the whole stack are evaluated against it.

## Building a stack from scratch

Plan the layers before writing any code. Present the plan as a table and get agreement:

| Layer | Branch | Ships | Base | Validation |
|---|---|---|---|---|
| L1 | `feat/catalog-data` | typed catalog, seed data, access module | `main` | `npm test -- catalog` |
| L2 | `feat/search-api` | validated `/api/products/search` | `feat/catalog-data` | `npm test -- api` |
| L3 | `feat/chat-grounding` | chat answers from real product data | `feat/search-api` | Playwright suite |
| L4 | `feat/grounded-ui` | citation cards, empty/error states | `feat/chat-grounding` | Playwright suite |

Then work one layer at a time: check out the layer, implement within its budget, run its validation, commit only when green, and only then add the next layer on top. Do not start layer N+1 while layer N is red — a broken base makes every PR above it unreviewable.

Confirm CI exists before submitting, since checks run for every layer.

## `gh stack` reference

GitHub's stacked pull requests have a CLI extension and a companion skill that teaches agents the workflow:

```bash
gh extension install github/gh-stack
gh skill install github/gh-stack        # or: npx skills add github/gh-stack
```

Core commands:

| Command | Does |
|---|---|
| `gh stack init` | start a stack, setting the first branch and its base |
| `gh stack add` | add the next layer on top of the current one |
| `gh stack push` | push all stack branches to remote |
| `gh stack submit` | open linked PRs on GitHub with a stack map on each |
| `gh stack rebase` | cascade a rebase locally after a lower layer changes |
| `gh stack sync` | fetch, cascade-rebase, push, and sync PR state in one go |

If `gh-stack` is unavailable in the repo or the user is not on GitHub, fall back to plain git (below) or to sequential PRs merged bottom-up.

## Slicing a diff that already exists

Do not edit while proposing the split. Produce the plan first, get agreement, then execute.

**1. Inventory the diff.**

```bash
git diff --stat main...HEAD          # or: git diff --stat  for uncommitted work
git diff main...HEAD --name-only
```

Group files by concern, not by directory. Flag anything that looks like drive-by cleanup — formatting-only changes, renames, unrelated dependency bumps — since those are usually the easiest layer to peel off first.

**2. Propose the sequence.** For each proposed patch state: goal, files touched, behaviour risk, tests to run, whether it can ship independently.

**3. Execute the split.** With uncommitted work, the cleanest route is to reset and re-stage in slices:

```bash
git stash                             # park everything
git checkout -b feat/layer-1 main
git stash pop
git restore --staged .                # unstage all
git add <files for layer 1>           # or: git add -p  for partial-file slicing
git commit -m "..."
git stash                             # park the remainder for the next layer
```

With work already committed, `git rebase -i` to reorder and split commits, or cherry-pick the relevant commits onto fresh branches in dependency order.

For a mixed file that contains both a mechanical and a semantic change, `git add -p` is the tool — stage the hunks belonging to the current layer and leave the rest.

**4. Verify each layer independently.** Every layer must build and pass its own validation on its own base. A layer that only compiles once a later layer lands is not a real layer; merge it upward and re-cut.

## Handling review feedback mid-stack

When changes are requested at the bottom of a stack:

1. Apply the fix on the layer that owns it — never patch a lower layer's problem in a higher layer.
2. Test, commit, and push that branch.
3. Cascade upward: `gh stack rebase` locally, then `gh stack push` (or `gh stack sync` for the all-in-one flow: fetch, rebase every branch above the changed one, push, sync PR state).
4. Let CI re-run across the stack before asking for re-review.

GitHub will flag a diverged stack as unmergeable until this is done.

**Prefer rebasing locally over the web "Rebase stack" button.** The web rebase runs on GitHub's servers: it resets the committer to whoever clicked it and produces unsigned commits, which quietly breaks branch protection rules that require signed commits.

## Plain-git fallback (no `gh-stack`)

Branch each layer off the previous one and open each PR with its base set to the layer below:

```bash
git checkout -b feat/layer-1 main
git checkout -b feat/layer-2 feat/layer-1
gh pr create --base main --head feat/layer-1
gh pr create --base feat/layer-1 --head feat/layer-2
```

After changing a lower layer, cascade manually from the bottom up:

```bash
git rebase --onto feat/layer-1 <old-layer-1-head> feat/layer-2
git push --force-with-lease
```

Use `--force-with-lease`, never bare `--force`, so you do not clobber someone else's push.

Add a hand-written stack map to each PR description so reviewers can navigate, and note the reading order:

```
Stack: #101 (data) ← #102 (api) ← #103 (wiring) ← **this PR** (ui)
Read top-down for context; review bottom-up.
```
