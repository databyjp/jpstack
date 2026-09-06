import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE_SCRIPT = Path(__file__).resolve().parents[1] / "collect_configs.py"


class CollectConfigsCliTests(unittest.TestCase):
    def test_collects_local_configs_and_omits_predefined_pi_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            home = workspace / "home"
            repository = workspace / "repo"
            pi_source = home / ".pi/agent/settings.json"
            nono_source = home / ".config/nono/profiles/pi-mise.json"
            pi_source.parent.mkdir(parents=True)
            nono_source.parent.mkdir(parents=True)

            pi_local = {
                "defaultModel": "device-model",
                "defaultProvider": "device-provider",
                "lastChangelogVersion": "9.9.9",
                "theme": "dark",
                "packages": ["npm:example"],
            }
            nono_local = {
                "extends": ["pi"],
                "meta": {"name": "pi-mise"},
                "filesystem": {"read": ["$HOME/.local/share/mise/installs/node"]},
            }
            pi_source.write_text(json.dumps(pi_local))
            nono_source.write_text(json.dumps(nono_local))

            self.prepare_repository(repository)
            result = self.run_collector(home, repository)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads((repository / "pi-agent/settings.json").read_text()),
                {"theme": "dark", "packages": ["npm:example"]},
            )
            self.assertEqual(
                json.loads((repository / "nono/pi-mise.json").read_text()),
                nono_local,
            )
            self.assertEqual(json.loads(pi_source.read_text()), pi_local)
            self.assertEqual(json.loads(nono_source.read_text()), nono_local)

    def test_invalid_source_does_not_overwrite_either_repository_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            home = workspace / "home"
            repository = workspace / "repo"
            pi_source = home / ".pi/agent/settings.json"
            nono_source = home / ".config/nono/profiles/pi-mise.json"
            pi_source.parent.mkdir(parents=True)
            nono_source.parent.mkdir(parents=True)
            pi_source.write_text('{"theme": "dark"}')
            nono_source.write_text("not JSON")
            self.prepare_repository(repository)
            pi_target = repository / "pi-agent/settings.json"
            nono_target = repository / "nono/pi-mise.json"
            original_pi = pi_target.read_text()
            original_nono = nono_target.read_text()

            result = self.run_collector(home, repository)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("cannot read", result.stderr)
            self.assertEqual(pi_target.read_text(), original_pi)
            self.assertEqual(nono_target.read_text(), original_nono)

    def test_refuses_to_overwrite_an_untracked_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            home = workspace / "home"
            repository = workspace / "repo"
            pi_source = home / ".pi/agent/settings.json"
            nono_source = home / ".config/nono/profiles/pi-mise.json"
            pi_source.parent.mkdir(parents=True)
            nono_source.parent.mkdir(parents=True)
            pi_source.write_text('{"theme": "dark"}')
            nono_source.write_text('{"extends": ["pi"]}')
            self.prepare_repository(repository)
            subprocess.run(
                ["git", "-C", repository, "rm", "--cached", "nono/pi-mise.json"],
                capture_output=True,
                check=True,
            )
            pi_target = repository / "pi-agent/settings.json"
            original_pi = pi_target.read_text()

            result = self.run_collector(home, repository)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "refusing to overwrite untracked configuration", result.stderr
            )
            self.assertEqual(pi_target.read_text(), original_pi)

    def prepare_repository(self, repository: Path) -> None:
        (repository / "pi-agent").mkdir(parents=True)
        (repository / "nono").mkdir()
        (repository / "pi-agent/settings.json").write_text("{}\n")
        (repository / "nono/pi-mise.json").write_text("{}\n")
        shutil.copy(SOURCE_SCRIPT, repository / "collect_configs.py")
        subprocess.run(["git", "init", "-q", repository], check=True)
        subprocess.run(
            [
                "git",
                "-C",
                repository,
                "add",
                "pi-agent/settings.json",
                "nono/pi-mise.json",
            ],
            check=True,
        )

    def run_collector(
        self, home: Path, repository: Path
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["HOME"] = str(home)
        return subprocess.run(
            [sys.executable, str(repository / "collect_configs.py")],
            cwd=repository,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
