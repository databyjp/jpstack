#!/usr/bin/env python3
"""Install jpstack configuration as symlinks into the home directory.

Links the Pi instruction files and extensions, the shared ``skills/`` tree
for Pi, and one link per skill into ``~/.claude/skills/`` so Claude Code reads
the same files. A target that is a real file or directory is replaced only
with confirmation: interactively one by one, or all at once with ``--yes``.
Replaced targets are moved to a ``.trash/`` directory beside them, never
deleted.
"""

import argparse
import shutil
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


class InstallConflict(Exception):
    pass


def skill_dirs() -> list[Path]:
    """Each skill directory under ``skills/``: one that holds a ``SKILL.md``."""
    return sorted(
        path
        for path in (REPO_ROOT / "skills").iterdir()
        if (path / "SKILL.md").is_file()
    )


def desired_links(home: Path) -> list[tuple[Path, Path]]:
    links = [
        (REPO_ROOT / "pi-agent/AGENTS.md", home / ".pi/agent/AGENTS.md"),
        (
            REPO_ROOT / "pi-agent/APPEND_SYSTEM.md",
            home / ".pi/agent/APPEND_SYSTEM.md",
        ),
        (REPO_ROOT / "skills", home / ".agents/skills"),
    ]
    extension_root = REPO_ROOT / "pi-extensions"
    links.extend(
        (extension, home / ".pi/agent/extensions" / extension.name)
        for extension in sorted(extension_root.iterdir())
    )
    # Claude Code reads ~/.claude/skills/<name>/SKILL.md. Linking each skill,
    # not the directory, leaves Claude's own entries (synced/, .trash/) alone.
    links.extend(
        (skill, home / ".claude/skills" / skill.name) for skill in skill_dirs()
    )
    return links


def describe(target: Path) -> str:
    if target.is_dir():
        count = sum(1 for path in target.rglob("*") if path.is_file())
        return f"directory, {count} file{'s' if count != 1 else ''}"
    return "file"


def move_to_trash(target: Path) -> Path:
    """Move ``target`` into a ``.trash/`` directory beside it; return the new path."""
    trash = target.parent / ".trash"
    trash.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = trash / f"{target.name}-{stamp}"
    shutil.move(str(target), str(destination))
    return destination


def apply(home: Path, confirm: Callable[[Path, Path], bool] | None = None) -> int:
    """Install the links; return the number of conflicts left in place.

    ``confirm(source, target)`` decides whether a real file or directory at
    ``target`` is moved to trash and replaced. Without it, any such conflict
    aborts before anything is changed, since a non-interactive run must not
    move files unasked.
    """
    links = desired_links(home)
    if confirm is None:
        conflicts = [
            target for _, target in links if target.exists() and not target.is_symlink()
        ]
        if conflicts:
            paths = ", ".join(str(path) for path in conflicts)
            raise InstallConflict(
                f"refusing to replace non-symlink: {paths} "
                "(run interactively to be asked, or pass --yes)"
            )

    kept = 0
    for source, target in links:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            if target.resolve(strict=False) == source.resolve():
                print(f"unchanged {target}")
                continue
            target.unlink()
        elif target.exists():
            if not confirm(source, target):
                print(f"kept {target}")
                kept += 1
                continue
            moved = move_to_trash(target)
            print(f"moved {target} -> {moved}")
        target.symlink_to(source, target_is_directory=source.is_dir())
        print(f"linked {target} -> {source}")
    return kept


def ask(source: Path, target: Path) -> bool:
    answer = input(
        f"Replace {target} ({describe(target)}) with a link to {source}? [y/N] "
    )
    return answer.strip().lower() in ("y", "yes")


def main() -> int:
    parser = argparse.ArgumentParser(description="Add jpstack configuration symlinks")
    parser.add_argument("command", choices=("apply",))
    parser.add_argument(
        "--yes",
        action="store_true",
        help="replace every conflicting file or directory without asking "
        "(each is moved to a .trash/ directory beside it)",
    )
    args = parser.parse_args()

    if args.yes:
        confirm = lambda source, target: True  # noqa: E731
    elif sys.stdin.isatty():
        confirm = ask
    else:
        confirm = None

    try:
        if args.command == "apply":
            kept = apply(Path.home(), confirm)
            if kept:
                print(
                    f"{kept} target(s) kept in place; re-run to be asked again",
                    file=sys.stderr,
                )
    except InstallConflict as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
