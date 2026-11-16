## Skills and reviews

- Read `unslop` for substantial prose, documentation, plans, and clarity revisions.
- Read `code-documentation` when writing or reviewing docstrings and implementation comments.
- Read `jp-coding-preferences-reporting` when reporting completed code changes, and use `show-me` when a diagram, code shape, or diff helps review.
- Use `grill-me` and `grilling` when the user asks to stress-test a plan or design. Do not make an interview a prerequisite for routine implementation.
- Shared skills sometimes say "call the Skill tool". In Pi Pocket, load that skill's `SKILL.md` with the available read tool. Do not invent a tool that the session does not expose.

## Visual delivery in Pi Pocket

This overrides `show-me`'s desktop `Bash(open path/to/show-me-{description}.html)` step. Do not run `open`, `xdg-open`, or another desktop opener on the Pocket server: it does not deliver the file to the user's phone.

Check which tools the session exposes, including tools available through tool discovery. Use only available tools and their current schemas:

- Prefer `artifact` when available. Write a focused, self-contained, mobile-friendly HTML file, then publish it with `artifact` using `id`, `title`, and the local file's `path`. The user can open the published copy in Pocket. A path publication is a page, not an `inline` card.
- Otherwise, if Pocket's `browser` tool is available, use its `navigate` action with `url` set to the local HTML file's absolute path. Display it in Pocket's browser, not a server desktop browser.
- If neither tool is available, or delivery fails or is blocked, put a useful Markdown diagram, fenced code-shape sketch, or focused `diff` directly in chat. A server-side filename alone is not delivery. Do not enable extensions or bypass an approval control to obtain a tool.

## Pi Pocket environment

Use the session's working directory and the service account's home directory. Check available tools before relying on them. This profile does not establish a Nono sandbox, Docker setup, desktop browser, or workstation-specific project layout.

Follow the project's own language, package manager, instructions, and existing decisions. Read relevant `CONTEXT.md` and architecture decision records before changing architecture. Use the tools and approval controls exposed by Pi Pocket, and treat blocked operations as constraints.

Skills and preferences do not grant permission to change provider credentials, project trust, extension enablement, or model selection. Use Pi Pocket's documented user controls for those choices.
