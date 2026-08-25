# Gated development extension

This Pi extension provides the `/gated-dev` command used by the
`gated-development` skill.

## Install for local development

From the repository root:

```sh
mkdir -p "$HOME/.pi/agent/extensions"
ln -s "$(pwd)/extensions/gated-dev" "$HOME/.pi/agent/extensions/gated-dev"
```

Restart Pi after creating the symlink. Use `/reload` after later source changes.

## Commands

```text
/gated-dev start
/gated-dev approve <vertical slice>
/gated-dev status
/gated-dev off
```

`start` locks `bash`, `edit`, and `write`. `approve` permits one agent run and
then locks those tools again when the agent settles. State does not survive a
Pi restart or `/reload`.
