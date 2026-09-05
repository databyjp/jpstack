#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


class InstallConflict(Exception):
    pass


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
    return links


def apply(home: Path) -> None:
    links = desired_links(home)
    conflicts = [
        target for _, target in links if target.exists() and not target.is_symlink()
    ]
    if conflicts:
        paths = ", ".join(str(path) for path in conflicts)
        raise InstallConflict(f"refusing to replace non-symlink: {paths}")

    for source, target in links:
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink():
            if target.resolve(strict=False) == source.resolve():
                print(f"unchanged {target}")
                continue
            target.unlink()
        target.symlink_to(source, target_is_directory=source.is_dir())
        print(f"linked {target} -> {source}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Install jpstack configuration")
    parser.add_argument("command", choices=("apply",))
    args = parser.parse_args()

    try:
        if args.command == "apply":
            apply(Path.home())
    except InstallConflict as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
