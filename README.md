# Agentic coding setup

## Add symlinks

Run from the repository root:

```shell
python3 add_symlinks.py apply
```

The script manages these symlinks:

- `pi-agent/AGENTS.md` to `~/.pi/agent/AGENTS.md`
- `pi-agent/APPEND_SYSTEM.md` to `~/.pi/agent/APPEND_SYSTEM.md`
- Each directory in `pi-extensions/` to `~/.pi/agent/extensions/`
- `skills/` to `~/.agents/skills`

It leaves `~/.pi/agent/settings.json` unchanged. It replaces stale symlinks but refuses to replace regular files or directories.

## Sandbox

Install [Nono](https://github.com/nolabs-ai/nono), then install or update the tracked profile through Nono's draft workflow:

```shell
mkdir -p ~/.config/nono/profile-drafts
cp nono/pi-mise.json ~/.config/nono/profile-drafts/pi-mise.json
nono profile validate --draft pi-mise
nono profile promote pi-mise
```

Add the Pi wrapper to `~/.zshrc`:

```shell
pi() {
    nono run --profile pi-mise --allow-cwd -- pi "$@"
}
```
