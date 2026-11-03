import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADD_SYMLINKS = REPO_ROOT / "add_symlinks.py"


class AddSymlinksCliTests(unittest.TestCase):
    def test_apply_installs_pi_and_shared_skill_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            result = self.run_script(home)

            self.assertEqual(result.returncode, 0, result.stderr)
            expected_links = {
                home / ".pi/agent/AGENTS.md": REPO_ROOT / "pi-agent/AGENTS.md",
                home / ".pi/agent/APPEND_SYSTEM.md": REPO_ROOT
                / "pi-agent/APPEND_SYSTEM.md",
                home / ".pi/agent/extensions/final-stamp": REPO_ROOT
                / "pi-extensions/final-stamp",
                home / ".pi/agent/extensions/mindful-session": REPO_ROOT
                / "pi-extensions/mindful-session",
                home / ".agents/skills": REPO_ROOT / "skills",
            }
            for target, source in expected_links.items():
                with self.subTest(target=target):
                    self.assertTrue(target.is_symlink())
                    self.assertEqual(target.resolve(), source.resolve())

    def test_apply_leaves_existing_pi_settings_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            target = home / ".pi/agent/settings.json"
            target.parent.mkdir(parents=True)
            original = '{\n  "theme": "device-specific"\n}\n'
            target.write_text(original)

            result = self.run_script(home)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_text(), original)

    def test_apply_replaces_stale_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            target = home / ".pi/agent/AGENTS.md"
            target.parent.mkdir(parents=True)
            target.symlink_to(home / "old-configuration")

            result = self.run_script(home)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.is_symlink())
            self.assertEqual(
                target.resolve(), (REPO_ROOT / "pi-agent/AGENTS.md").resolve()
            )

    def test_apply_links_each_skill_into_claude_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            result = self.run_script(home)

            self.assertEqual(result.returncode, 0, result.stderr)
            target = home / ".claude/skills/show-me"
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), (REPO_ROOT / "skills/show-me").resolve())
            # Only directories holding a SKILL.md are skills; skills/synced is not.
            self.assertFalse((home / ".claude/skills/synced").exists())

    def test_apply_with_yes_moves_conflicts_to_trash_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            target = home / ".claude/skills/show-me"
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("stale copy")
            sibling = home / ".claude/skills/synced"
            sibling.mkdir()

            result = self.run_script(home, "--yes")

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(target.is_symlink())
            trashed = list((home / ".claude/skills/.trash").glob("show-me-*"))
            self.assertEqual(len(trashed), 1)
            self.assertEqual((trashed[0] / "SKILL.md").read_text(), "stale copy")
            self.assertTrue(sibling.is_dir() and not sibling.is_symlink())

    def test_apply_asks_per_conflict_and_keeps_declined_targets(self) -> None:
        sys.path.insert(0, str(REPO_ROOT))
        import add_symlinks

        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            keep = home / ".claude/skills/show-me"
            replace = home / ".claude/skills/unslop"
            for target in (keep, replace):
                target.mkdir(parents=True)
                (target / "SKILL.md").write_text("stale copy")
            answers = {keep: False, replace: True}

            kept = add_symlinks.apply(home, lambda source, target: answers[target])

            self.assertEqual(kept, 1)
            self.assertTrue(keep.is_dir() and not keep.is_symlink())
            self.assertTrue(replace.is_symlink())

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

                result = self.run_script(home)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("refusing to replace non-symlink", result.stderr)
                self.assertFalse((home / ".pi/agent/AGENTS.md").exists())
                if conflict_kind == "file":
                    self.assertEqual(target.read_text(), "keep me")
                else:
                    self.assertEqual((target / "keep-me").read_text(), "keep me")

    def run_script(self, home: Path, *flags: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["HOME"] = str(home)
        return subprocess.run(
            [sys.executable, str(ADD_SYMLINKS), "apply", *flags],
            cwd=REPO_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )


if __name__ == "__main__":
    unittest.main()
