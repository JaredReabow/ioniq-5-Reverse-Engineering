from __future__ import annotations

import copy
import hashlib
import importlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools" / "uk_fw"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import smack_privileged_exec_chain as audit  # noqa: E402

BoundaryError = audit.BoundaryError

PYTHON = Path("/Users/leo/.platformio/penv/bin/python3")
ROOTFS = ROOT / "work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz"
BASH = ROOT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs/bin/bash"
REPORT = ROOT / "evidence/artifacts/application-candidates/smack-privileged-exec-chain-report.json"
SOURCES = {
    "--smack-lsm": ROOT / "work/online-smack-20261108/smack_lsm-v4.1.c",
    "--smack-header": ROOT / "work/online-smack-20261108/smack-v4.1.h",
    "--exec-source": ROOT / "work/online-kernel-exec-smack-20261108/exec.c",
    "--binfmt-script": ROOT / "work/online-kernel-exec-smack-20261108/binfmt_script.c",
    "--binfmt-elf": ROOT / "work/online-kernel-exec-smack-20261108/binfmt_elf.c",
    "--commoncap": ROOT / "work/online-kernel-exec-smack-20261108/commoncap.c",
    "--bash-shell": ROOT / "work/online-bash-3.2.57-20261109/bash-3.2.57/shell.c",
    "--bash-variables": ROOT / "work/online-bash-3.2.57-20261109/bash-3.2.57/variables.c",
    "--bash-findcmd": ROOT / "work/online-bash-3.2.57-20261109/bash-3.2.57/findcmd.c",
    "--glibc-rtld": ROOT / "work/online-glibc-2.25-20261109/glibc-2.25/elf/rtld.c",
    "--glibc-unsecvars": ROOT / "work/online-glibc-2.25-20261109/glibc-2.25/sysdeps/generic/unsecvars.h",
    "--glibc-extra-unsecvars": ROOT / (
        "work/online-glibc-2.25-20261109/glibc-2.25/"
        "sysdeps/unix/sysv/linux/x86_64/64/dl-librecon.h"
    ),
}


def _have_inputs() -> bool:
    return PYTHON.is_file() and ROOTFS.is_file() and BASH.is_file() and REPORT.is_file() and all(
        path.is_file() for path in SOURCES.values()
    )


def _command() -> list[str]:
    command = [
        str(PYTHON), str(TOOLS / "smack_privileged_exec_chain.py"),
        "--rootfs", str(ROOTFS),
        "--bash", str(BASH),
    ]
    for option, path in SOURCES.items():
        command.extend((option, str(path)))
    return command


