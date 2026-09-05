# Mindful session extension

This Pi extension keeps a visible session intention and private notes for mindful agent use.

```text
[2 notes] 📝 Session Intent: Finish the refactor without expanding its scope
```

## Commands

- `/intention <text>` sets the session intention. Without text, it opens an input prompt.
- `/notes-add <text>` adds a note. Without text, it opens an editor.
- `/notes-show` opens the numbered notes list.
- `/notes-edit <number>` opens that note in an editor.
- `/notes-delete <number>` asks for confirmation, then deletes that note.

Note numbers are current 1-based positions. Deleting a note renumbers the notes after it.

## Behavior

- The note count and intention remain visible above the editor.
- The extension stores its state as custom entries in Pi's session JSONL.
- The intention and notes survive `/reload` and session resume.
- State is session-global rather than branch-local.
- Custom entries do not enter model context.
- `/notes-show` uses a dim, left-aligned overlay.

## Install

Remove the earlier standalone `~/.pi/agent/extensions/mindful-session.ts` copy first. If both copies remain, Pi loads the extension twice and suffixes its duplicate commands.

From the `jpstack` repository root, create the managed extension symlink:

```sh
python3 add_symlinks.py apply
```

Alternatively, install this directory as a local Pi package:

```sh
pi install ./pi-extensions/mindful-session
```

Run `/reload` after installation and after source changes.
