## Agentic coding setup

### Prompts

Symlink `AGENTS.md` and `APPEND_SYSTEM.md` to inside `~/.pi/agent/`

### Pi Extensions

Symlink each extension directory in `extensions` to `~/.pi/agent/extensions`

### Skills

Symlink each skill directory in `skills` to agent skills directories - e.g. `~/.pi/agent/skills`

### Sandbox

https://github.com/nolabs-ai/nono

Nono sandbox

`~/.config/nono/profiles/pi-mise.json`

```json
{
  "extends": [
    "pi"
  ],
  "meta": {
    "name": "pi-mise",
    "version": "",
    "description": "Pi sandbox with a mise-managed Node runtime",
    "author": null
  },
  "filesystem": {
    "allow": [
      "$WORKDIR",
      "$HOME/.pi",
      "$HOME/code/agents",
      "~/.pi-lens"
    ],
    "read": [
      "$HOME/.local/share/mise/installs/node",
      "~/.worktrees",
      "~/code"
    ],
}

```

`~/.zshrc`

```shell
pi() {
    nono run --profile pi-mise --allow-cwd -- pi "$@"
}
```