@pytest.mark.skipif(not _have_inputs(), reason="private canonical audit inputs are unavailable")
def test_retained_report_is_exact_and_chain_is_bounded() -> None:
    completed = subprocess.run(_command(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    assert completed.returncode == 0, completed.stderr.decode("utf-8", "replace")
    assert completed.stderr == b""
    assert completed.stdout == REPORT.read_bytes()
    assert completed.stdout.endswith(b"\n") and b"\r" not in completed.stdout

    report = json.loads(completed.stdout)
    assert report["rootfs"] == {
        "size": 879109759,
        "sha256": "423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84",
        "member_count": 66836,
        "inventory_sha256": "c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c",
        "policy_member_count": 27,
        "policy_normalized_sha256": "4aa679165cca01d53993082df802bbaec29ee1fcaf42eda9f014951653a08f1a",
    }
    assert report["policy"]["app_domain_floor_execute_rule_count"] == 27
    assert report["policy"]["all_enumerated_app_floor_rules_allow_read_and_execute"] is True
    assert "App::upgrade" in report["policy"]["app_domain_floor_execute_subjects"]
    assert report["configured_labels"] == {
        "onlycap_label": "Privileged",
        "appupgrade_exec_label": "App::upgrade",
        "anchor_access_label": "_",
        "anchor_exec_label": "Privileged",
        "anchor_interpreter": "/bin/sh",
        "anchor_resets_path": False,
        "unqualified_lookup_before_argument_exit": "date",
    }
    assert report["bash"]["sha256"] == "783a69b9b27fae5da3fa93e441467160d6e760f3a79048a4dd02d98b571ad0aa"
    assert report["bash"]["build_id"] == "bbe47288a3fee7f0979fed1eb2794e5596f33113"
    assert report["bash"]["elf_interpreter"] == "/lib/ld-linux-x86-64.so.2"
    assert report["bash"]["dynamic_loader"]["sha256"] == "0dfa16d8b5c9b35fb161a6f5dab48e7b267531ecf8ec3bf3ac74de61ce2ad99e"
    chain = report["static_chain"]
    assert chain["committed_anchor_task_label"] == "Privileged"
    assert chain["v028_or_session_bus_required_for_this_transition"] is False
    assert chain["pretransition_subject_and_inode_access_label_control_open_admission"] is True
    assert chain["exec_transition_label_does_not_authorize_open"] is True
    assert chain["ordinary_read_and_execute_permission_from_every_enumerated_app_domain"] is True
    assert chain["credential_commit_can_precede_late_elf_loader_failure"] is True
    assert chain["glibc_secure_mode_removes_named_unsecure_variables_but_not_path"] is True
    assert chain["bash_source_allows_environment_function_import_when_uid_gid_match"] is True
    assert chain["onlycap_is_a_smack_call_site_gate_not_a_capability_mask"] is True
    assert report["assessment"] == {
        "configured_direct_app_to_onlycap_label_transition_candidate": True,
        "configured_uid_escalation": False,
        "configured_smack_override_eligibility_after_transition": True,
        "effective_smack_override_established": False,
        "runtime_root_or_persistence_demonstrated": False,
        "operational_payload_emitted": False,
    }
    assert all(value is None for value in report["runtime_unknowns"].values())


@pytest.mark.skipif(not _have_inputs(), reason="private canonical audit inputs are unavailable")
def test_cli_output_is_encoding_independent_and_does_not_emit_payload_material() -> None:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-16"
    completed = subprocess.run(_command(), env=environment, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=False)
    assert completed.returncode == 0
    assert completed.stderr == b""
    assert completed.stdout == REPORT.read_bytes()
    for forbidden in (
        str(ROOT).encode(), b"LD_PRELOAD=", b"PATH=/tmp", b"#!/bin/sh\nexec",
        b"chsmack -e", b"mount -o", b"/dev/mmcblk",
    ):
        assert forbidden not in completed.stdout


def test_policy_parser_rejects_duplicates_and_malformed_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(audit, "POLICY_RULE_COUNT", 1)
    base = {"name": "etc/smack/accesses.d/a", "bytes": b"App::one _ rwx---\n"}
    rules = audit.parse_policy([base])
    assert rules[0]["subject"] == "App::one"
    assert {"r", "x"}.issubset(set(rules[0]["access"]))
    duplicate = [
        base,
        {"name": "etc/smack/accesses.d/b", "bytes": b"App::one _ r-----\n"},
    ]
    with pytest.raises(BoundaryError, match="duplicate"):
        audit.parse_policy(duplicate)
    with pytest.raises(BoundaryError, match="field-count"):
        audit.parse_policy([{"name": "etc/smack/accesses.d/a", "bytes": b"App::one _\n"}])
    with pytest.raises(BoundaryError, match="unsupported policy access"):
        audit.parse_policy([{"name": "etc/smack/accesses.d/a", "bytes": b"App::one _ rwx!\n"}])


def test_build_id_is_parsed_from_the_stable_bytes_without_reopening(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = BASH.read_bytes() if BASH.is_file() else None
    if raw is None:
        pytest.skip("canonical bash is unavailable")
    assert audit._gnu_build_id(raw) == audit.BASH_BUILD_ID
    monkeypatch.setattr(audit, "_read_stable", lambda *_args, **_kwargs: raw)
    monkeypatch.setattr(Path, "open", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("reopen")))
    assert audit._gnu_build_id(raw) == audit.BASH_BUILD_ID


def test_source_validation_rejects_identity_and_semantic_drift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "source.c"
    source.write_bytes(b"required-anchor\n")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    monkeypatch.setattr(audit, "SOURCE_IDENTITIES", {"one": digest})
    monkeypatch.setattr(audit, "SOURCE_ANCHORS", {"one": (b"required-anchor",)})
    assert audit.validate_sources({"one": source})["one"]["sha256"] == digest
    source.write_bytes(b"changed\n")
    with pytest.raises(BoundaryError, match="identity drift"):
        audit.validate_sources({"one": source})


def test_source_validation_rejects_path_in_arch_extra_unsecure_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    extra = tmp_path / "dl-librecon.h"
    raw = b'#define EXTRA_UNSECURE_ENVVARS "PATH\\0"\n'
    extra.write_bytes(raw)
    monkeypatch.setattr(audit, "SOURCE_IDENTITIES", {
        "glibc_extra_unsecvars": hashlib.sha256(raw).hexdigest(),
    })
    monkeypatch.setattr(audit, "SOURCE_ANCHORS", {
        "glibc_extra_unsecvars": (b"#define EXTRA_UNSECURE_ENVVARS",),
    })
    with pytest.raises(BoundaryError, match="unexpectedly includes PATH"):
        audit.validate_sources({"glibc_extra_unsecvars": extra})


def _small_rootfs(path: Path) -> tuple[dict[str, object], str, int, str, str]:
    selected_bytes = b"ELF"
    policy_bytes = b"App::one _ rwx---\n"
    with tarfile.open(path, "w:gz", format=tarfile.GNU_FORMAT) as archive:
        selected = tarfile.TarInfo("./bin/bash")
        selected.mode = 0o755
        selected.uid = selected.gid = 0
        selected.mtime = 0
        selected.size = len(selected_bytes)
        archive.addfile(selected, io.BytesIO(selected_bytes))
        policy = tarfile.TarInfo("./etc/smack/accesses.d/test")
        policy.mode = 0o644
        policy.uid = policy.gid = 0
        policy.mtime = 0
        policy.size = len(policy_bytes)
        archive.addfile(policy, io.BytesIO(policy_bytes))
    inventory = hashlib.sha256()
    count = 0
    with tarfile.open(path, "r:gz") as archive:
        for index, member in enumerate(archive):
            count += 1
            inventory.update(audit._inventory_line(index, member))
    policy_digest = hashlib.sha256(policy_bytes).hexdigest()
    normalized = hashlib.sha256(
        f"./etc/smack/accesses.d/test\0{len(policy_bytes)}\0{policy_digest}\n".encode("utf-8")
    ).hexdigest()
    expected = {
        "kind": "regular", "mode": 0o755, "uid": 0, "gid": 0,
        "size": len(selected_bytes), "sha256": hashlib.sha256(selected_bytes).hexdigest(),
    }
    return expected, hashlib.sha256(path.read_bytes()).hexdigest(), count, inventory.hexdigest(), normalized


def _archive_member(name: str, raw: bytes = b"ELF", *, kind: bytes = tarfile.REGTYPE,
                    linkname: str = "") -> tuple[tarfile.TarInfo, bytes | None]:
    member = tarfile.TarInfo(name)
    member.mode = 0o755
    member.uid = member.gid = 0
    member.mtime = 0
    member.type = kind
    member.linkname = linkname
    member.size = len(raw) if kind in (tarfile.REGTYPE, tarfile.AREGTYPE) else 0
    return member, raw if member.size else None


def _write_members(path: Path, members: list[tuple[tarfile.TarInfo, bytes | None]]) -> None:
    with tarfile.open(path, "w:gz", format=tarfile.GNU_FORMAT) as archive:
        for member, raw in members:
            archive.addfile(member, None if raw is None else io.BytesIO(raw))


def _configure_alias_fixture(path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    selected_raw = b"ELF"
    monkeypatch.setattr(audit, "SELECTED", {
        "bin/bash": {
            "kind": "regular", "mode": 0o755, "uid": 0, "gid": 0,
            "size": len(selected_raw), "sha256": hashlib.sha256(selected_raw).hexdigest(),
        }
    })
    monkeypatch.setattr(audit, "ROOTFS", {"size": path.stat().st_size})


@pytest.mark.parametrize(
    ("members", "error"),
    (
        ((_archive_member("bin/bash"),), "selected rootfs member is duplicated or aliased"),
        ((_archive_member("./bin/./bash"),), "non-canonical or unsafe"),
        ((_archive_member("./etc/../bin/bash"),), "non-canonical or unsafe"),
        ((
            _archive_member("./bin/bash"),
            _archive_member("bin/bash"),
        ), "duplicate or aliased member names"),
        ((
            _archive_member("./bin/bash"),
            _archive_member("./etc/smack/accesses.d/nested/test", b"App::one _ rwx---\n"),
        ), "policy member is nested or aliased"),
        ((
            _archive_member("./bin/bash", b"", kind=tarfile.SYMTYPE, linkname="target"),
        ), "selected archive member is not a regular file"),
        ((
            _archive_member("./bin/bash", b"", kind=tarfile.CHRTYPE),
        ), "selected archive member is not a regular file"),
    ),
    ids=(
        "selected-alias", "dot-alias", "dotdot-alias", "duplicate-canonical",
        "nested-policy", "selected-link", "selected-special",
    ),
)
def test_rootfs_archive_alias_and_special_node_rejections(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    members: tuple[tuple[tarfile.TarInfo, bytes | None], ...],
    error: str,
) -> None:
    archive = tmp_path / "rootfs.tar.gz"
    _write_members(archive, list(members))
    _configure_alias_fixture(archive, monkeypatch)
    with pytest.raises(BoundaryError, match=error):
        audit.rootfs_snapshot(archive)


def test_rootfs_path_replacement_during_streaming_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = tmp_path / "rootfs.tar.gz"
    replacement = tmp_path / "replacement.tar.gz"
    expected, digest, count, inventory, normalized = _small_rootfs(original)
    shutil.copyfile(original, replacement)
    monkeypatch.setattr(audit, "SELECTED", {"bin/bash": expected})
    monkeypatch.setattr(audit, "POLICY_COUNT", 1)
    monkeypatch.setattr(audit, "POLICY_NORMALIZED_SHA256", normalized)
    monkeypatch.setattr(audit, "ROOTFS", {
        "size": original.stat().st_size,
        "sha256": digest,
        "member_count": count,
        "inventory_sha256": inventory,
    })
    real_reader = audit._HashingReader
    replaced = False

    class ReplacingReader(real_reader):  # type: ignore[misc, valid-type]
        def read(self, size: int = -1) -> bytes:
            nonlocal replaced
            value = super().read(size)
            if not replaced:
                os.replace(replacement, original)
                replaced = True
            return value

    monkeypatch.setattr(audit, "_HashingReader", ReplacingReader)
    with pytest.raises(BoundaryError, match="changed during streaming"):
        audit.rootfs_snapshot(original)


def test_module_reload_keeps_contract_constants_stable() -> None:
    before = copy.deepcopy(audit.ROOTFS)
    reloaded = importlib.reload(audit)
    assert reloaded.ROOTFS == before
