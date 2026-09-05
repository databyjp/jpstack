# Final stamp extension

This Pi extension adds a dim, right-aligned local timestamp after each user message and final visible assistant message.

Timestamps use 24-hour `YYYY-MMM-DD HH:MM` format:

```text
2026-Sep-04 13:05
```

## Behavior

- Every user message receives a timestamp.
- An assistant message receives a timestamp when it contains non-empty text and no tool call.
- Thinking-only and tool-use turns receive no timestamp.
- Timestamp entries persist in the session but do not enter model context.
- The extension records entries only in TUI mode.

The assistant rule prevents orphaned timestamps when `pi-calm` hides thinking and tool-use turns.

## Install

Install the directory as a local Pi package:

```sh
pi install ~/code/jpstack/extensions/final-stamp
```

Run `/reload` after installation and after source changes.

The package has no settings or commands. It uses the system's local time zone.
