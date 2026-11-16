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

This profile does not install terminal extensions, Claude configuration, Nono,
Docker, credentials, provider settings, or trust decisions. Pi Pocket extensions
and PiP's separate `pip.md` are outside its scope.

## Install

Use Python 3.10+, Git, and filesystem symlinks. Install after this change is
merged into main, using a clean committed checkout and the Pi Pocket service
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
