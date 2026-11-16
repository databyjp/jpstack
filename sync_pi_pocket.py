#!/usr/bin/env python3
"""Install, review, update, and roll back the curated Pi Pocket profile.

The active profile points at a committed worktree. Fetching or editing the
source checkout cannot change the instructions or skills a running agent sees.
"""
import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import errno
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import uuid

PROFILE_PATH = "profiles/pi-pocket/profile.json"
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
REVISION = re.compile(r"[0-9a-f]{40,64}\Z")
INCOMPLETE_REVISION = re.compile(r"[0-9a-f]{40,64}\.incomplete-[0-9a-f]{32}\Z")
STATE_FIELDS = {"revision", "skills", "home", "repository", "instructions_sha256"}
UNAVAILABLE_GITFILE = b"jpstack: Git registration unavailable; restore verified metadata before using Git here.\n"


class ProfileError(Exception):
    pass


class Repository:
    def __init__(self, root: Path):
        self.root = root.resolve()

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True, text=True, encoding="utf-8", check=False,
        )
        if result.returncode:
            raise ProfileError(result.stderr.strip() or f"git {' '.join(args)} failed")
        return result.stdout

    def revision(self, value: str) -> str:
        return self.git("rev-parse", "--verify", f"{value}^{{commit}}").strip()

    def read(self, revision: str, name: str) -> str:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or not path.parts or "\\" in name:
            raise ProfileError(f"invalid repository path: {name}")
        entry = self.git("ls-tree", revision, "--", name).strip()
        if not entry.startswith("100644 blob ") and not entry.startswith("100755 blob "):
            raise ProfileError(f"expected a tracked regular file: {name}")
        return self.git("show", f"{revision}:{name}")

    def clean(self) -> None:
        if self.git("status", "--porcelain", "--untracked-files=all").strip():
            raise ProfileError(f"checkout has local changes; commit or preserve them first: {self.root}")

    def ancestor(self, older: str, newer: str) -> bool:
        result = subprocess.run(
            ["git", "-C", str(self.root), "merge-base", "--is-ancestor", older, newer],
            capture_output=True, text=True, check=False,
        )
        if result.returncode not in (0, 1):
            raise ProfileError(result.stderr.strip())
        return result.returncode == 0


def markdown_headings(text: str) -> list[tuple[int, int, str]]:
    """Find ATX headings without treating fenced code as document structure."""
    headings = []
    fence: str | None = None
    offset = 0
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
        elif fence is None:
            heading = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
            if heading:
                headings.append((offset, len(heading.group(1)), heading.group(2)))
        offset += len(line)
    return headings


def section(text: str, title: str, subsections: bool) -> str:
    headings = markdown_headings(text)
    matches = [item for item in headings if item[2] == title]
    if len(matches) != 1:
        raise ProfileError(f"expected exactly one instruction heading {title!r}; found {len(matches)}")
    start, level, _ = matches[0]
    end = next(
        (position for position, depth, _ in headings
         if position > start and (not subsections or depth <= level)),
        len(text),
    )
    return text[start:end].strip()


@dataclass(frozen=True)
class Profile:
    revision: str
    skills: tuple[str, ...]
    instructions: str


