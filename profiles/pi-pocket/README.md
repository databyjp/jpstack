# Pi Pocket profile

Install a small set of skills and portable preferences, then review and apply
repository updates explicitly. The active profile uses its own Git worktree, so
fetching or pulling the source checkout does not change a running agent's rules.

## Selection and shared preferences

| Skill | Purpose |
| --- | --- |
| `unslop` | Clear prose and substantial clarity revisions |
| `code-documentation` | Docstrings and implementation comments |
| `jp-coding-preferences-reporting` | Reports of completed changes |
| `show-me` | Visual explanations; a dependency of the reporting skill |
| `grill-me`, `grilling` | Explicit plan and design reviews |

[`profile.json`](profile.json) declares the allowlist, known skill dependencies,
and instruction sources. The generated global `AGENTS.md` combines:

- Writing style and editing discipline from
  [`APPEND_SYSTEM.md`](../../pi-agent/APPEND_SYSTEM.md).
- Direct development preferences and code style from
  [`AGENTS.md`](../../pi-agent/AGENTS.md).
- Pocket-specific rules from [`instructions.md`](instructions.md).

The existing policy sections remain the shared source: no second copy needs
manual reconciliation. Renaming or duplicating a selected heading stops the
update. The development workflow subsection is excluded, so Pocket does not
require unselected workflow skills.

For `show-me` HTML, the Pocket instructions replace the shared skill's desktop
`open` step. Check tool availability: publish the file by path with `artifact`,
or navigate to the local HTML file with Pocket's `browser`. If both are
unavailable, blocked, or fail, show a Markdown diagram, code shape, or diff in
chat. A server-side path alone is not delivery to a phone. The shared skill's
desktop procedure remains unchanged.

This profile does not install terminal extensions, Claude configuration, Nono,
Docker, credentials, provider settings, or trust decisions. Pi Pocket extensions
and PiP's separate `pip.md` are outside its scope.

## Install

Use Linux, Python 3.10+, Git with worktree support, and filesystem symlinks.
Install after this change is merged into main, using a clean committed checkout
and the Pi Pocket service
account. For a systemd service using `pi-pocket` with home `/var/lib/pi-pocket`:

```bash
sudo -u pi-pocket -H bash
cd "$HOME"
mkdir -p code/agents
git clone https://github.com/databyjp/jpstack.git code/agents/jpstack
cd code/agents/jpstack
python3 sync_pi_pocket.py install
python3 sync_pi_pocket.py status
```

If the checkout already exists, use it instead of cloning over it. The optional
`--home` goes before the subcommand and can target an isolated test home:

```bash
python3 sync_pi_pocket.py --home /tmp/pocket-profile-test install
```

The installer refuses unmanaged `AGENTS.md` files, conflicting selected skill
names, and redirected parent directories such as a whole-directory
`~/.agents/skills` symlink. Preserve or migrate those deliberately first.
Unrelated skill entries are left in place.

```text
~/.agents/skills/<name> -> .../current/source/skills/<name>
~/.pi/agent/AGENTS.md   -> .../current/AGENTS.md
~/.local/share/jpstack/pi-pocket/
  current             -> revisions/<active-commit>/
  previous            -> revisions/<previous-commit>/
  revisions/<commit>/
    source/           # detached worktree of the complete repository
    AGENTS.md         # generated instructions
    profile-state.json
```

The complete worktree preserves references outside individual skills; only
allowlisted skills are exposed. Keep the source checkout and managed revisions
because Git uses both. Edit tracked sources rather than generated files or
active worktrees. The updater refuses local edits instead of discarding them.

## Recovery after failed staging

Fix the original failure (for example, disk space or a transient Git error), then
retry the same `install` or `update --apply FULL_COMMIT_HASH` command. Staging
failures do not switch the active instructions or skill links. An update may
already have fast-forwarded the source checkout; the active profile stays on its
separate worktree until staging and activation succeed.

A revision is complete only after `profile-state.json` has all completion fields.
The installer writes and flushes that record to a unique temporary file, then
atomically renames it into place. Existing completed revisions still undergo
ownership, instruction-hash, worktree revision, and local-edit checks; the
installer does not treat those check failures as an unfinished installation.

On retry, a revision with missing, truncated, or unfinished metadata is renamed
to `revisions/<commit>.incomplete-<unique-id>/`, and a fresh revision is staged.
The command prints the retained path. It preserves all files, including partial
instructions, temporary metadata, untracked files, and local worktree edits.
Redirected paths and conflicting unmanaged configuration remain errors.

