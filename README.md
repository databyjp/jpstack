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
