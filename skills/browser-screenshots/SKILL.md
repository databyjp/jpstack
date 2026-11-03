---
name: browser-screenshots
description: Take web page screenshots with Playwright in Docker. Use when a task needs a screenshot of a URL or a local HTML page, or when a browser cannot start inside the nono sandbox.
---

# Browser screenshots

Host browsers cannot run inside the nono sandbox. Take page screenshots with Playwright in Docker:

```bash
dir=~/code/scratch/agents/<short-description>-$(openssl rand -hex 3)
mkdir -p "$dir"
docker run --rm --init --ipc=host --user pwuser \
  --security-opt no-new-privileges \
  -v "$dir:/out" \
  mcr.microsoft.com/playwright:v1.50.0-noble \
  npx -y playwright@1.50.0 screenshot --full-page <url> /out/<name>.png
```

- Write screenshots to your own folder under `~/code/scratch/agents/`, and give the user its path when you finish. The sandbox cannot delete files there; the user clears the folder.
- Mount only folders under `~/code` or `~/.claude/tmp` (Claude Code scratchpads). The Docker VM mounts only those two paths. A folder mounted from anywhere else, including `/private/tmp`, is empty inside the container, and the screenshot never reaches the host.
- For a local HTML page, mount the folder containing the page read-only (`-v "$PWD/<dir>:/site:ro"`) and use a `file:///site/...` URL. Do not start a server on the host; the sandbox blocks binding ports. Mount only the folders the page needs, never the project root or `$HOME`.
- Do not use Chrome, the Claude in Chrome extension, or a host browser with a real profile.