def load_profile(repo: Repository, revision: str) -> Profile:
    try:
        manifest = json.loads(repo.read(revision, PROFILE_PATH))
    except json.JSONDecodeError as error:
        raise ProfileError(f"invalid {PROFILE_PATH}: {error}") from error
    if (not isinstance(manifest, dict) or type(manifest.get("version")) is not int
            or manifest["version"] != 1):
        raise ProfileError("unsupported profile version; expected version 1")
    skills = manifest.get("skills")
    if (not isinstance(skills, list) or not skills
            or any(not isinstance(name, str) or not SKILL_NAME.fullmatch(name) for name in skills)
            or len(set(skills)) != len(skills)):
        raise ProfileError("skills must be a nonempty list of unique skill names")
    dependencies = manifest.get("skill_dependencies", {})
    if not isinstance(dependencies, dict):
        raise ProfileError("skill_dependencies must be an object")
    for name, required in dependencies.items():
        if name not in skills or not isinstance(required, list):
            raise ProfileError(f"invalid dependency declaration for {name}")
        for dependency in required:
            if dependency not in skills:
                raise ProfileError(f"{name} requires selected skill {dependency}")
    for name in skills:
        body = repo.read(revision, f"skills/{name}/SKILL.md")
        frontmatter = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|$)", body, re.S)
        if frontmatter is None or not re.search(
            rf"(?m)^name:\s*{re.escape(name)}\s*$", frontmatter.group(1)
        ):
            raise ProfileError(f"skills/{name}/SKILL.md must declare name: {name}")
    sources = manifest.get("instruction_sources")
    if not isinstance(sources, list) or not sources:
        raise ProfileError("instruction_sources must be a nonempty list")
    pieces = ["# Pi Pocket instructions",
              f"<!-- Generated by sync_pi_pocket.py from {revision}. Edit the tracked sources, not this file. -->"]
    for source in sources:
        if not isinstance(source, dict) or not isinstance(source.get("path"), str):
            raise ProfileError("each instruction source needs a repository path")
        text = repo.read(revision, source["path"])
        selections = source.get("sections")
        if selections is None:
            pieces.append(text.strip())
            continue
        if not isinstance(selections, list) or not selections:
            raise ProfileError("sections must be a nonempty list")
        for selection in selections:
            if (not isinstance(selection, dict) or not isinstance(selection.get("heading"), str)
                    or not isinstance(selection.get("subsections", True), bool)):
                raise ProfileError("each section needs a heading and optional boolean subsections")
            pieces.append(section(text, selection["heading"], selection.get("subsections", True)))
    return Profile(revision, tuple(skills), "\n\n".join(pieces) + "\n")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def link_destination(path: Path) -> Path | None:
    if not path.is_symlink():
        return None
    return Path(os.path.abspath(path.parent / path.readlink()))


def replace_link(path: Path, target: Path) -> None:
    temporary = path.with_name(f".{path.name}-{uuid.uuid4().hex}")
    try:
        temporary.symlink_to(target, target_is_directory=target.is_dir())
        temporary.replace(path)
    finally:
        if temporary.is_symlink():
            temporary.unlink()


