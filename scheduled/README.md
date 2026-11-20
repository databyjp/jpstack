# Scheduled Pi tasks with agents-cron

Use [agents-cron](https://github.com/fookhsu/agents-cron) for weekly summaries,
repository digests, PR triage, and other independent recurring jobs. This guide
records JP's macOS setup: launchd checks for due tasks every minute, and each run
starts a fresh Pi session inside the `pi-jph` nono profile.

```text
launchd: every 60 seconds
  → agents-cron run-due --all
    → pi-scheduled wrapper, started in the task's working directory
      → nono run --profile pi-jph --allow-cwd
        → pi --print, with a separate saved session for this run
```

Pi does not need to remain open. The user LaunchAgent runs while logged in;
sleep and power-off delay execution. Missed recurring periods collapse into one
catch-up run, not a backlog. One-off tasks have a default five-minute lateness
grace, after which agents-cron records them as missed.

## Install the package and sandbox wrapper

Run setup commands from a normal host terminal, not from inside a sandboxed Pi
session. Follow the [nono profile and authentication setup](../nono/README.md)
first. Pi needs working model credentials, and agents-cron requires Node
22.19 or newer.

```sh
pi install npm:agents-cron
mkdir -p "$HOME/.local/bin" "$HOME/Library/LaunchAgents" "$HOME/.pi/agent/logs"
```

Restart Pi or run `/reload` to load its scheduling commands. Save this executable
as `~/.local/bin/pi-scheduled`:

```sh
#!/bin/sh
set -eu

exec /Users/jphwang/.local/bin/nono run \
  --profile pi-jph \
  --allow-cwd \
  --silent \
  --startup-timeout 0 \
  -- /Users/jphwang/.pi/agent/bin/pi "$@"
```

```sh
chmod +x "$HOME/.local/bin/pi-scheduled"
```

Use the real Pi executable, not a shell function or this wrapper itself.
`--silent` keeps nono's banners out of the captured answer; `--startup-timeout 0`
disables the TUI startup watchdog because scheduled runs use `--print`.

The following CLI examples use these variables. Set them in each host terminal
where you use the examples; the export also keeps manual task runs sandboxed:

```sh
AC="$HOME/.pi/agent/npm/node_modules/.bin/agents-cron"
export AGENTS_CRON_PI_BIN="$HOME/.local/bin/pi-scheduled"
```

The adapter directly spawns an executable, so it does not use the `pi()` function
in `.zshrc`. `AGENTS_CRON_PI_BIN` must be a path to the wrapper, not a command
string containing `nono run ...`.

## Configure launchd

Save the following as
`~/Library/LaunchAgents/com.jphwang.agents-cron.plist`. These are JP's installed
absolute paths. Check `command -v node` and the wrapper paths when setting up
another machine. Plist strings do not expand `$HOME` or `~`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.jphwang.agents-cron</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/jphwang/.local/share/mise/installs/node/24.22.1/bin/node</string>
        <string>/Users/jphwang/.pi/agent/npm/node_modules/agents-cron/bin/agents-cron.mjs</string>
        <string>run-due</string>
        <string>--all</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/jphwang</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>HOME</key>
        <string>/Users/jphwang</string>
        <key>PATH</key>
        <string>/Users/jphwang/.local/share/mise/installs/node/24.22.1/bin:/Users/jphwang/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
        <key>AGENTS_CRON_PI_BIN</key>
        <string>/Users/jphwang/.local/bin/pi-scheduled</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>StartInterval</key>
    <integer>60</integer>
    <key>ProcessType</key>
    <string>Background</string>
    <key>Umask</key>
    <integer>63</integer>
    <key>StandardOutPath</key>
    <string>/Users/jphwang/.pi/agent/logs/agents-cron.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/jphwang/.pi/agent/logs/agents-cron.err.log</string>
</dict>
</plist>
```

The explicit environment is necessary because launchd does not read `.zshrc`.
The scheduler itself runs outside nono; each Pi child enters the sandbox through
the wrapper. `Umask` is decimal 63, equivalent to octal `077`, so new log files
are private to this user.

Validate the file and inspect existing tasks before loading it. `RunAtLoad`
starts a check immediately, and `--all` executes due tasks across every project,
including any model usage or external actions those tasks authorize.

```sh
plutil -lint "$HOME/Library/LaunchAgents/com.jphwang.agents-cron.plist"
"$AC" list
launchctl bootstrap "gui/$(id -u)" \
  "$HOME/Library/LaunchAgents/com.jphwang.agents-cron.plist"
launchctl print "gui/$(id -u)/com.jphwang.agents-cron"
```

A healthy idle job shows `state = not running`, `last exit code = 0`, and
`run interval = 60 seconds`. The runner exits after each check; it is not a
persistent daemon. It loads again at future logins.

When changing the plist, reload it from the host terminal. Do this only when no
task is running, because unloading stops the active runner:

```sh
launchctl bootout "gui/$(id -u)/com.jphwang.agents-cron"
launchctl bootstrap "gui/$(id -u)" \
  "$HOME/Library/LaunchAgents/com.jphwang.agents-cron.plist"
```

The Node path is pinned to the installed version. If that version is removed,
update both its `ProgramArguments` entry and its directory in `PATH`, then reload.
Keep one trigger for `run-due --all`; do not also install a cron entry.

## Create and manage tasks

In the target repository, create `.pi/tasks/weekly-summary.md` with the complete
instructions: repositories and sources to inspect, time window, report location,
and permitted actions. Scheduled runs do not inherit an interactive conversation
and cannot answer approval prompts. For digests, start with read-only external
access and a local report rather than autonomous comments, labels, or pushes.

Then create a task from that repository:

```sh
"$AC" add \
  --name weekly-summary \
  --cron '0 17 * * 5' \
  --prompt 'Read .pi/tasks/weekly-summary.md and carry out its instructions.' \
  --notify always
```

This runs on Fridays at 17:00 in the scheduler's default timezone. Use
`--every 3d` instead of `--cron ...` for an interval of three days. The stored
prompt above tells Pi to read the file on every run, so file edits apply to future
runs; it is not a native prompt-file option. You can also pass the entire task
text to `--prompt`.

`--notify always` includes successful runs, but delivery still requires configured
channels. Notifications otherwise default to errors only. See the upstream
[notification setup](https://github.com/fookhsu/agents-cron#notifications).
Saved reports and transcripts remain available without notifications.

### Manage tasks from inside Pi

The host CLI above can manage the registry. Inside sandboxed Pi, commands that
create or change tasks also need write access to `~/.agents/cron/`. The tracked
`pi-jph` composition grants `~/.agents/` read access only. To grant the narrower
registry directory for one interactive session, start from the host terminal:

```sh
nono run --profile pi-jph --allow-cwd \
  --allow "$HOME/.agents/cron" -- "$PI_BIN"
```

`PI_BIN` must name the real Pi executable used by the interactive shell wrapper.
For persistent access, review and promote a nono profile draft with that same
narrow grant. The scheduled Pi wrapper does not need it: the host runner owns
registry writes, and the scheduling extension is inactive inside task sessions.

With management access in place, Pi commands include:

```text
/schedule add "0 17 * * 5" Read .pi/tasks/weekly-summary.md and carry out its instructions. --notify always
/schedule add 3d Summarise this repository's work over the past three days.
/schedule list
/schedule set <task-id> --cwd packages/api
/schedule runs <task-id>
/schedule open <run-id>
/schedule remove <task-id>
```

Quote cron expressions in slash commands. `/schedule open` prints the saved
session path; it does not merge the run into the current conversation. Removal
asks for confirmation in Pi.

### Working directory and sandbox scope

Tasks belong to the project where they are created. CLI `--project /path/to/repo`
selects a different owning project. Execution defaults to that project root;
`--cwd` overrides only the agent's working directory. Relative overrides such as
`packages/api` resolve against the owning project, not launchd's directory.

For an existing task, substitute its ID below:

```sh
TASK_ID=task_replace_with_actual_id
"$AC" set "$TASK_ID" --cwd /Users/jphwang/code/agents/general
"$AC" show "$TASK_ID"
"$AC" runs "$TASK_ID"
```

Pause a task with `"$AC" disable "$TASK_ID"`, resume it with
`"$AC" enable "$TASK_ID"`, or delete its definition with
`"$AC" remove "$TASK_ID"`. These are separate actions, not a sequence to run.

To execute an existing task immediately, without changing its schedule, run
`"$AC" run "$TASK_ID"` from a host terminal with the wrapper export above. Avoid
launching the nono wrapper from inside an already-sandboxed Pi session.

The adapter sets the working directory before invoking nono, so `--allow-cwd`
applies to that task's directory. It does not narrow the profile's other grants:
`pi-jph` inherits read/write access to all of `~/code` from `jph-default`, rather
than isolating one repository. It also selects JP's personal GitHub identity.
Review the [profile boundaries](../nono/README.md#permission-boundaries) before
authorizing unattended external writes. A working-directory override does not
move the owning project's session files; those paths must remain writable too.

Task definitions live at `~/.agents/cron/tasks.json`. Per-project run records,
reports, and transcripts live under `.agents/cron/`. Exclude that project-local
directory from Git; it can contain private prompts and output. Fresh runs can
read explicit progress files, such as a last-successful cutoff, when incremental
digests or duplicate-action prevention require state across runs.

## Verify the complete scheduling and sandbox chain

An idle runner with exit code zero proves only that it can check the queue.
Use one scheduled diagnostic task to test an actual Pi run. This consumes one
short agent run using the configured model; do not manually trigger it, because
that would skip testing launchd.

From a host terminal, prepare harmless canaries in the test workspace and outside
the scheduled profile's grants:

```sh
cd "$HOME/code/agents/general"
printf 'workspace-canary\n' > scheduler-allowed-canary.txt
printf 'outside-canary\n' > \
  "$HOME/Library/LaunchAgents/pi-scheduler-canary.txt"

"$AC" add \
  --name scheduler-sandbox-smoke \
  --at "$(date -u -v+2M '+%Y-%m-%dT%H:%M:%SZ')" \
  --notify never \
  --prompt 'Perform a diagnostic check only. Do not modify source code or sandbox policy.
Report the actual working directory and whether NONO_CAP_FILE is set.
Read scheduler-allowed-canary.txt in the working directory.
Use nono why --self to check read access to that file and to /Users/jphwang/Library/LaunchAgents/pi-scheduler-canary.txt.
Use Python to attempt an actual read of the outside canary. Catch PermissionError and report BLOCKED. A missing file or any other error is INCONCLUSIVE, not a pass. If the read succeeds, report UNEXPECTED_ACCESS. Do not inspect other private files.
Write the observations to scheduler-sandbox-smoke-result.json in the working directory.
Return PASS only if the working directory is /Users/jphwang/code/agents/general, NONO_CAP_FILE is set, the workspace file contains workspace-canary, the outside read is denied by the effective policy, and the actual outside-file read is blocked. Otherwise report FAIL or INCONCLUSIVE with evidence.'
```

Keep the returned task ID, leave the Mac awake, and allow a few minutes for the
run. Inspect `"$AC" runs "$TASK_ID"` after assigning that ID to `TASK_ID`, then
open `scheduler-sandbox-smoke-result.json`. Use `/schedule open <run-id>` to
inspect the raw tool output, not just the final summary.

The run must be marked `scheduled`, the workspace read and result write must
succeed, and the outside file must be denied both by `nono why --self` and by an
actual read. An agents-cron `success` status alone records the Pi process outcome,
not whether these diagnostic assertions passed. Do not expand permissions to
make the outside canary readable; denial is the intended result.

This smoke test passed on 2026-11-19 with agents-cron 0.18.2. It demonstrated
scheduling, the intended working directory, workspace read/write access, and an
actual denied read outside the sandbox grants. It did not certify every
filesystem or network rule. If the profile changes, review the canary locations
and repeat the test rather than assuming the same boundary still applies.

A one-off task disables after its attempt. Remove its definition with
`"$AC" remove "$TASK_ID"` when finished. Delete the two canary files and diagnostic
JSON once their evidence is no longer needed; do not remove the LaunchAgent.

## Inspect failures or stop scheduling

```sh
tail -n 40 "$HOME/.pi/agent/logs/agents-cron.out.log"
tail -n 40 "$HOME/.pi/agent/logs/agents-cron.err.log"
```

For a task failure, inspect its run record and saved session. Check the Node and
wrapper paths, model credentials, profile access, and any GitHub authentication
the task needs. Project-local settings, skills, and extensions require saved
project trust: review `/trust` interactively in that project before relying on
those resources in headless runs. `AGENTS.md` loads independently of that trust
setting.

Run launchctl setup commands in the host terminal if activation fails inside a
sandbox. To pause all automatic checks, use the `launchctl bootout` command above.
To stop loading them at future logins as well, move the plist out of
`~/Library/LaunchAgents/` after unloading it. Disabling or removing one task does
not require stopping launchd.

For more commands, see the [upstream guide](https://github.com/fookhsu/agents-cron#readme)
and [Pi package page](https://pi.dev/packages/agents-cron).
