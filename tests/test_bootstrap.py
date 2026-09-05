import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = REPO_ROOT / "bootstrap.py"


class BootstrapCliTests(unittest.TestCase):
    def test_apply_installs_pi_and_shared_skill_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            result = self.run_bootstrap(home)

            self.assertEqual(result.returncode, 0, result.stderr)
            expected_links = {
                home / ".pi/agent/AGENTS.md": REPO_ROOT / "pi-agent/AGENTS.md",
                home / ".pi/agent/APPEND_SYSTEM.md": REPO_ROOT
                / "pi-agent/APPEND_SYSTEM.md",
                home / ".pi/agent/extensions/final-stamp": REPO_ROOT
                / "pi-extensions/final-stamp",
                home / ".agents/skills": REPO_ROOT / "skills",
            }
            for target, source in expected_links.items():
                with self.subTest(target=target):
                    self.assertTrue(target.is_symlink())
                    self.assertEqual(target.resolve(), source.resolve())

    def test_apply_replaces_stale_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            target = home / ".pi/agent/AGENTS.md"
            target.parent.mkdir(parents=True)
            target.symlink_to(home / "old-configuration")

            result = self.run_bootstrap(home)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.is_symlink())
            self.assertEqual(
                target.resolve(), (REPO_ROOT / "pi-agent/AGENTS.md").resolve()
            )

    def test_apply_refuses_non_symlink_conflicts_before_making_changes(self) -> None:
        for conflict_kind in ("file", "directory"):
            with (
                self.subTest(conflict_kind=conflict_kind),
                tempfile.TemporaryDirectory() as directory,
            ):
                home = Path(directory)
                target = home / ".agents/skills"
                target.parent.mkdir(parents=True)
                if conflict_kind == "file":
                    target.write_text("keep me")
                else:
                    target.mkdir()
                    (target / "keep-me").write_text("keep me")

                result = self.run_bootstrap(home)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("refusing to replace non-symlink", result.stderr)
                self.assertFalse((home / ".pi/agent/AGENTS.md").exists())
                if conflict_kind == "file":
                    self.assertEqual(target.read_text(), "keep me")
                else:
                    self.assertEqual((target / "keep-me").read_text(), "keep me")

    def run_bootstrap(self, home: Path) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["HOME"] = str(home)
        return subprocess.run(
            [sys.executable, str(BOOTSTRAP), "apply"],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