class Installation:
    def __init__(self, repo: Repository, home: Path):
        self.repo = repo
        self.home = home.resolve()
        self.root = self.home / ".local/share/jpstack/pi-pocket"
        self.current = self.root / "current"
        self.previous = self.root / "previous"
        self.revisions = self.root / "revisions"

    def parent_directories(self) -> None:
        """Refuse redirected parents before writing through a user's dotfiles."""
        for relative in (".local", ".local/share", ".local/share/jpstack",
                         ".local/share/jpstack/pi-pocket", ".local/share/jpstack/pi-pocket/revisions",
                         ".agents", ".agents/skills",
                         ".pi", ".pi/agent"):
            path = self.home / relative
            if path.is_symlink() or (path.exists() and not path.is_dir()):
                raise ProfileError(f"expected a real directory, not a redirected or conflicting path: {path}")

    @staticmethod
    def revision_paths(release: Path) -> None:
        for path in (release, release / "source"):
            if path.is_symlink() or (path.exists() and not path.is_dir()):
                raise ProfileError(f"managed revision must not redirect to another directory: {path}")
        for name in ("AGENTS.md", "profile-state.json", ".worktree-registration.json", "source/.git"):
            path = release / name
            if path.is_symlink() or (path.exists() and not path.is_file()):
                raise ProfileError(f"expected a regular managed file, not a redirected or conflicting path: {path}")

    def revision_state(self, release: Path) -> dict | None:
        """A missing or unfinished completion record marks a recoverable stage."""
        if release.parent != self.revisions or not REVISION.fullmatch(release.name):
            raise ProfileError(f"profile pointer is outside managed revisions: {release}")
        self.revision_paths(release)
        try:
            data = json.loads((release / "profile-state.json").read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
            return None
        except OSError as error:
            raise ProfileError(f"cannot read managed revision {release}: {error}") from error
        if not isinstance(data, dict):
            return None
        # Even an unfinished record must not claim another installation.
        for key, expected in (("revision", release.name), ("home", str(self.home)),
                              ("repository", str(self.repo.root))):
            if key in data and data[key] != expected:
                raise ProfileError(f"invalid managed revision metadata: {release}")
        return data if STATE_FIELDS <= data.keys() else None

    def metadata(self, release: Path) -> dict:
        data = self.revision_state(release)
        if data is None:
            raise ProfileError(f"cannot read managed revision {release}: incomplete profile-state.json")
        if (data.get("revision") != release.name or data.get("home") != str(self.home)
                or data.get("repository") != str(self.repo.root)
                or not isinstance(data.get("skills"), list)
                or any(not isinstance(name, str) or not SKILL_NAME.fullmatch(name) for name in data["skills"])):
            raise ProfileError(f"invalid managed revision metadata: {release}")
        if digest(release / "AGENTS.md") != data.get("instructions_sha256"):
            raise ProfileError("generated AGENTS.md has local edits; preserve them in the tracked sources first")
        snapshot = Repository(release / "source")
        if snapshot.revision("HEAD") != release.name:
            raise ProfileError(f"managed worktree points at a different revision: {release}")
        snapshot.clean()
        return data

    def active(self) -> dict | None:
        target = link_destination(self.current)
        if target is None:
            if self.current.exists():
                raise ProfileError(f"refusing to replace unmanaged profile directory: {self.current}")
            return None
        return self.metadata(target)

    def links(self, skills: list[str] | tuple[str, ...]) -> dict[Path, Path]:
        return {
            self.home / ".pi/agent/AGENTS.md": self.current / "AGENTS.md",
            **{self.home / ".agents/skills" / name: self.current / "source/skills" / name
               for name in skills},
        }

    def preflight(self, profile: Profile, active: dict | None) -> None:
        self.parent_directories()
        names = set(profile.skills) | set(active["skills"] if active else [])
        for path, expected in self.links(sorted(names)).items():
            if path.exists() or path.is_symlink():
                if link_destination(path) != expected:
                    raise ProfileError(f"refusing to replace an unmanaged file, directory, or link: {path}")
        if self.previous.exists() and not self.previous.is_symlink():
            raise ProfileError(f"refusing to replace unmanaged rollback pointer: {self.previous}")
        if self.previous.is_symlink():
            self.metadata(link_destination(self.previous))

    @contextmanager
    def locked(self):
        self.parent_directories()
        self.root.mkdir(parents=True, exist_ok=True)
        lock = self.root / ".sync-lock"
        try:
            lock.mkdir()
        except FileExistsError as error:
            raise ProfileError(f"another sync may be running; inspect {lock} before removing a stale lock") from error
        try:
            yield
        finally:
            lock.rmdir()

    def worktree_admin_root(self) -> Path:
        common = self.repo.git("rev-parse", "--git-common-dir").strip()
        root = Path(os.path.abspath(self.repo.root / common)) / "worktrees"
        if root.is_symlink() or (root.exists() and not root.is_dir()):
            raise ProfileError(f"redirected or conflicting Git worktree registry: {root}")
        return root

    @staticmethod
    def regular_bytes(path: Path) -> bytes:
        if path.is_symlink() or not path.is_file():
            raise ProfileError(f"expected a regular registration file: {path}")
        return path.read_bytes()

    @staticmethod
    def sync_directory(path: Path) -> None:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            try:
                os.fsync(descriptor)
            except OSError as error:
                if error.errno not in (errno.EINVAL, errno.ENOTSUP, errno.EBADF):
                    raise
                print(f"warning: directory fsync is unsupported for {path}; "
                      "atomic replacement remains available, but power-loss durability is not guaranteed",
                      file=sys.stderr)
        finally:
            os.close(descriptor)

    @staticmethod
    def replace_registration(path: Path, content: bytes, release: Path, label: str) -> None:
        """Keep durable original bytes before atomically changing a Git pointer."""
        if path.exists() or path.is_symlink():
            original = Installation.regular_bytes(path)
            if original == content:
                return
            backup = release / f".worktree-{label}-{uuid.uuid4().hex}"
            with backup.open("xb") as stream:
                stream.write(original)
                stream.flush()
                os.fsync(stream.fileno())
            Installation.sync_directory(release)
        temporary = path.with_name(f".jpstack-{path.name}-{uuid.uuid4().hex}.tmp")
        with temporary.open("xb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
        Installation.sync_directory(path.parent)

    def prepare_incomplete_worktree(self, release: Path) -> None:
        """Find registration by its back-pointer, not a possibly stale .git file."""
        source = release / "source"
        expected = str(source / ".git")
        root = self.worktree_admin_root()
        matches = []
        for admin in sorted(root.iterdir()) if root.exists() else []:
            if admin.is_symlink() or not admin.is_dir():
                continue
            try:
                backlink = self.regular_bytes(admin / "gitdir").decode("utf-8").strip()
            except (ProfileError, OSError, UnicodeError):
                continue
            if backlink == expected:
                matches.append(admin)
        if len(matches) > 1:
            raise ProfileError(f"ambiguous worktree registrations for {source}")
        receipt = release / ".worktree-registration.json"
        if matches:
            admin = matches[0]
            identity = uuid.uuid4().hex
            # Bind the retained stage to this allocation of an admin directory,
            # not merely its reusable name or its reusable canonical source path.
            record = json.dumps({"admin": str(admin), "identity": identity}) + "\n"
            self.replace_registration(receipt, record.encode("utf-8"), release, "receipt")
            self.replace_registration(admin / "jpstack-owner", (identity + "\n").encode("utf-8"),
                                      release, "identity")
            source.mkdir(exist_ok=True)
            self.replace_registration(source / ".git", f"gitdir: {admin}\n".encode("utf-8"),
                                      release, "gitfile")
        else:
            if receipt.exists():
                self.replace_registration(receipt, b"{}\n", release, "receipt")
            if (source / ".git").exists():
                print(f"warning: no owned Git registration for {source}; preserving its files without repair",
                      file=sys.stderr)

    def repair_retained_worktree(self, retained: Path, root: Path) -> None:
        source = retained / "source"
        gitfile = source / ".git"
        receipt_path = retained / ".worktree-registration.json"
        if not gitfile.exists() and not receipt_path.exists():
            return
        receipt = json.loads(self.regular_bytes(receipt_path))
        if (not isinstance(receipt, dict) or not isinstance(receipt.get("admin"), str)
                or not isinstance(receipt.get("identity"), str)
                or not re.fullmatch(r"[0-9a-f]{32}", receipt["identity"])):
            raise ProfileError("missing or invalid registration ownership receipt")
        admin = Path(receipt["admin"])
        if admin.parent != root or admin.is_symlink() or not admin.is_dir():
            raise ProfileError("Git administrative directory is missing or not owned by this repository")
        if self.regular_bytes(admin / "jpstack-owner").decode("utf-8").strip() != receipt["identity"]:
            raise ProfileError("Git registration identity is missing or changed; refusing to redirect it")
        backlink = self.regular_bytes(admin / "gitdir").decode("utf-8").strip()
        if backlink == str(gitfile):
            source.mkdir(exist_ok=True)
            self.replace_registration(gitfile, f"gitdir: {admin}\n".encode("utf-8"), retained, "gitfile")
            return
        revision = retained.name.split(".incomplete-", 1)[0]
        original_source = self.revisions / revision / "source"
        # A moved stage can still have its old back-pointer. It is safe to fix
        # only while that old path is absent. A reused admin name is not proof
        # of ownership: it can now belong to a different or newer worktree.
        if (backlink != str(original_source / ".git")
                or original_source.exists() or original_source.is_symlink()):
            raise ProfileError("Git registration belongs to another worktree; refusing to redirect it")
        source.mkdir(exist_ok=True)
        self.replace_registration(gitfile, f"gitdir: {admin}\n".encode("utf-8"), retained, "gitfile")
        self.replace_registration(admin / "gitdir", (str(gitfile) + "\n").encode("utf-8"),
                                  retained, "backlink")

    def repair_incomplete_worktrees(self) -> None:
        # Repeat interrupted moves, but never trust a retained .git file alone.
        root = self.worktree_admin_root()
        for retained in sorted(self.revisions.glob("*.incomplete-*")):
            if not INCOMPLETE_REVISION.fullmatch(retained.name):
                continue
            self.revision_paths(retained)
            try:
                self.repair_retained_worktree(retained, root)
            except (ProfileError, OSError, UnicodeError, json.JSONDecodeError) as error:
                gitfile = retained / "source/.git"
                if gitfile.exists():
                    # A stale pointer can share another worktree's index after
                    # Git reuses an admin name. Preserve it, then stop Git from
                    # following it or searching a parent repository instead.
                    self.replace_registration(gitfile, UNAVAILABLE_GITFILE, retained, "gitfile")
                print(f"warning: cannot repair retained worktree {retained / 'source'}: {error}; "
                      "files remain preserved; Git is unavailable here until verified metadata is restored",
                      file=sys.stderr)

    @staticmethod
    def publish_metadata(release: Path, data: dict) -> None:
        # Only a complete, flushed record can acquire the completion filename.
        # Leave interrupted writes beside the other staged files for recovery.
        temporary = release / f".profile-state-{uuid.uuid4().hex}.tmp"
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(release / "profile-state.json")
        Installation.sync_directory(release)

    def stage(self, profile: Profile) -> Path:
        release = self.revisions / profile.revision
        if release.exists() or release.is_symlink():
            if self.revision_state(release) is not None:
                data = self.metadata(release)
                if data["skills"] != list(profile.skills):
                    raise ProfileError("saved revision has a different skill selection")
                self.repair_incomplete_worktrees()
                return release
            self.repair_incomplete_worktrees()
            self.prepare_incomplete_worktree(release)
            retained = release.with_name(f"{release.name}.incomplete-{uuid.uuid4().hex}")
            release.rename(retained)
            self.sync_directory(self.revisions)
            print(f"preserved incomplete revision: {retained}")
        self.repair_incomplete_worktrees()
        release.mkdir(parents=True)
        self.repo.git("worktree", "add", "--quiet", "--detach", str(release / "source"), profile.revision)
        agents = release / "AGENTS.md"
        agents.write_text(profile.instructions, encoding="utf-8")
        data = {"revision": profile.revision, "skills": list(profile.skills),
                "home": str(self.home), "repository": str(self.repo.root),
                "instructions_sha256": digest(agents)}
        self.publish_metadata(release, data)
        return release

    def activate(self, revision: str, advance_checkout: bool = False) -> None:
        profile = load_profile(self.repo, revision)
        with self.locked():
            active = self.active()
            self.preflight(profile, active)
            if active and active["revision"] == revision:
                print(f"already active: {revision}")
                return
            if advance_checkout:
                if active and not self.repo.ancestor(active["revision"], revision):
                    raise ProfileError("active revision changed; review the update again before applying it")
                self.repo.clean()
                head = self.repo.revision("HEAD")
                if self.repo.ancestor(head, revision):
                    self.repo.git("merge", "--ff-only", revision)
                elif not self.repo.ancestor(revision, head):
                    raise ProfileError("source checkout has diverged; resolve it before updating the profile")
            release = self.stage(profile)
            new_links = self.links(profile.skills)
            old_links = self.links(active["skills"] if active else [])
            created: list[Path] = []
            removed: dict[Path, Path] = {}
            previous_target = link_destination(self.previous)
            try:
                for path, target in new_links.items():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if not path.is_symlink():
                        path.symlink_to(target, target_is_directory=path.name != "AGENTS.md")
                        created.append(path)
                for path, target in old_links.items():
                    if path not in new_links:
                        path.unlink()
                        removed[path] = target
                if active:
                    replace_link(self.previous, self.revisions / active["revision"])
                replace_link(self.current, release)
            except OSError:
                for path, target in removed.items():
                    path.symlink_to(target, target_is_directory=True)
                for path in reversed(created):
                    path.unlink()
                if previous_target is not None:
                    replace_link(self.previous, previous_target)
                elif self.previous.is_symlink():
                    self.previous.unlink()
                raise
            print(f"active revision: {revision}")
            print("skills: " + ", ".join(profile.skills))

    def update(self, approved: str | None) -> None:
        active = self.active()
        if active is None:
            raise ProfileError("install the profile before checking for updates")
        if approved is None:
            self.repo.git("fetch", "origin")
            target = self.repo.revision("refs/remotes/origin/main")
        else:
            if not REVISION.fullmatch(approved):
                raise ProfileError("--apply needs the full reviewed commit hash printed by update")
            target = self.repo.revision(approved)
            if not self.repo.ancestor(target, self.repo.revision("refs/remotes/origin/main")):
                raise ProfileError("reviewed revision is not in the fetched origin/main history")
        if not self.repo.ancestor(active["revision"], target):
            raise ProfileError("origin/main is not a forward update; use rollback for an installed revision")
        profile = load_profile(self.repo, target)
        self.preflight(profile, active)
        if approved is not None:
            self.activate(target, advance_checkout=True)
            return
        if target == active["revision"]:
            print(f"up to date: {target}")
            return
        print(self.repo.git("diff", "--stat", active["revision"], target), end="")
        paths = ["sync_pi_pocket.py", "profiles/pi-pocket", "pi-agent/AGENTS.md", "pi-agent/APPEND_SYSTEM.md",
                 *[f"skills/{name}" for name in sorted(set(active["skills"]) | set(profile.skills))],
                 "references", "tests/writing"]
        print(self.repo.git("diff", active["revision"], target, "--", *paths), end="")
        print(f"\nReviewed revision: {target}")
        print(f"Apply with: python3 sync_pi_pocket.py update --apply {target}")

    def rollback(self) -> None:
        target = link_destination(self.previous)
        if target is None:
            raise ProfileError("no previous installed revision is available")
        self.metadata(target)
        self.activate(target.name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home(), help="Pi Pocket service user's home")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("install", help="install the current committed revision")
    commands.add_parser("status", help="show the active revision and skill selection")
    update = commands.add_parser("update", help="fetch and review changes without activating them")
    update.add_argument("--apply", metavar="COMMIT", help="activate this exact previously reviewed commit")
    commands.add_parser("rollback", help="restore the previously active revision")
    args = parser.parse_args()
    repo = Repository(Path(__file__).resolve().parent)
    installation = Installation(repo, args.home)
    try:
        if args.command == "install":
            repo.clean()
            installation.activate(repo.revision("HEAD"))
        elif args.command == "update":
            installation.update(args.apply)
        elif args.command == "rollback":
            installation.rollback()
        else:
            active = installation.active()
            print(json.dumps(active, indent=2) if active else "not installed")
    except (ProfileError, OSError, KeyError, TypeError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
