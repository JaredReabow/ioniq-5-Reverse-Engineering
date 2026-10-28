"""Self-tests for the read-only Ioniq 5 research validation harness.

Fixtures live in temporary directories. The Council test drives the real
checker against a deliberately unsafe packet; the rest inject command output so
Git scope, redaction, and history-state rules can be tested without touching the
repository.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_all  # noqa: E402
from harness import artifacts, common, council, docs, gitscope, jsoncheck, ledger, privacy  # noqa: E402


def write_json(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


def fake_runner(rules):
    """Build a command runner from (predicate, result) rules."""

    def run(argv, cwd=None):
        for predicate, result in rules:
            if predicate(argv):
                return {
                    "argv": list(argv),
                    "exit_status": result.get("exit_status", 0),
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "error": result.get("error"),
                }
        return {
            "argv": list(argv),
            "exit_status": 1,
            "stdout": "",
            "stderr": "unexpected command",
            "error": None,
        }

    return run


def git_config_block(entries):
    """Render ``(key, value)`` pairs as ``git config --list -z`` output."""
    return "".join(f"{key}\n{value}\u0000" for key, value in entries)


def git_runner(
    *,
    status_stdout="",
    origin=None,
    branch="main",
    top_ok=True,
    config=None,
    status_ok=True,
    config_ok=True,
):
    """Inject Git command output, including a full config snapshot."""
    entries = []
    if origin:
        entries.append(("remote.origin.url", origin))
    entries_source = (
        config.items() if isinstance(config, dict) else (config or [])
    )
    for key, value in entries_source:
        values = value if isinstance(value, (list, tuple)) else [value]
        for item in values:
            entries.append((key, item))
    config_stdout = git_config_block(entries) if config_ok else ""
    rules = [
        (
            lambda argv: "--show-toplevel" in argv,
            {"exit_status": 0 if top_ok else 128, "stdout": "/tmp/repo\n"},
        ),
        (
            lambda argv: "--porcelain=v1" in argv,
            {
                "exit_status": 0 if status_ok else 128,
                "stdout": status_stdout if status_ok else "",
                "stderr": "" if status_ok else "fatal: index unreadable",
            },
        ),
        (
            lambda argv: "config" in argv and "--list" in argv,
            {
                "exit_status": 0 if config_ok else 128,
                "stdout": config_stdout,
                "stderr": "" if config_ok else "fatal: bad config",
            },
        ),
        (lambda argv: "symbolic-ref" in argv, {"exit_status": 0, "stdout": branch + "\n"}),
        (lambda argv: "--abbrev-ref" in argv, {"exit_status": 0, "stdout": branch + "\n"}),
    ]
    return fake_runner(rules)


class ArtifactTests(unittest.TestCase):
    def test_stale_hash_reports_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evidence").mkdir()
            (root / "evidence" / "a.md").write_text("changed\n", encoding="utf-8")
            write_json(
                root / "research-ledger.json",
                {
                    "schema_version": 1,
                    "artifacts": [
                        {
                            "id": "ART-A",
                            "task_id": "T1",
                            "path": "evidence/a.md",
                            "sha256": "0" * 64,
                            "kind": "research-note",
                        }
                    ],
                },
            )
            result = artifacts.artifacts_check(root / "research-ledger.json", root)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            self.assertEqual(result["details"]["entries"][0]["state"], "stale")
            self.assertEqual(result["details"]["counts"]["stale"], 1)

    def test_missing_and_unsafe_paths_are_distinct(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(
                root / "research-ledger.json",
                {
                    "schema_version": 1,
                    "artifacts": [
                        {"id": "A", "path": "evidence/gone.md", "sha256": "a" * 64},
                        {"id": "B", "path": "../escape.md", "sha256": "b" * 64},
                    ],
                },
            )
            result = artifacts.artifacts_check(root / "research-ledger.json", root)
            states = [entry["state"] for entry in result["details"]["entries"]]
            self.assertEqual(states, ["missing", "unsafe"])
            self.assertEqual(result["status"], common.STATUS_FAIL)


class CouncilTests(unittest.TestCase):
    def _package(self, root: Path, packet: object) -> Path:
        directory = root / "council" / "review-batch-1"
        directory.mkdir(parents=True)
        if isinstance(packet, str):
            (directory / "council-packet.json").write_text(packet, encoding="utf-8")
        else:
            write_json(directory / "council-packet.json", packet)
        return directory

    def test_unsafe_frozen_artifact_path_fails(self):
        checker = Path(council.DEFAULT_CHECKER)
        if not checker.is_file():
            self.skipTest("council checker not installed")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet = {
                "schema_version": 1,
                "package": {
                    "id": "pkg",
                    "version": "v1",
                    "fingerprint": "a" * 64,
                    "produced_by": [],
                    "artifacts": [{"path": "../escape.md", "sha256": "b" * 64}],
                    "task_manifest": "../escape.md",
                },
                "requirements": [{"id": "R1", "text": "requirement"}],
                "required_checks": [],
                "panel": [],
                "integration": {},
                "rounds": [],
                "initial_reports": [],
                "findings": [],
                "reviewer_finals": [],
            }
            self._package(root, packet)
            result = council.council_check_packages(root, checker_path=checker)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            record = result["details"]["packages"][0]
            self.assertIn("artifact_path_unsafe", record["problem_codes"])
            self.assertIs(record["package_verified"], False)

    def test_historical_blocked_with_verified_bytes_is_info(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._package(root, {})
            report = {
                "outcome": "BLOCKED",
                "package_verified": True,
                "problems": ["final_missing_reviewer: reviewer_finals: no verdict"],
                "package_fingerprint": "c" * 64,
                "reviewer_verdicts": {"seat-a": "BLOCKED"},
            }
            runner = fake_runner(
                [(
                    lambda argv: "council-packet.json" in " ".join(argv),
                    {"exit_status": 1, "stdout": json.dumps(report)},
                )]
            )
            result = council.council_check_packages(root, runner=runner)
            self.assertEqual(result["status"], common.STATUS_INFO)
            self.assertEqual(result["details"]["packages"][0]["outcome"], "BLOCKED")

    def test_unusable_packet_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._package(root, "{not json")
            runner = fake_runner(
                [(
                    lambda argv: "council-packet.json" in " ".join(argv),
                    {"exit_status": 2, "stderr": "error: unsupported schema_version"},
                )]
            )
            result = council.council_check_packages(root, runner=runner)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            self.assertIn("unusable packet", result["details"]["packages"][0]["summary"])

    def test_fingerprint_mismatch_fails_even_when_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._package(root, {})
            report = {
                "outcome": "BLOCKED",
                "package_verified": True,
                "problems": ["fingerprint_mismatch: package: criteria changed after the vote"],
                "package_fingerprint": "d" * 64,
                "reviewer_verdicts": {},
            }
            runner = fake_runner(
                [(
                    lambda argv: "council-packet.json" in " ".join(argv),
                    {"exit_status": 1, "stdout": json.dumps(report)},
                )]
            )
            result = council.council_check_packages(root, runner=runner)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            self.assertIn("hard_problem_codes", result["details"]["packages"][0])


IONIQ_REPO_URL = "https://github.com/JaredReabow/ioniq-5-Reverse-Engineering.git"
KONA_REPO_URL = "https://github.com/JaredReabow/kona-EV.git"


def verified_git_config(**overrides):
    """Config of a verified explicit Ioniq push destination."""
    config = {
        "remote.ioniq.url": IONIQ_REPO_URL,
        "remote.pushDefault": "ioniq",
    }
    config.update(overrides)
    return config


class GitScopeTests(unittest.TestCase):
    def codes(self, result):
        return [reason["code"] for reason in result["details"]["reasons"]]

    def test_staged_kona_path_blocks_even_with_verified_destination(self):
        runner = git_runner(
            status_stdout="?? evidence/a.md\u0000A  kona_research/uk_units/x.md\u0000",
            origin=KONA_REPO_URL,
            config=verified_git_config(),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertEqual(self.codes(result), ["staged-kona-path"])
        self.assertIsNotNone(result["details"]["verified_destination"])
        # The Kona origin is inert here; the block is the staged scope.
        self.assertTrue(result["details"]["origin_kona_ignored"])

    def test_rename_from_kona_path_blocks(self):
        runner = git_runner(
            status_stdout="R  kona_research/old.md\u0000kona_research/old.md\u0000",
            origin=KONA_REPO_URL,
            config=verified_git_config(),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("staged-kona-path", self.codes(result))

    def test_kona_origin_with_verified_ioniq_destination_passes(self):
        runner = git_runner(
            status_stdout="M  evidence/a.md\u0000?? new.md\u0000",
            origin=KONA_REPO_URL,
            config=verified_git_config(),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_PASS)
        details = result["details"]
        self.assertEqual(details["verified_destination"]["remote"], "ioniq")
        self.assertEqual(details["verified_destination"]["url"], IONIQ_REPO_URL)
        self.assertTrue(details["origin_kona_ignored"])
        self.assertEqual(details["reasons"], [])

    def test_kona_origin_alone_still_blocks(self):
        runner = git_runner(origin=KONA_REPO_URL)
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        codes = self.codes(result)
        self.assertIn("missing-ioniq-remote", codes)
        self.assertIn("push-default-not-ioniq", codes)
        self.assertNotIn("origin-kona-ev", codes)
        self.assertIsNone(result["details"]["verified_destination"])
        self.assertFalse(result["details"]["origin_kona_ignored"])

    def test_push_default_must_be_ioniq(self):
        runner = git_runner(
            config={"remote.ioniq.url": IONIQ_REPO_URL},
            origin=KONA_REPO_URL,
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("push-default-not-ioniq", self.codes(result))

    def test_empty_push_default_does_not_inherit_global_ioniq(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=[
                ("remote.ioniq.url", IONIQ_REPO_URL),
                ("remote.pushDefault", "ioniq"),
                ("remote.pushDefault", ""),
            ],
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("push-default-not-ioniq", self.codes(result))

    def test_push_default_naming_kona_remote_blocks(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(**{"remote.pushDefault": "origin"}),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        codes = self.codes(result)
        self.assertIn("push-default-not-ioniq", codes)
        self.assertIn("push-remote-kona-ev", codes)

    def test_ioniq_near_matches_block(self):
        near_matches = (
            "https://github.com/JaredReabow/ioniq-5-Reverse-Engineering-fork.git",
            "https://github.com/JaredReabow/ioniq5.git",
            "https://github.com/someone-else/Ioniq-5.git",
            "https://gitlab.com/JaredReabow/ioniq-5-Reverse-Engineering.git",
            "git@github.com:JaredReabow/ioniq-5-Reverse-Engineering.git.extra",
        )
        for url in near_matches:
            with self.subTest(url=url):
                runner = git_runner(
                    origin=KONA_REPO_URL,
                    config=verified_git_config(**{"remote.ioniq.url": url}),
                )
                result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
                self.assertEqual(result["status"], common.STATUS_BLOCKED)
                self.assertIn("ioniq-remote-mismatch", self.codes(result))

    def test_insecure_http_ioniq_remote_blocks(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(
                **{"remote.ioniq.url": "http://github.com/JaredReabow/ioniq-5-Reverse-Engineering.git"}
            ),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("insecure-ioniq-remote", self.codes(result))

    def test_ssh_remote_forms_are_accepted(self):
        for url in (
            "git@github.com:JaredReabow/ioniq-5-Reverse-Engineering.git",
            "ssh://git@github.com/JaredReabow/ioniq-5-Reverse-Engineering.git",
            "https://github.com/JaredReabow/ioniq-5-Reverse-Engineering",
        ):
            with self.subTest(url=url):
                runner = git_runner(
                    origin=KONA_REPO_URL,
                    config=verified_git_config(**{"remote.ioniq.url": url}),
                )
                result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
                self.assertEqual(result["status"], common.STATUS_PASS)
                self.assertEqual(
                    result["details"]["verified_destination"]["url"], url
                )

    def test_branch_push_remote_override_blocks(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(**{"branch.main.pushRemote": "origin"}),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        codes = self.codes(result)
        self.assertIn("branch-push-remote-overrides", codes)
        self.assertIn("push-remote-kona-ev", codes)

    def test_branch_push_remote_literal_kona_url_blocks(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(**{"branch.main.pushRemote": KONA_REPO_URL}),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("push-remote-kona-ev", self.codes(result))

    def test_branch_push_remote_other_remote_blocks(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(
                **{
                    "remote.mirror.url": "https://example.com/mirror.git",
                    "branch.main.pushRemote": "mirror",
                }
            ),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        codes = self.codes(result)
        self.assertIn("branch-push-remote-overrides", codes)
        self.assertIn("effective-push-mismatch", codes)

    def test_inactive_branch_pushing_to_kona_blocks(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(
                **{"branch.old-experiment.pushRemote": "origin"}
            ),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("branch-push-remote-kona-ev", self.codes(result))

    def test_inactive_branch_other_remote_is_reported_not_blocked(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(
                **{
                    "remote.backup.url": "https://example.com/backup.git",
                    "branch.topic.pushRemote": "backup",
                }
            ),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_PASS)
        self.assertEqual(
            result["details"]["inactive_branch_push_remotes"][0]["branch"], "topic"
        )

    def test_ioniq_pushurl_mismatch_blocks(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(**{"remote.ioniq.pushurl": KONA_REPO_URL}),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("ioniq-pushurl-mismatch", self.codes(result))

    def test_branch_pushurl_mismatch_blocks(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(**{"branch.main.pushurl": KONA_REPO_URL}),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("branch-pushurl-mismatch", self.codes(result))

    def test_url_rewrite_to_kona_blocks(self):
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(
                **{
                    "url.https://github.com/JaredReabow/kona-EV.git.pushInsteadOf": (
                        "https://github.com/JaredReabow/ioniq-5-Reverse-Engineering"
                    ),
                }
            ),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("url-rewrite-redirect", self.codes(result))

    def test_credentials_are_redacted_from_output(self):
        secret = "ghp_SUPERSECRETTOKEN"
        url = f"https://x-access-token:{secret}@github.com/JaredReabow/ioniq-5-Reverse-Engineering.git"
        runner = git_runner(
            origin=KONA_REPO_URL,
            config=verified_git_config(**{"remote.ioniq.url": url}),
        )
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_PASS)
        rendered = json.dumps(result)
        self.assertNotIn(secret, rendered)
        self.assertEqual(
            result["details"]["verified_destination"]["url"],
            "https://<redacted>@github.com/JaredReabow/ioniq-5-Reverse-Engineering.git",
        )

    def test_config_failure_blocks(self):
        runner = git_runner(origin=KONA_REPO_URL, config_ok=False)
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("config-unavailable", self.codes(result))

    def test_status_failure_blocks(self):
        runner = git_runner(status_ok=False, config=verified_git_config())
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_BLOCKED)
        self.assertIn("status-unavailable", self.codes(result))

    def test_not_a_repository_is_pending(self):
        runner = git_runner(top_ok=False)
        result = gitscope.gitscope_check(Path("/tmp/repo"), runner=runner)
        self.assertEqual(result["status"], common.STATUS_PENDING)


class GitScopeRealRepositoryTests(unittest.TestCase):
    """End-to-end check of the real ``git config --list -z`` snapshot path."""

    @unittest.skipUnless(shutil.which("git"), "git is not installed")
    def test_fresh_repo_passes_then_branch_override_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def git(*args):
                return subprocess.run(
                    ["git", "-C", str(root), *args],
                    check=True,
                    capture_output=True,
                    text=True,
                )

            git("init", "-q")
            branch = git("symbolic-ref", "--short", "HEAD").stdout.strip()
            git("remote", "add", "origin", KONA_REPO_URL)
            git("remote", "add", "ioniq", IONIQ_REPO_URL)
            git("config", "remote.pushDefault", "ioniq")

            result = gitscope.gitscope_check(root)
            self.assertEqual(result["status"], common.STATUS_PASS, result)
            self.assertEqual(
                result["details"]["verified_destination"]["url"], IONIQ_REPO_URL
            )

            git("config", f"branch.{branch}.pushRemote", "origin")
            result = gitscope.gitscope_check(root)
            self.assertEqual(result["status"], common.STATUS_BLOCKED)
            codes = [reason["code"] for reason in result["details"]["reasons"]]
            self.assertIn("push-remote-kona-ev", codes)


class PrivacyTests(unittest.TestCase):
    def test_secret_withheld_and_no_value_leaked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evidence").mkdir()
            secret = "AKIAIOSFODNN7EXAMPLE"
            address = "private.person@home-mailbox.io"
            (root / "evidence" / "leak.md").write_text(
                f"aws={secret}\nmail={address}\n", encoding="utf-8"
            )
            result = privacy.privacy_scan(root)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            categories = {item["category"] for item in result["details"]["findings"]}
            self.assertIn("aws-access-key", categories)
            self.assertIn("email-address-private-repository", categories)
            rendered = json.dumps(result)
            self.assertNotIn(secret, rendered)
            self.assertNotIn(address, rendered)

    def test_public_noreply_address_is_info_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evidence").mkdir()
            (root / "evidence" / "note.md").write_text(
                "commit identity: 37484454+xwtk@users.noreply.github.com\n",
                encoding="utf-8",
            )
            result = privacy.privacy_scan(root)
            self.assertEqual(result["status"], common.STATUS_INFO)
            self.assertEqual(result["details"]["blocking_count"], 0)

    def test_raw_archive_is_permitted_without_exposing_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evidence").mkdir()
            (root / "evidence" / "firmware.zip").write_bytes(b"PK\x03\x04payload")
            result = privacy.privacy_scan(root)
            self.assertEqual(result["status"], common.STATUS_PASS)
            self.assertNotIn("payload", json.dumps(result))

    def test_private_key_file_remains_prohibited(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "evidence").mkdir()
            (root / "evidence" / "live.key").write_bytes(b"secret-key-material")
            result = privacy.privacy_scan(root)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            self.assertEqual(result["details"]["findings"][0]["category"], "prohibited-file")
            self.assertNotIn("secret-key-material", json.dumps(result))

    def test_public_mode_rejects_raw_exports_and_personal_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PUBLIC-RELEASE.md").write_text("public snapshot\n")
            raw = root / "evidence" / "vehicle-usb" / "export.dlt"
            raw.parent.mkdir(parents=True)
            raw.write_bytes(b"opaque")
            (root / "evidence" / "note.md").write_text(
                "local path: /Users/privateperson/private\n", encoding="utf-8"
            )
            result = privacy.privacy_scan(root)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            categories = {item["category"] for item in result["details"]["findings"]}
            self.assertIn("raw-evidence-in-public-tree", categories)
            self.assertIn("operator-home-path", categories)
            self.assertNotIn("/Users/privateperson/private", json.dumps(result))

    def test_public_mode_ignores_private_untracked_raw_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "PUBLIC-RELEASE.md").write_text("public snapshot\n")
            (root / "evidence" / "vehicle-usb").mkdir(parents=True)
            (root / "evidence" / "vehicle-usb" / "private.dlt").write_bytes(b"private")
            subprocess.run(["git", "-C", str(root), "add", "PUBLIC-RELEASE.md"], check=True)
            result = privacy.privacy_scan(root)
            self.assertEqual(result["status"], common.STATUS_PASS)

    def test_public_mode_scans_new_vm_source_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "PUBLIC-RELEASE.md").write_text("public snapshot\n")
            vm_source = root / "vm" / "repro" / "probe.qml"
            vm_source.parent.mkdir(parents=True)
            vm_source.write_text("contact=private.person@home-mailbox.io\n")
            subprocess.run(
                ["git", "-C", str(root), "add", "PUBLIC-RELEASE.md", "vm/repro/probe.qml"],
                check=True,
            )
            result = privacy.privacy_scan(root)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            self.assertIn(
                "email-address-private-repository",
                {item["category"] for item in result["details"]["findings"]},
            )


class DocsTests(unittest.TestCase):
    def _ledger(self, root: Path, state: str, write_paths=None) -> Path:
        path = root / "research-ledger.json"
        task = {"id": "T6", "state": state}
        if write_paths is not None:
            task["write_paths"] = write_paths
        write_json(path, {"schema_version": 1, "tasks": [task]})
        return path

    def test_pending_while_t6_queued(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = docs.docs_check(self._ledger(root, "queued"), root)
            self.assertEqual(result["status"], common.STATUS_PENDING)
            self.assertEqual(
                sorted(result["details"]["required_docs"].values()),
                ["Ioniq5-CHANGELOG.md", "Ioniq5-HISTORY.md"],
            )

    def test_kona_titled_root_docs_do_not_satisfy_active_t6(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._ledger(
                root, "accepted", write_paths=["HISTORY.md", "CHANGELOG.md"]
            )
            (root / "HISTORY.md").write_text(
                "# History\n\nKona EV infotainment research.\n", encoding="utf-8"
            )
            (root / "CHANGELOG.md").write_text(
                "# Changelog\n\n## 0.1.3 - Kona EV\n", encoding="utf-8"
            )
            result = docs.docs_check(path, root)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            self.assertEqual(
                result["details"]["kona_owned_rejected"], ["HISTORY.md", "CHANGELOG.md"]
            )
            self.assertEqual(
                sorted(result["details"]["missing"]),
                ["Ioniq5-CHANGELOG.md", "Ioniq5-HISTORY.md"],
            )
            codes = [reason["code"] for reason in result["details"]["reasons"]]
            self.assertIn("kona-owned-path-declared", codes)
            self.assertIn("missing-ioniq-docs", codes)

    def test_dedicated_ioniq_docs_satisfy_active_t6(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._ledger(root, "accepted")
            (root / "HISTORY.md").write_text("# History\n\nKona EV.\n", encoding="utf-8")
            (root / "Ioniq5-HISTORY.md").write_text(
                "# Ioniq 5 History\n", encoding="utf-8"
            )
            (root / "Ioniq5-CHANGELOG.md").write_text(
                "# Ioniq 5 Changelog\n", encoding="utf-8"
            )
            result = docs.docs_check(path, root)
            self.assertEqual(result["status"], common.STATUS_PASS)
            self.assertEqual(result["details"]["required_source"], "default")
            self.assertEqual(result["details"]["missing"], [])

    def test_ledger_declared_ioniq_paths_are_preferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._ledger(
                root,
                "ready_for_review",
                write_paths=["ioniq5/HISTORY.md", "ioniq5/CHANGELOG.md"],
            )
            (root / "ioniq5").mkdir()
            (root / "ioniq5" / "HISTORY.md").write_text("# History\n", encoding="utf-8")
            (root / "ioniq5" / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
            result = docs.docs_check(path, root)
            self.assertEqual(result["status"], common.STATUS_PASS)
            self.assertEqual(result["details"]["required_source"], "ledger")
            self.assertEqual(
                sorted(result["details"]["required_docs"].values()),
                ["ioniq5/CHANGELOG.md", "ioniq5/HISTORY.md"],
            )

    def test_ioniq_doc_symlink_to_kona_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = self._ledger(root, "accepted")
            (root / "HISTORY.md").write_text("# History\n\nKona EV.\n", encoding="utf-8")
            (root / "CHANGELOG.md").write_text("# Changelog\n\nKona EV.\n", encoding="utf-8")
            (root / "Ioniq5-HISTORY.md").symlink_to(root / "HISTORY.md")
            (root / "Ioniq5-CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
            result = docs.docs_check(path, root)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            self.assertEqual(
                result["details"]["kona_owned_alias"], ["Ioniq5-HISTORY.md"]
            )


class JsonTests(unittest.TestCase):
    def test_bad_json_record_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "research-ledger.json", {"schema_version": 1})
            (root / "council" / "review-batch-1").mkdir(parents=True)
            (root / "council" / "review-batch-1" / "council-packet.json").write_text(
                "{", encoding="utf-8"
            )
            result = jsoncheck.jsoncheck_scan(root)
            self.assertEqual(result["status"], common.STATUS_FAIL)
            self.assertEqual(result["details"]["invalid"], 1)


class LedgerTests(unittest.TestCase):
    def _workflow(self, root: Path) -> Path:
        path = root / "workflow.py"
        path.write_text("# stub\n", encoding="utf-8")
        return path

    def test_warnings_become_info(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runner = fake_runner(
                [(
                    lambda argv: "validate" in argv,
                    {
                        "exit_status": 0,
                        "stdout": json.dumps(
                            {"ok": True, "errors": [], "warnings": ["unmapped requirement R9"]}
                        ),
                    },
                )]
            )
            result = ledger.ledger_validate(
                root / "research-ledger.json",
                workflow_path=self._workflow(root),
                runner=runner,
            )
            self.assertEqual(result["status"], common.STATUS_INFO)

    def test_errors_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runner = fake_runner(
                [(
                    lambda argv: "validate" in argv,
                    {
                        "exit_status": 1,
                        "stdout": json.dumps({"ok": False, "errors": ["bad state"], "warnings": []}),
                    },
                )]
            )
            result = ledger.ledger_validate(
                root / "research-ledger.json",
                workflow_path=self._workflow(root),
                runner=runner,
            )
            self.assertEqual(result["status"], common.STATUS_FAIL)
            self.assertEqual(result["details"]["errors"], ["bad state"])


class RunnerTests(unittest.TestCase):
    def test_public_mode_checks_json_without_private_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "PUBLIC-RELEASE.md").write_text("public snapshot\n")
            write_json(root / "evidence" / "summary.json", {"ok": True})
            report = run_all.runner_collect(root, only=["json", "ledger", "artifacts", "council"])
            self.assertEqual(report["exit_code"], 0)
            self.assertEqual(next(c for c in report["checks"] if c["check"] == "json")["status"], common.STATUS_PASS)

    def test_json_is_deterministic_and_clean_root_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_json(root / "research-ledger.json", {"schema_version": 1, "artifacts": []})
            first = run_all.runner_collect(root, only=["json"])
            second = run_all.runner_collect(root, only=["json"])
            self.assertEqual(run_all.runner_render_json(first), run_all.runner_render_json(second))
            self.assertEqual(first["exit_code"], 0)

    def test_invalid_json_exits_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "council" / "review-batch-1").mkdir(parents=True)
            (root / "council" / "review-batch-1" / "task.json").write_text("{", encoding="utf-8")
            report = run_all.runner_collect(root, only=["json"])
            self.assertEqual(report["exit_code"], 1)
            self.assertEqual(report["overall"], "fail")

    def test_unknown_check_is_harness_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(common.HarnessError):
                run_all.runner_collect(Path(tmp), only=["nope"])


if __name__ == "__main__":
    unittest.main()