Before renaming, the installer finds the stage's Git registration by its
administrative `gitdir` back-pointer, not by trusting a possibly stale `.git`
file. It restores missing or partial `.git` files even when `worktree add`
registered the worktree before creating `source`. After renaming, it updates only
the verified registration's back-pointer. It accepts the old path only while
that path is absent, so an interrupted rename can be recovered on the next retry.
A `.worktree-registration.json` receipt and a `jpstack-owner` marker in the Git
administrative directory identify that allocation, not just its reusable name.
A retained `.git` file cannot reclaim an administrative directory that Git has
reused for another worktree, even at the same old path. No broad
`git worktree repair` command runs.

Every changed registration file gets a flushed, `fsync`-checked backup in the
retained directory before atomic replacement: `.worktree-gitfile-<unique-id>`
for `.git`, `.worktree-backlink-<unique-id>` for an administrative back-pointer,
or `.worktree-receipt-*` / `.worktree-identity-*` for ownership records. The
installer also syncs the backup and replacement directories where supported.
Filesystems that reject directory `fsync` with `EINVAL`, `ENOTSUP`, or `EBADF`
produce a warning; atomic replacement still works, but power-loss durability is
not guaranteed. Other I/O errors remain fatal. Unchanged pointer files are not
rewritten. Interrupted writes can leave `.jpstack-*.tmp` files beside pointers;
these are retained too.

If an older retained worktree has lost or damaged Git administrative data, the
command warns and leaves its files intact instead of blocking unrelated staging
or reuse of a completed revision. A stale `.git` file could otherwise access
another worktree's index if Git reused its admin name. The installer preserves
that file in `.worktree-gitfile-*` and replaces it with an invalid Gitfile that
makes Git commands fail rather than touch another repository or search a parent.
Do not remove that safety file or run Git commands in a warned directory.
If saving or replacing the unsafe Gitfile fails (for example, with a full disk),
the command stops rather than silently leaving Git access to another index.
The active profile stays unchanged. Fix the I/O error and retry the same command.

The retained content remains available as ordinary files. Copy wanted edits into
tracked sources, or restore the original administrative data and ownership
marker from backup. A subsequent retry can verify the receipt and restore Git
access. A warning does not mean the registration is usable. If a stale
registration still occupies the new stage's path, Git refuses the add rather
than overwriting that registration.

Retained directories are not active or rollback targets, and are never deleted
automatically. Inspect them and preserve wanted data before any deliberate
cleanup. Keep a usable retained worktree registered with Git while you use it;
do not simply move or delete its directory.

If an interrupted process leaves `.sync-lock`, first confirm that no sync is
running, then remove only that empty lock directory and retry.

## Review and update

Between agent sessions, from the source checkout:

```bash
python3 sync_pi_pocket.py update
```

This fetches `origin`, validates the candidate, and shows changes to the profile,
shared policy, selected skills, and supporting references. It does not activate
them. Review the diff and full commit hash, then apply that exact revision:

```bash
python3 sync_pi_pocket.py update --apply FULL_COMMIT_HASH
```

Apply uses the already-fetched commit, even if newer commits exist. It verifies a
forward update in the fetched `origin/main` history, fast-forwards the source
checkout when possible, stages a worktree, and switches the active pointer. A
diverged checkout or modified managed files must be resolved first. Skill links
removed from the allowlist are removed only when this installer owns them.

Pi Pocket rereads skills and global `AGENTS.md` within about 30 seconds on a
subsequent request; no restart is needed. Apply between sessions because active
work can receive the new instructions on its next request.
[Pi Pocket customisation](https://tannermidd.github.io/pi-pocket/docs/customizing/)
describes this loading behavior.

The manifest validates declared dependencies. Review changed procedures for new
tool requirements and skill references too; file validation cannot establish
their semantics. There is no background update schedule.

## Roll back

```bash
python3 sync_pi_pocket.py rollback
python3 sync_pi_pocket.py status
```

Rollback restores the previous instructions and skill selection without fetching;
running it again switches back. Revisions are retained. Modified worktrees or
generated instructions must be preserved first. If an interrupted process leaves
`.sync-lock` in the state directory, confirm no sync is running before removing
that empty lock directory and retrying.

## Maintain the profile

Commit selection or policy changes to their tracked sources and use the same
review/apply workflow after they reach main. For local development, `install`
explicitly activates the current clean committed revision. Uncommitted files are
never included.

Run the Python checks with:

```bash
python3 -m unittest discover -s tests -v
```
