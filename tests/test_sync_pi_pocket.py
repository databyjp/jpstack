import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
import sync_pi_pocket as sync


def setUpModule() -> None:
    with tempfile.TemporaryDirectory() as directory:
        try:
            (Path(directory) / "link").symlink_to(Path(directory) / "target")
        except OSError as error:
            raise unittest.SkipTest(f"filesystem symlinks unavailable: {error}") from error


class PocketProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.seed = self.root / "seed"
        self.seed.mkdir()
        self.environment = os.environ.copy()
        self.environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
                                GIT_TERMINAL_PROMPT="0")
        self.git(self.seed, "init", "-q", "-b", "main")
        self.git(self.seed, "config", "user.name", "Profile Tests")
        self.git(self.seed, "config", "user.email", "tests@example.invalid")
        shutil.copy(REPO_ROOT / "sync_pi_pocket.py", self.seed / "sync_pi_pocket.py")
        self.write(self.seed / "rules.md", "# Policy\nKeep changes reviewable.\n")
        for name in ("one", "two"):
            self.write(self.seed / f"skills/{name}/SKILL.md",
                       f"---\nname: {name}\ndescription: Test skill.\n---\n\n{name} version one\n")
        self.manifest = {"version": 1, "skills": ["one"], "skill_dependencies": {},
                         "instruction_sources": [{"path": "rules.md", "sections": [{"heading": "Policy"}]}]}
        self.write_manifest()
        self.first = self.commit("Initial profile")
        self.remote = self.root / "origin.git"
        self.git(self.root, "clone", "--bare", "-q", str(self.seed), str(self.remote))
        self.git(self.seed, "remote", "add", "origin", str(self.remote))
        self.checkout = self.root / "checkout"
        self.git(self.root, "clone", "-q", str(self.remote), str(self.checkout))
        self.home = self.root / "home"
        self.home.mkdir()
        self.state = self.home / ".local/share/jpstack/pi-pocket"

    def git(self, directory: Path, *arguments: str) -> str:
        result = subprocess.run(["git", "-C", str(directory), *arguments],
                                env=self.environment, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    @staticmethod
    def write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_manifest(self) -> None:
        self.write(self.seed / sync.PROFILE_PATH, json.dumps(self.manifest, indent=2) + "\n")

    def commit(self, message: str) -> str:
        self.git(self.seed, "add", ".")
        self.git(self.seed, "commit", "-q", "-m", message)
        return self.git(self.seed, "rev-parse", "HEAD")

    def publish(self, message: str = "Update profile") -> str:
        revision = self.commit(message)
        self.git(self.seed, "push", "-q", "origin", "main")
        return revision

    def cli(self, *arguments: str, success: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run([sys.executable, str(self.checkout / "sync_pi_pocket.py"),
                                 "--home", str(self.home), *arguments],
                                env=self.environment, capture_output=True, text=True, check=False)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, result.stdout)
        return result

    def active(self) -> str:
        return (self.state / "current").resolve().name

    def agents(self) -> str:
        return (self.home / ".pi/agent/AGENTS.md").read_text(encoding="utf-8")

    def change_policy(self, text: str = "New policy") -> str:
        self.write(self.seed / "rules.md", f"# Policy\n{text}\n")
        return self.publish()

    def test_install_exposes_only_selected_skills_and_preserves_other_configuration(self) -> None:
        self.write(self.home / ".pi/agent/settings.json", '{"defaultProvider":"device-specific"}')
        self.write(self.home / ".pi/agent/auth.json", '{"test":"leave alone"}')
        self.write(self.home / ".agents/skills/local/SKILL.md", "Local skill")
        self.cli("install")
        self.assertEqual(self.active(), self.first)
        self.assertTrue((self.home / ".agents/skills/one").is_symlink())
        self.assertFalse((self.home / ".agents/skills/two").exists())
        self.assertEqual((self.home / ".agents/skills/local/SKILL.md").read_text(), "Local skill")
        self.assertEqual((self.home / ".pi/agent/settings.json").read_text(), '{"defaultProvider":"device-specific"}')
        self.assertEqual((self.home / ".pi/agent/auth.json").read_text(), '{"test":"leave alone"}')
        self.assertFalse((self.home / ".pi/agent/extensions").exists())
        self.assertFalse((self.home / ".claude").exists())
        self.assertIn("Keep changes reviewable.", self.agents())

    def test_install_is_idempotent(self) -> None:
        self.cli("install")
        self.assertIn("already active", self.cli("install").stdout)
        self.assertFalse((self.state / "previous").exists())

    def test_conflicting_agents_file_is_preserved_before_any_skill_links_are_created(self) -> None:
        self.write(self.home / ".pi/agent/AGENTS.md", "Personal instructions")
        result = self.cli("install", success=False)
        self.assertIn("unmanaged", result.stderr)
        self.assertEqual((self.home / ".pi/agent/AGENTS.md").read_text(), "Personal instructions")
        self.assertFalse((self.home / ".agents/skills/one").is_symlink())

    def test_whole_directory_skill_symlink_is_not_followed(self) -> None:
        outside = self.root / "other-skills"
        outside.mkdir()
        (self.home / ".agents").mkdir()
        (self.home / ".agents/skills").symlink_to(outside, target_is_directory=True)
        self.assertIn("redirected", self.cli("install", success=False).stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_fetch_and_source_checkout_updates_do_not_change_active_skills(self) -> None:
        self.cli("install")
        self.write(self.seed / "skills/one/SKILL.md", "---\nname: one\n---\nChanged skill\n")
        second = self.publish()
        result = self.cli("update")
        self.assertIn(second, result.stdout)
        self.assertEqual(self.active(), self.first)
        self.git(self.checkout, "merge", "--ff-only", "origin/main")
        self.assertIn("version one", (self.home / ".agents/skills/one/SKILL.md").read_text())
        self.assertEqual(self.active(), self.first)

    def test_apply_activates_exact_reviewed_commit_even_if_origin_has_advanced(self) -> None:
        self.cli("install")
        second = self.change_policy("Reviewed policy")
        self.cli("update")
        third = self.change_policy("Not applied yet")
        self.cli("update")
        self.cli("update", "--apply", second)
        self.assertEqual(self.active(), second)
        self.assertIn("Reviewed policy", self.agents())
        self.assertNotIn("Not applied yet", self.agents())
        self.assertNotEqual(self.active(), third)

    def test_apply_removes_only_previously_managed_skills(self) -> None:
        self.cli("install")
        self.write(self.home / ".agents/skills/local/SKILL.md", "Keep this")
        self.manifest["skills"] = ["two"]
        self.write_manifest()
        second = self.publish()
        self.cli("update")
        self.cli("update", "--apply", second)
        self.assertFalse((self.home / ".agents/skills/one").is_symlink())
        self.assertTrue((self.home / ".agents/skills/two").is_symlink())
        self.assertEqual((self.home / ".agents/skills/local/SKILL.md").read_text(), "Keep this")

    def test_generated_instruction_edits_are_not_overwritten(self) -> None:
        self.cli("install")
        self.write(self.home / ".pi/agent/AGENTS.md", "Local edit")
        self.change_policy()
        result = self.cli("update", success=False)
        self.assertIn("local edits", result.stderr)
        self.assertEqual((self.home / ".pi/agent/AGENTS.md").read_text(), "Local edit")
        self.assertEqual(self.active(), self.first)

    def test_forward_update_is_rechecked_under_the_installation_lock(self) -> None:
        self.cli("install")
        second = self.change_policy("Reviewed second policy")
        third = self.change_policy("Already active third policy")
        self.cli("update")
        self.cli("update", "--apply", third)
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        with patch.dict(os.environ, self.environment):
            with self.assertRaisesRegex(sync.ProfileError, "active revision changed"):
                installation.activate(second, advance_checkout=True)
        self.assertEqual(self.active(), third)

    def test_edited_skill_snapshot_is_not_overwritten(self) -> None:
        self.cli("install")
        self.write(self.home / ".agents/skills/one/SKILL.md", "Local skill edit")
        self.change_policy()
        self.assertIn("local changes", self.cli("update", success=False).stderr)
        self.assertEqual((self.home / ".agents/skills/one/SKILL.md").read_text(), "Local skill edit")

    def test_renamed_source_heading_stops_update_without_activation(self) -> None:
        self.cli("install")
        self.write(self.seed / "rules.md", "# Renamed policy\nNew instructions\n")
        self.publish()
        result = self.cli("update", success=False)
        self.assertIn("exactly one instruction heading", result.stderr)
        self.assertEqual(self.active(), self.first)

    def test_missing_declared_dependency_is_rejected(self) -> None:
        self.manifest["skill_dependencies"] = {"one": ["two"]}
        self.write_manifest()
        self.publish()
        self.git(self.checkout, "pull", "--ff-only")
        self.assertIn("requires selected skill two", self.cli("install", success=False).stderr)
        self.assertFalse((self.state / "current").exists())

    def test_selected_skill_must_exist_and_declare_its_name(self) -> None:
        self.write(self.seed / "skills/one/SKILL.md", "---\nname: another-name\n---\n")
        self.publish()
        self.git(self.checkout, "pull", "--ff-only")
        self.assertIn("must declare name: one", self.cli("install", success=False).stderr)

    def test_uncommitted_checkout_is_rejected_for_initial_install(self) -> None:
        self.write(self.checkout / "rules.md", "Uncommitted policy")
        self.assertIn("local changes", self.cli("install", success=False).stderr)
        self.assertFalse((self.state / "current").exists())

    def test_apply_requires_a_full_commit_hash(self) -> None:
        self.cli("install")
        self.assertIn("full reviewed commit hash", self.cli("update", "--apply", "origin/main", success=False).stderr)

    def test_rollback_restores_instructions_and_skill_selection_without_fetching(self) -> None:
        self.cli("install")
        self.manifest["skills"] = ["two"]
        self.write_manifest()
        second = self.change_policy("Second policy")
        self.cli("update")
        self.cli("update", "--apply", second)
        self.git(self.checkout, "remote", "set-url", "origin", str(self.root / "missing-remote"))
        self.cli("rollback")
        self.assertEqual(self.active(), self.first)
        self.assertIn("Keep changes reviewable", self.agents())
        self.assertTrue((self.home / ".agents/skills/one").is_symlink())
        self.assertFalse((self.home / ".agents/skills/two").is_symlink())
        self.cli("rollback")
        self.assertEqual(self.active(), second)

    def test_failed_pointer_switch_restores_links_and_existing_rollback(self) -> None:
        self.cli("install")
        second = self.change_policy("Second active policy")
        self.cli("update")
        self.cli("update", "--apply", second)
        self.manifest["skills"] = ["two"]
        self.write_manifest()
        third = self.publish()
        self.git(self.checkout, "fetch", "origin")
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        original = sync.replace_link

        def fail_current(path: Path, target: Path) -> None:
            if path == installation.current:
                raise OSError("simulated pointer replacement failure")
            original(path, target)

        with patch.dict(os.environ, self.environment), patch.object(sync, "replace_link", fail_current):
            with self.assertRaisesRegex(OSError, "simulated"):
                installation.activate(third)
        self.assertEqual(self.active(), second)
        self.assertEqual((self.state / "previous").resolve().name, self.first)
        self.assertTrue((self.home / ".agents/skills/one").is_symlink())
        self.assertFalse((self.home / ".agents/skills/two").is_symlink())
        self.cli("rollback")
        self.assertEqual(self.active(), self.first)

    def test_lock_refuses_concurrent_installation(self) -> None:
        (self.state / ".sync-lock").mkdir(parents=True)
        self.assertIn("another sync", self.cli("install", success=False).stderr)

    def test_default_profile_uses_portable_shared_sections_and_selected_dependencies(self) -> None:
        manifest = json.loads((REPO_ROOT / sync.PROFILE_PATH).read_text())
        for name in manifest["skills"]:
            shutil.copytree(REPO_ROOT / "skills" / name, self.seed / "skills" / name, dirs_exist_ok=True)
        for source in manifest["instruction_sources"]:
            self.write(self.seed / source["path"], (REPO_ROOT / source["path"]).read_text(encoding="utf-8"))
        self.write(self.seed / sync.PROFILE_PATH, json.dumps(manifest))
        revision = self.commit("Real Pocket profile")
        profile = sync.load_profile(sync.Repository(self.seed), revision)
        self.assertEqual(set(profile.skills), {"unslop", "code-documentation", "jp-coding-preferences-reporting",
                                               "show-me", "grill-me", "grilling"})
        self.assertIn("Do NOT commit changes unless specifically asked", profile.instructions)
        self.assertIn("## Writing style", profile.instructions)
        self.assertIn("## Editing discipline", profile.instructions)
        self.assertIn("## Code style", profile.instructions)
        self.assertNotIn("Sessions run inside a nono sandbox", profile.instructions)
        self.assertNotIn("load `gated-development`", profile.instructions)
        self.assertNotIn("Host browsers cannot run", profile.instructions)


class MarkdownSectionTests(unittest.TestCase):
    def test_excludes_child_workflow_when_only_parent_preferences_are_selected(self) -> None:
        source = "# Preferences\nPortable.\n## Workflow\nSpecial tooling.\n# Other\nOther.\n"
        self.assertEqual(sync.section(source, "Preferences", False), "# Preferences\nPortable.")
        self.assertIn("Special tooling", sync.section(source, "Preferences", True))

    def test_ignores_headings_inside_code_fences(self) -> None:
        source = "# Policy\n```python\n# Not a heading\n```\nKeep this.\n# End\n"
        self.assertIn("Keep this", sync.section(source, "Policy", True))

    def test_duplicate_heading_is_rejected(self) -> None:
        with self.assertRaisesRegex(sync.ProfileError, "found 2"):
            sync.section("# Policy\nOne.\n# Policy\nTwo.\n", "Policy", True)


if __name__ == "__main__":
    unittest.main()
