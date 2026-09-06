#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class ConfigSpec:
    source: Path
    destination: Path
    ignored_keys: frozenset[str]


CONFIGS = (
    ConfigSpec(
        source=Path(".pi/agent/settings.json"),
        destination=Path("pi-agent/settings.json"),
        ignored_keys=frozenset(
            {"defaultModel", "defaultProvider", "lastChangelogVersion"}
        ),
    ),
    ConfigSpec(
        source=Path(".config/nono/profiles/pi-mise.json"),
        destination=Path("nono/pi-mise.json"),
        ignored_keys=frozenset(),
    ),
)


class CollectionError(Exception):
    pass


def load_all_configs(home: Path) -> list[tuple[ConfigSpec, dict[str, object]]]:
    loaded = []
    for config in CONFIGS:
        source = home / config.source
        try:
            value = json.loads(source.read_text())
        except (OSError, json.JSONDecodeError) as error:
            raise CollectionError(f"cannot read {source}: {error}") from error
        if not isinstance(value, dict):
            raise CollectionError(f"expected a JSON object in {source}")
        loaded.append(
            (
                config,
                {
                    key: item
                    for key, item in value.items()
                    if key not in config.ignored_keys
                },
            )
        )
    return loaded


def require_tracked_destinations(repository: Path) -> None:
    destinations = [str(config.destination) for config in CONFIGS]
    result = subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "ls-files",
            "--error-unmatch",
            "--",
            *destinations,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "one or more destinations are not tracked"
        raise CollectionError(
            f"refusing to overwrite untracked configuration: {detail}"
        )


def write_json(target: Path, value: dict[str, object]) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=target.parent,
            prefix=f".{target.name}.",
            delete=False,
        ) as temporary:
            json.dump(value, temporary, indent=2)
            temporary.write("\n")
            temporary_path = Path(temporary.name)
        temporary_path.chmod(target.stat().st_mode)
        temporary_path.replace(target)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def collect(home: Path, repository: Path) -> None:
    configs = load_all_configs(home)
    require_tracked_destinations(repository)
    for config, value in configs:
        target = repository / config.destination
        write_json(target, value)
        print(f"collected {home / config.source} -> {target}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect local Pi and Nono configuration into this repository"
    )
    parser.parse_args()
    try:
        collect(Path.home(), REPO_ROOT)
    except CollectionError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
