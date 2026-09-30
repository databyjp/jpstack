# Personal research workspace

This directory is a minimal Pi workspace for researching a topic and auditing a prior claim or recommendation. `AGENTS.md` supplies the shared evidence standards. The two prompt templates supply the task-specific workflows.

## Use the workspace

Start Pi from this directory:

Pi loads project prompt templates only after the project is trusted. If Pi asks, trust this directory and restart. For a one-off trusted run, start it with `pi --approve`.

Available prompts:

```text
/research <topic or question>
/verify-recommendation [claim, product, or recommendation]
```

`/verify-recommendation` audits the most consequential claim or recommendation in the current conversation when no argument is supplied.

Pi discovers the templates in `.pi/prompts/`. No project skill or extension is required. Until the old installation is removed, Pi may also discover `../.agents/skills/last30days` while walking ancestor directories.

## Save research

Research remains in the conversation unless you ask Pi to save it. Saved artifacts go under `outputs/` by default. Generated output files are ignored so exploratory work does not become a maintained reference accidentally.
