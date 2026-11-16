import errno
import json
import os
from pathlib import Path
import shutil
import stat
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

    def retained(self, revision: str) -> Path:
        retained = list((self.state / "revisions").glob(f"{revision}.incomplete-*"))
        self.assertEqual(len(retained), 1)
        return retained[0]

    def assert_registered_worktree(self, source: Path, revision: str) -> None:
        self.assertEqual(self.git(source, "rev-parse", "HEAD"), revision)
        listing = self.git(self.checkout, "worktree", "list", "--porcelain")
        self.assertIn(f"worktree {source}\n", listing)
        git_dir = Path(self.git(source, "rev-parse", "--absolute-git-dir"))
        self.assertEqual((git_dir / "gitdir").read_text().strip(), str(source / ".git"))

    def test_worktree_creation_failure_allows_normal_install_retry(self) -> None:
        repo = sync.Repository(self.checkout)
        installation = sync.Installation(repo, self.home)
        original = repo.git

        def fail_add(*args: str) -> str:
            if args[:2] == ("worktree", "add"):
                raise sync.ProfileError("simulated worktree creation failure")
            return original(*args)

        with patch.object(repo, "git", fail_add):
            with self.assertRaisesRegex(sync.ProfileError, "simulated"):
                installation.activate(self.first)
        release = installation.revisions / self.first
        self.write(release / "notes.txt", "Keep this unfinished attempt")
        self.assertFalse(installation.current.exists())
        result = self.cli("install")
        self.assertIn("preserved incomplete revision:", result.stdout)
        self.assertEqual(self.active(), self.first)
        self.assertEqual((self.retained(self.first) / "notes.txt").read_text(), "Keep this unfinished attempt")

    def test_instruction_write_failure_preserves_edited_worktree_on_retry(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        release = installation.revisions / self.first
        original = Path.write_text

        def fail_instructions(path: Path, text: str, **kwargs) -> int:
            if path == release / "AGENTS.md":
                original(path, "Partial instructions", **kwargs)
                raise OSError("simulated instruction write failure")
            return original(path, text, **kwargs)

        with patch.object(Path, "write_text", fail_instructions):
            with self.assertRaisesRegex(OSError, "simulated"):
                installation.activate(self.first)
        self.write(release / "source/rules.md", "Local tracked edit")
        self.write(release / "source/notes.txt", "Untracked work")
        self.cli("install")
        retained = self.retained(self.first)
        self.assertEqual((retained / "AGENTS.md").read_text(), "Partial instructions")
        self.assertEqual((retained / "source/rules.md").read_text(), "Local tracked edit")
        self.assertEqual((retained / "source/notes.txt").read_text(), "Untracked work")
        self.assert_registered_worktree(retained / "source", self.first)
        self.assertIn("rules.md", self.git(retained / "source", "status", "--porcelain"))
        self.assertIn("Keep changes reviewable", self.agents())
        self.assertEqual(self.git(release / "source", "status", "--porcelain"), "")

    def test_partial_metadata_write_is_not_published_and_retry_preserves_it(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        release = installation.revisions / self.first

        def partial_dump(data, stream, **kwargs) -> None:
            stream.write('{"revision":')
            raise OSError("simulated metadata write failure")

        with patch.object(sync.json, "dump", partial_dump):
            with self.assertRaisesRegex(OSError, "simulated"):
                installation.activate(self.first)
        self.assertFalse((release / "profile-state.json").exists())
        temporary = list(release.glob(".profile-state-*.tmp"))
        self.assertEqual(len(temporary), 1)
        self.cli("install")
        retained = self.retained(self.first)
        self.assertEqual((retained / temporary[0].name).read_text(), '{"revision":')
        self.assert_registered_worktree(retained / "source", self.first)
        self.assertEqual(installation.active()["revision"], self.first)

    def test_metadata_publication_failure_allows_retry(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        release = installation.revisions / self.first
        original = Path.replace

        def fail_publication(path: Path, target: Path) -> Path:
            if target == release / "profile-state.json":
                self.assertFalse(target.exists())
                self.assertEqual(json.loads(path.read_text())["revision"], self.first)
                raise OSError("simulated metadata publication failure")
            return original(path, target)

        with patch.object(Path, "replace", fail_publication):
            with self.assertRaisesRegex(OSError, "simulated"):
                installation.activate(self.first)
        self.assertFalse((release / "profile-state.json").exists())
        self.cli("install")
        self.assertEqual(self.active(), self.first)
        self.assertEqual(len(list(self.retained(self.first).glob(".profile-state-*.tmp"))), 1)

    def test_legacy_partial_metadata_is_preserved_on_normal_retry(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        release = installation.revisions / self.first
        # Cover truncated JSON, a valid but unfinished object, and broken UTF-8.
        for content in (b'{"revision":', b'{"skills": ["one"]}', b'\xff'):
            with self.subTest(content=content):
                with installation.locked():
                    installation.stage(sync.load_profile(installation.repo, self.first))
                (release / "profile-state.json").write_bytes(content)
                with installation.locked():
                    installation.stage(sync.load_profile(installation.repo, self.first))
                retained = [path for path in installation.revisions.glob(f"{self.first}.incomplete-*")
                            if (path / "profile-state.json").read_bytes() == content]
                self.assertEqual(len(retained), 1)
                self.assert_registered_worktree(retained[0] / "source", self.first)
        self.cli("install")
        self.assertEqual(self.active(), self.first)

    def test_interrupted_recovery_repairs_registration_on_next_retry(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        release = installation.revisions / self.first
        with installation.locked():
            installation.stage(sync.load_profile(installation.repo, self.first))
        (release / "profile-state.json").unlink()
        self.write(release / "source/notes.txt", "Retain across interrupted recovery")
        with patch.object(installation, "repair_retained_worktree",
                          side_effect=KeyboardInterrupt("simulated interruption before repair")):
            with self.assertRaisesRegex(KeyboardInterrupt, "simulated"):
                installation.activate(self.first)
        retained = self.retained(self.first)
        self.assertFalse(release.exists())
        self.cli("install")
        self.assertEqual((retained / "source/notes.txt").read_text(), "Retain across interrupted recovery")
        self.assert_registered_worktree(retained / "source", self.first)
        self.assert_registered_worktree(release / "source", self.first)

    def test_registered_stage_with_missing_or_partial_gitfile_allows_retry(self) -> None:
        # Simulate interrupted Git creation: registration exists, but the Git
        # file is absent or partial, or the entire checkout is still absent.
        for mode in ("missing-gitfile", "partial-gitfile", "missing-source"):
            with self.subTest(mode=mode):
                self.home = self.root / mode
                self.home.mkdir()
                self.state = self.home / ".local/share/jpstack/pi-pocket"
                installation = sync.Installation(sync.Repository(self.checkout), self.home)
                with installation.locked():
                    release = installation.stage(sync.load_profile(installation.repo, self.first))
                (release / "profile-state.json").unlink()
                if mode == "missing-source":
                    shutil.rmtree(release / "source")
                else:
                    self.write(release / "source/notes.txt", mode)
                    if mode == "missing-gitfile":
                        (release / "source/.git").unlink()
                    else:
                        (release / "source/.git").write_bytes(b"gitdir: interrupted")
                self.cli("install")
                self.assertEqual(self.active(), self.first)
                retained = self.retained(self.first)
                self.assert_registered_worktree(retained / "source", self.first)
                if mode != "missing-source":
                    self.assertEqual((retained / "source/notes.txt").read_text(), mode)
                if mode == "partial-gitfile":
                    backup, = retained.glob(".worktree-gitfile-*")
                    self.assertEqual(backup.read_bytes(), b"gitdir: interrupted")

    def test_damaged_retained_git_metadata_warns_without_blocking_updates(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        with installation.locked():
            release = installation.stage(sync.load_profile(installation.repo, self.first))
        (release / "profile-state.json").unlink()
        self.write(release / "source/notes.txt", "Preserve despite lost Git metadata")
        self.cli("install")
        retained = self.retained(self.first)
        admin = Path(self.git(retained / "source", "rev-parse", "--absolute-git-dir"))
        # Damage only this temporary fixture's retained registration.
        shutil.rmtree(admin)
        second = self.change_policy()
        self.cli("update")
        result = self.cli("update", "--apply", second)
        self.assertIn("warning: cannot repair retained worktree", result.stderr)
        self.assertEqual(self.active(), second)
        self.assertEqual((retained / "source/notes.txt").read_text(), "Preserve despite lost Git metadata")
        self.cli("rollback")
        self.assertEqual(self.active(), self.first)

    def test_reused_git_admin_name_is_not_reclaimed_by_retained_worktree(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        with installation.locked():
            release = installation.stage(sync.load_profile(installation.repo, self.first))
        (release / "profile-state.json").unlink()
        self.write(release / "source/notes.txt", "Old retained work")
        self.cli("install")
        retained = self.retained(self.first)
        freed_admin = Path(self.git(retained / "source", "rev-parse", "--absolute-git-dir"))
        shutil.rmtree(freed_admin)
        second = self.change_policy("Second policy")
        self.cli("update")
        self.cli("update", "--apply", second)
        second_source = installation.revisions / second / "source"
        reused_admin = Path(self.git(second_source, "rev-parse", "--absolute-git-dir"))
        self.assertEqual(reused_admin, freed_admin)
        # Reuse of a complete revision must not let the old .git file redirect
        # this newly allocated registration back to its retained directory.
        with installation.locked():
            installation.stage(sync.load_profile(installation.repo, second))
        self.assert_registered_worktree(second_source, second)
        self.assertEqual((retained / "source/notes.txt").read_text(), "Old retained work")
        original_index = (reused_admin / "index").read_bytes()
        for arguments in (("rev-parse", "HEAD"), ("add", "-A")):
            result = subprocess.run(["git", "-C", str(retained / "source"), *arguments],
                                    env=self.environment, capture_output=True, text=True, check=False)
            self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertEqual((reused_admin / "index").read_bytes(), original_index)
        self.assertEqual((retained / "source/.git").read_bytes(), sync.UNAVAILABLE_GITFILE)
        self.assertTrue(any(path.read_bytes().startswith(b"gitdir: ")
                            for path in retained.glob(".worktree-gitfile-*")))
        # Recovery of another partial stage must not run broad Git repair either.
        third = self.change_policy("Third policy")
        self.cli("update")
        with patch.object(sync.Installation, "publish_metadata", side_effect=OSError("simulated")):
            with self.assertRaisesRegex(OSError, "simulated"):
                installation.update(third)
        self.cli("update", "--apply", third)
        self.assert_registered_worktree(second_source, second)
        self.assertEqual(self.active(), third)
        self.cli("rollback")
        self.assertEqual(self.active(), second)
        self.assert_registered_worktree(second_source, second)

    def test_safety_gitfile_write_failure_fails_closed_and_allows_later_retry(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        with installation.locked():
            release = installation.stage(sync.load_profile(installation.repo, self.first))
        (release / "profile-state.json").unlink()
        self.cli("install")
        original_agents = self.agents()
        retained = self.retained(self.first)
        gitfile = retained / "source/.git"
        original_gitfile = gitfile.read_bytes()
        admin = Path(self.git(retained / "source", "rev-parse", "--absolute-git-dir"))
        shutil.rmtree(admin)
        second = self.change_policy()
        self.cli("update")
        original_replace = sync.Installation.replace_registration

        def no_space(path: Path, content: bytes, release: Path, label: str) -> None:
            if path == gitfile:
                raise OSError(errno.ENOSPC, "simulated safety-file write failure")
            original_replace(path, content, release, label)

        with patch.object(sync.Installation, "replace_registration", staticmethod(no_space)):
            with self.assertRaisesRegex(OSError, "simulated safety-file"):
                installation.update(second)
        self.assertEqual(self.active(), self.first)
        self.assertEqual(self.agents(), original_agents)
        self.assertEqual(gitfile.read_bytes(), original_gitfile)
        self.assertFalse((installation.revisions / second).exists())
        self.cli("update", "--apply", second)
        self.assertEqual(self.active(), second)
        self.assertEqual(gitfile.read_bytes(), sync.UNAVAILABLE_GITFILE)

    def test_unsupported_directory_fsync_does_not_block_installation(self) -> None:
        original_fsync = os.fsync
        for error_number in (errno.EINVAL, errno.ENOTSUP, errno.EBADF):
            with self.subTest(error_number=error_number):
                home = self.root / f"unsupported-fsync-{error_number}"
                installation = sync.Installation(sync.Repository(self.checkout), home)

                def unsupported(descriptor: int) -> None:
                    if stat.S_ISDIR(os.fstat(descriptor).st_mode):
                        raise OSError(error_number, "directory fsync unsupported")
                    original_fsync(descriptor)

                with patch.object(sync.os, "fsync", unsupported):
                    installation.activate(self.first)
                self.assertEqual(installation.active()["revision"], self.first)

    def test_restored_retained_admin_metadata_recovers_disabled_gitfile(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        with installation.locked():
            release = installation.stage(sync.load_profile(installation.repo, self.first))
        (release / "profile-state.json").unlink()
        self.cli("install")
        retained = self.retained(self.first)
        admin = Path(self.git(retained / "source", "rev-parse", "--absolute-git-dir"))
        saved = self.root / "saved-admin"
        admin.rename(saved)
        with installation.locked():
            installation.repair_incomplete_worktrees()
        self.assertEqual((retained / "source/.git").read_bytes(), sync.UNAVAILABLE_GITFILE)
        saved.rename(admin)
        with installation.locked():
            installation.repair_incomplete_worktrees()
        self.assert_registered_worktree(retained / "source", self.first)

    def test_changed_admin_identity_prevents_repair_of_an_absent_old_path(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        with installation.locked():
            release = installation.stage(sync.load_profile(installation.repo, self.first))
        (release / "profile-state.json").unlink()
        self.cli("install")
        retained = self.retained(self.first)
        admin = Path(self.git(retained / "source", "rev-parse", "--absolute-git-dir"))
        # Simulate reuse at the exact same canonical path, with no source yet.
        # Even the old back-pointer alone cannot prove allocation ownership.
        (admin / "jpstack-owner").write_text("changed allocation\n")
        old_backlink = str(release / "source/.git") + "\n"
        (admin / "gitdir").write_text(old_backlink)
        saved = self.root / "saved-complete-release"
        release.rename(saved)
        try:
            with self.assertRaisesRegex(sync.ProfileError, "identity is missing or changed"):
                installation.repair_retained_worktree(retained, installation.worktree_admin_root())
            self.assertEqual((admin / "gitdir").read_text(), old_backlink)
        finally:
            saved.rename(release)

    def test_registration_rewrite_flushes_backup_before_atomic_replacement(self) -> None:
        target = self.root / "pointer"
        target.write_bytes(b"original registration\n")
        original_replace = Path.replace
        with patch.object(sync.os, "fsync", wraps=os.fsync) as fsync:
            def checked_replace(path: Path, destination: Path) -> Path:
                self.assertEqual(destination, target)
                backup, = self.root.glob(".worktree-test-*")
                self.assertEqual(backup.read_bytes(), b"original registration\n")
                self.assertEqual(target.read_bytes(), b"original registration\n")
                # Backup file, backup directory, and replacement file are
                # synced before the replacement; its directory follows it.
                self.assertEqual(fsync.call_count, 3)
                return original_replace(path, destination)

            with patch.object(Path, "replace", checked_replace):
                sync.Installation.replace_registration(target, b"new registration\n", self.root, "test")
            self.assertEqual(fsync.call_count, 4)
        self.assertEqual(target.read_bytes(), b"new registration\n")

    def test_failed_update_staging_preserves_active_profile_and_allows_apply_retry(self) -> None:
        self.cli("install")
        original_agents = self.agents()
        original_skill = (self.home / ".agents/skills/one/SKILL.md").read_text()
        self.manifest["skills"] = ["two"]
        self.write_manifest()
        second = self.change_policy("Second policy")
        self.cli("update")
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        release = installation.revisions / second
        original_git = installation.repo.git

        def fail_add(*args: str) -> str:
            if args[:2] == ("worktree", "add"):
                raise sync.ProfileError("simulated update worktree failure")
            return original_git(*args)

        def partial_dump(data, stream, **kwargs) -> None:
            stream.write("{")
            raise OSError("simulated update metadata failure")

        for failure in (patch.object(installation.repo, "git", fail_add),
                        patch.object(sync.json, "dump", partial_dump)):
            with failure:
                with self.assertRaisesRegex((sync.ProfileError, OSError), "simulated"):
                    installation.update(second)
            self.assertEqual(self.active(), self.first)
            self.assertEqual(self.agents(), original_agents)
            self.assertEqual((self.home / ".agents/skills/one/SKILL.md").read_text(), original_skill)
            self.assertFalse((self.home / ".agents/skills/two").is_symlink())
            self.assertFalse((self.state / "previous").is_symlink())
        self.write(release / "source/notes.txt", "Keep failed update work")
        self.cli("update", "--apply", second)
        self.assertEqual(self.active(), second)
        self.assertIn("Second policy", self.agents())
        self.assertFalse((self.home / ".agents/skills/one").is_symlink())
        self.assertTrue((self.home / ".agents/skills/two").is_symlink())
        retained = [path for path in installation.revisions.glob(f"{second}.incomplete-*")
                    if (path / "source/notes.txt").exists()]
        self.assertEqual(len(retained), 1)
        self.assert_registered_worktree(retained[0] / "source", second)
        self.cli("rollback")
        self.assertEqual(self.active(), self.first)
        self.assertEqual(self.agents(), original_agents)

    def test_completed_inactive_revision_still_rejects_local_edits(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        with installation.locked():
            release = installation.stage(sync.load_profile(installation.repo, self.first))
        for relative, expected in (("AGENTS.md", "local edits"), ("source/rules.md", "local changes")):
            with self.subTest(relative=relative):
                path = release / relative
                original = path.read_text()
                self.write(path, "Keep local edits")
                self.assertIn(expected, self.cli("install", success=False).stderr)
                self.assertEqual(path.read_text(), "Keep local edits")
                self.assertEqual(list(installation.revisions.glob("*.incomplete-*")), [])
                self.write(path, original)
        self.cli("install")
        self.assertEqual(self.active(), self.first)

    def test_completed_revision_with_wrong_ownership_is_not_recovered(self) -> None:
        installation = sync.Installation(sync.Repository(self.checkout), self.home)
        with installation.locked():
            release = installation.stage(sync.load_profile(installation.repo, self.first))
        path = release / "profile-state.json"
        data = json.loads(path.read_text())
        data["home"] = str(self.root / "someone-else")
        self.write(path, json.dumps(data))
        self.assertIn("invalid managed revision metadata", self.cli("install", success=False).stderr)
        self.assertEqual(json.loads(path.read_text()), data)
        self.assertEqual(list(installation.revisions.glob("*.incomplete-*")), [])

    def test_incomplete_revision_symlink_conflicts_are_not_followed_or_moved(self) -> None:
        release = self.state / "revisions" / self.first
        release.parent.mkdir(parents=True)
        outside = self.root / "outside"
        outside.mkdir()
        self.write(outside / "notes.txt", "Untouched")
        for relative in ("", "source", "AGENTS.md", "profile-state.json", ".worktree-registration.json", "source/.git"):
            with self.subTest(relative=relative):
                path = release / relative if relative else release
                path.parent.mkdir(parents=True, exist_ok=True)
                path.symlink_to(outside)
                self.assertIn("redirect", self.cli("install", success=False).stderr)
                self.assertTrue(path.is_symlink())
                self.assertEqual((outside / "notes.txt").read_text(), "Untouched")
                self.assertEqual(list(release.parent.glob("*.incomplete-*")), [])
                path.unlink()

    def test_dangling_revision_symlink_is_rejected(self) -> None:
        release = self.state / "revisions" / self.first
        release.parent.mkdir(parents=True)
        release.symlink_to(self.root / "missing")
        self.assertIn("redirect", self.cli("install", success=False).stderr)
        self.assertTrue(release.is_symlink())

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
        self.assertIn("## Visual delivery in Pi Pocket", profile.instructions)
        self.assertIn("overrides `show-me`'s desktop `Bash(open", profile.instructions)
        self.assertIn("Check which tools the session exposes", profile.instructions)
        self.assertIn("Prefer `artifact` when available", profile.instructions)
        self.assertIn("local file's `path`", profile.instructions)
        self.assertIn("`browser` tool is available", profile.instructions)
        self.assertIn("`navigate` action with `url`", profile.instructions)
        self.assertIn("Markdown diagram, fenced code-shape sketch, or focused `diff` directly in chat", profile.instructions)
        self.assertIn("Do not enable extensions", profile.instructions)
        self.assertIn("Bash(open path/to/show-me-{description}.html)",
                      (REPO_ROOT / "skills/show-me/SKILL.md").read_text())
        self.assertNotIn("Sessions run inside a nono sandbox", profile.instructions)
        self.assertNotIn("load `gated-development`", profile.instructions)
        self.assertNotIn("Host browsers cannot run", profile.instructions)
        self.git(self.seed, "push", "-q", "origin", "main")
        self.git(self.checkout, "pull", "--ff-only")
        self.cli("install")
        self.assertEqual(self.agents(), profile.instructions)
        self.assertEqual({path.name for path in (self.home / ".agents/skills").iterdir()}, set(profile.skills))


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
