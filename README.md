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

## Instruction file placement

Pi assembles its system prompt in this order: core prompt, then `APPEND_SYSTEM.md` (the `addendum` section), then every discovered AGENTS.md (`project_context`), then skills, then cwd. Both files sit inside the system prompt; they differ in merge behavior:

- AGENTS.md files are cumulative. The global `~/.pi/agent/AGENTS.md` loads first, then each ancestor of cwd.
- Pi uses exactly one APPEND_SYSTEM.md. A trusted project's `.pi/APPEND_SYSTEM.md` replaces the global file, so rules that must hold in every project belong in AGENTS.md or in tooling (hooks, permission rules), not here.

Split content accordingly: APPEND_SYSTEM.md holds always-on behavioral policy (task report format, writing style, editing discipline); AGENTS.md holds task-gated working knowledge (skill triggers, workflow, documentation and code style guidelines).

## Claude Code

`~/.claude/CLAUDE.md` imports both files:

```
@~/code/agents/jpstack/pi-agent/AGENTS.md
@~/code/agents/jpstack/pi-agent/APPEND_SYSTEM.md
```

Claude Code delivers CLAUDE.md content as a user message after the system prompt, not inside it ([memory docs](https://code.claude.com/docs/en/memory)). For true system-prompt placement of the APPEND_SYSTEM.md rules, wrap `claude` in `~/.zshrc` and remove that import from `~/.claude/CLAUDE.md` so the file does not load twice:

```shell
claude() {
    command claude --append-system-prompt-file \
        ~/code/agents/jpstack/pi-agent/APPEND_SYSTEM.md "$@"
}
```

Claude Code loads skills from `~/.claude/skills/`, which holds copies, not symlinks to `skills/` here. After changing a skill in this repository, copy it there.

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
    nono run --profile pi-mise --allow-cwd -- "$PI_BIN" "$@"
}

yolopi() {
    "$PI_BIN" "$@"
}
```

To enable agents to use Docker, install Colima, and then set up its own profile; separate to my own .docker

1. Create the Docker client directory

Run outside the sandbox:

```bash
CLIENT="$HOME/.local/share/nono-docker-client"

mkdir -p "$CLIENT/cli-plugins" "$CLIENT/buildx"
printf '{}\n' > "$CLIENT/config.json"

ln -sfn \
/Applications/Docker.app/Contents/Resources/cli-plugins/docker-buildx \
"$CLIENT/cli-plugins/docker-buildx"

ln -sfn \
/Applications/Docker.app/Contents/Resources/cli-plugins/docker-compose \
"$CLIENT/cli-plugins/docker-compose"
 ```

This supplies Buildx and Compose without exposing ~/.docker or its
registry credentials.

Verify:

```bash
DOCKER_CONFIG="$CLIENT" docker buildx version
DOCKER_CONFIG="$CLIENT" docker compose version
```

### Colima setup

To start Colima for the sandbox:

```shell
colima start agents
```

Stop it with `colima stop agents`.

The VM's mounts are set in `~/.colima/agents/colima.yaml`.

```yaml
mounts:
  - location: ~/code
    writable: true
  - location: ~/.claude/tmp   # Claude Code scratchpads
    writable: true
```

A non-empty `mounts` list replaces Colima's default read-only mount of `~`. Note containers get full read, write, and delete access to mounted paths, regardless of nono's rules.

The `jph-docker` nono profile connects sandboxed agents to this VM. It sets `DOCKER_HOST` to `unix://~/.colima/agents/docker.sock` and `DOCKER_CONFIG` to the client directory above, grants the sandbox that one unix socket and nothing else under `~/.colima`, and denies `DOCKER_CONTEXT` and `DOCKER_TLS*` so an agent cannot retarget another daemon. Verify from inside a sandboxed session with `docker info`.
