# Nono profiles

These profiles configure Pi and Claude Code on this macOS machine. Development tooling is shared through `jph-default`; GitHub authentication is selected explicitly through `gh-jph` or `gh-agent`.

## Choose a GitHub identity

| Launch profile | GitHub account | Intended use |
| --- | --- | --- |
| `pi-jph` | `databyjp` | Personal and private-repository work |
| `claude-jph` | `databyjp` | Claude Code with the existing personal tooling and permissions |
| `pi-agent` | `ar-woodhouse` | Autonomous public OSS fork-and-PR work |

`gh-jph` and `gh-agent` configure the host-side credential proxy. Compose exactly one, last in the launch profile's `extends` list. The runtime packs explicitly disable inherited proxy credentials, so the identity component must follow them.

`pi-agent` omits the Claude runtime component because that component grants broad Keychain access. It also omits `jph-docker`: Docker access should be added only after checking that the VM cannot expose personal credentials through host mounts. Existing personal profiles retain their Claude and Docker components.

## Install the profiles

Profiles under `~/.config/nono/profiles/` are symlinks to the JSON files in this directory. Keep those links when reviewing or updating the source. To register the GitHub identity profiles and agent launch profile on another installation, run these commands in your normal terminal:

```bash
repo="$HOME/code/agents/jpstack"
for name in gh-jph gh-agent pi-agent; do
  ln -s "$repo/nono/$name.json" "$HOME/.config/nono/profiles/$name.json"
done
```

`ln -s` refuses to replace an existing destination. Inspect any conflict rather than forcing an overwrite. Keep the repository files authoritative rather than installing independent copies.

Once all links exist, validate the compositions:

```bash
for name in jph-default gh-jph gh-agent pi-jph claude-jph pi-agent; do
  nono profile validate --strict "$repo/nono/$name.json" || break
done
nono profile show pi-agent
```

These profiles use features present in nono 0.79.0. The credential-capture commands use the Homebrew `gh` at `/opt/homebrew/bin/gh` and macOS `/usr/bin/security`.

## Prepare authentication

### Personal account

Your normal terminal must already have a stored `gh` login for `databyjp` on `github.com`. The proxy explicitly selects that username and ignores ambient `GH_TOKEN` and `GITHUB_TOKEN` values when loading its credential. It does not switch your active account or update your terminal's Git configuration.

### Agent account

Close older broad-access agent sessions before adding the token. Profile changes apply only to new sessions.

While signed into `ar-woodhouse`, create an expiring classic PAT at <https://github.com/settings/tokens/new>. Start with a 30-day lifetime and only the `public_repo` scope. Do not add `repo`, `workflow`, or administrative scopes for this public OSS workflow.

In your normal terminal, store the PAT in Keychain:

```bash
/usr/bin/security add-generic-password \
  -s nono-agent \
  -a github-pat \
  -w
```

Keep `-w` last so `security` prompts for the token instead of putting it in the command line. Do not put the PAT in shell startup files, repository files, Pi settings, or chat. An existing item causes this command to fail; inspect it before updating it.

`gh-agent` loads the API token from `keyring://nono-agent/github-pat`. Its host-side Git capture reads that same item and formats `ar-woodhouse:PAT` for Basic authentication. Neither route uses your personal `gh` login as a fallback.

## Start a session

```bash
# Public OSS work as the agent
nono run --profile pi-agent -- pi

# Explicitly use your personal identity, including for private repositories
nono run --profile pi-jph -- pi
```

The profiles request nono's trusted TLS-interception CA because `gh` on macOS uses the system trust store. The first launch may require a host-side trust prompt. Keep certificate verification enabled; do not use `sslVerify=false` or insecure TLS options.

`GH_TOKEN` and `GITHUB_GIT_TOKEN` inside a proxied session are placeholders, not the real credentials. Requests use the authenticated forward proxy: API requests receive the selected token, and Git HTTPS requests receive Basic authentication. Git's credential helper is not used for GitHub authentication.

## Work on the public fork

Use an agent checkout with these remotes:

```text
origin    https://github.com/ar-woodhouse/weaviate-docs.git
upstream  https://github.com/weaviate/docs.git
```

The fork's immediate parent is `databyjp/weaviate-docs`; its original source repository is `weaviate/docs`. Choose the PR target explicitly when submitting changes.

Both identity components rewrite `git@github.com:...` and `ssh://git@github.com/...` remotes to HTTPS for the session. They do not rewrite stored remotes or global Git configuration. Prefer a separate agent checkout rather than changing a personal checkout's `origin`.

The agent's commit author is `ar-woodhouse` with the GitHub no-reply address `357525867+ar-woodhouse@users.noreply.github.com`. The agent profile ignores personal global/system Git configuration, resets credential helpers, and disables inherited commit signing for the session.

## Verify before autonomous writes

In your normal terminal:

```bash
gh api user --jq .login
# Expected: databyjp
```

In a newly launched `pi-agent` session:

```bash
gh api user --jq .login
# Expected: ar-woodhouse

git var GIT_AUTHOR_IDENT
nono why --self --path "$HOME/.config/gh" --op read
nono why --self --path "$HOME/Library/Keychains" --op read
# Both path queries should report DENIED.
```

Verify a read-only fetch from the intended checkout before authorizing a test branch push. Confirm the API identity before relying on it: the Keychain reference selects an item, not the GitHub account contained in its token. Keep pushes and PR creation subject to your normal review policy until those live checks pass.

## Permission boundaries

- The agent Git route permits smart-HTTP fetches and permits `git-receive-pack` only under `/ar-woodhouse/`. It rejects Git pushes to other owners. This is an owner-level rule, not a selected-repository rule.
- The GitHub API route supports normal `gh` commands, including GraphQL. It is **not repository-restricted**: the PAT's `public_repo` scope and the agent account's memberships define its API authority. Do not grant that account more public-repository authority than intended.
- The agent profile filters inherited environment variables, blocks conventional personal GitHub/Git/SSH credential paths, and blocks the symlink-backed profile source. It grants no Docker socket access. Its standard deny groups keep Keychain files protected.
- `allow_domain: ["*"]` preserves general development network access through the proxy. These are not general-purpose egress allowlists.
- Pi state and development working trees remain shared. Do not put personal GitHub tokens in those locations. This configuration separates conventional credential sources; it does not create a separate OS account or make arbitrary shared files secret.
- These profiles target macOS. The agent uses deny-within-allow rules under the shared code directory; Linux Landlock cannot enforce that arrangement in the same way.

Private work requires an explicit personal-profile launch. A correctly scoped agent PAT cannot grant access to private repositories, and a missing or rejected agent credential does not select the personal route.

For token rotation, update the Keychain item from your normal terminal and restart agent sessions. The proxy keeps credentials in memory, and Git captures are cached for up to 900 seconds.
