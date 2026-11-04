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

import applauncher_app300_argv as audit  # noqa: E402
from appfumo_boot_activation_boundary import (  # noqa: E402
    BoundaryError,
    _canonical_member_name,
    _inventory_line,
)

ROOTFS = ROOT / "work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz"
APP = ROOT / "work/decrypted-eu-260128/extracted-partial-bsdtar/mango-rootfs/app/bin/AppLauncher"
MANIFEST = ROOT / "evidence/artifacts/application-candidates/applauncher-app300-argv-manifest.json"
REPORT = ROOT / "evidence/artifacts/application-candidates/applauncher-app300-argv-report.json"
OBJDUMP = Path("/opt/homebrew/opt/llvm/bin/llvm-objdump")
READELF = Path("/opt/homebrew/opt/llvm/bin/llvm-readelf")
PYTHON = Path("python3")


def _have_inputs() -> bool:
    return all(path.is_file() for path in (ROOTFS, APP, MANIFEST, REPORT, OBJDUMP, READELF, PYTHON))


def _command() -> list[str]:
    return [
        str(PYTHON), str(TOOLS / "applauncher_app300_argv.py"),
        "--rootfs", str(ROOTFS),
        "--applauncher", str(APP),
        "--manifest", str(MANIFEST),
        "--objdump", str(OBJDUMP),
        "--readelf", str(READELF),
    ]


@pytest.mark.skipif(not _have_inputs(), reason="private canonical audit inputs are unavailable")
def test_retained_report_is_exact_and_contract_is_bounded() -> None:
    completed = subprocess.run(_command(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    assert completed.returncode == 0, completed.stderr.decode("utf-8", "replace")
    assert completed.stderr == b""
    assert completed.stdout == REPORT.read_bytes()
    assert completed.stdout.endswith(b"\n") and b"\r" not in completed.stdout

    report = json.loads(completed.stdout)
    assert report["artifact"] == {
        "role": "canonical-rootfs-AppLauncher",
        "size": 407720,
        "sha256": "c8d6d56bc254ad0731e81f40bd83aa9b3be6b49bcbd8efb291157a06c4a84268",
        "build_id": "0452df1033bd1bbae15727a83d4d56576d8b9444",
    }
    assert report["rootfs"]["external_option_member_present"] is False
    assert report["static_contract"]["table_source"]["fallback_is_bounded_to_one_transition"] is True
    assert report["static_contract"]["table_source"]["recursive_fallback_call_site"] == "0x38df0"
    assert report["whole_inventory"] == {
        "instruction_count": 59259,
        "instruction_sha256": "a83cf95ee11850142b5c6b37d7a2d861f48452521aa1d8b4f57fd74c08faa168",
        "fde_count": 436,
        "fde_sha256": "b7d430bbf6dedd5285ffdabe84188d7eb404909550ffc3aaf1f7380a30a664c5",
        "machine_anchor_count": 127,
        "direct_transfer_target_count": 7,
    }

    contract = report["static_contract"]
    assert contract["process_construction"]["app_id_300_uses_this_ordinary_path"] is True
    assert contract["process_construction"]["option_builder_call"] == {
        "site": "0x1fec8", "target": "0x34510", "mode": 0,
    }
    assert contract["process_construction"]["program_store"]["field"] == "AppProcess+0x58"
    assert contract["process_construction"]["generated_arguments_store"]["field"] == "AppProcess+0x60"
    assert contract["process_start"]["qprocess_start_site"] == "0x1745d"
    assert contract["process_start"]["program_binding"]["call_register"] == "rsi"
    assert contract["process_start"]["argument_list_address_binding"]["call_register"] == "rdx"
    assert contract["option_builder"]["selected_options_preserve_list_order"] is True
    predicate = contract["recovered_row_selection_predicate"]
    assert predicate["matching_embedded_data_rows"] == 1
    assert predicate["matching_embedded_split_index"] == 50
    assert predicate["region_column_participates_in_predicate"] is False
    assert predicate["owner_unit_runtime_predicate_satisfied"] is None
    assert contract["option_builder"]["whole_generated_argv_fixed_by_static_row_alone"] is False

    table = contract["table"]
    assert table["selected_row_split_index"] == 50
    assert table["selected_row_field_count_including_terminal_empty"] == 38
    assert table["normal_branch_matching_row_count"] == 1
    assert table["selected_option_count"] == 17
    assert table["selected_option_sequence_sha256"] == "4a265a6c887376163f37544abec770074afe3ec63d063eaf9bdf28a87010d04a"
    assert table["update_mode_option_ordinal_zero_based"] == 14
    assert table["update_mode_value_role"] == "zero"
    assert table["owner_unit_selected_this_row"] is None
    assert all(value is None for value in report["runtime_unknowns"].values())


@pytest.mark.skipif(not _have_inputs(), reason="private canonical audit inputs are unavailable")
def test_cli_output_is_encoding_independent_and_privacy_bounded() -> None:
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-16"
    completed = subprocess.run(_command(), env=environment, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, check=False)
    assert completed.returncode == 0
    assert completed.stderr == b""
    assert completed.stdout == REPORT.read_bytes()
    forbidden = [
        str(ROOT).encode(), str(ROOTFS).encode(), str(APP).encode(),
        b"/app/bin/CarOption.csv", b"-un:0", b"NE,o,0x26", b"QDBusMessage",
    ]
    assert all(item not in completed.stdout for item in forbidden)
    assert b"\r" not in completed.stdout


def test_table_contract_is_exact_but_does_not_promote_runtime_selection() -> None:
    raw = APP.read_bytes() if APP.is_file() else b""
    if not raw:
        pytest.skip("private AppLauncher is unavailable")
    table = audit._table_contract(raw[0x4BA10:0x4BA10 + 0x69B5])
    assert table["delimiter_occurrences"] == 128
    assert table["split_component_count"] == 129
    assert table["selected_row_role"] == "recovered-NE-EUR-fallback-row"
    assert table["owner_unit_selected_this_row"] is None
    value = raw[0x4BA10:0x4BA10 + 0x69B5]
    ne_start = value.index(b"NE,o,0x26,EV")
    update_mode = value.index(b"-un:0", ne_start)
    changed_ne = value[:update_mode] + b"-un:9" + value[update_mode + 5:]
    for changed in (
        value.replace(b"END            ", b"ENX            ", 1),
        changed_ne,
    ):
        with pytest.raises(BoundaryError):
            audit._table_contract(changed)


def test_manifest_rejects_duplicate_keys_boolean_integer_and_shape_drift(tmp_path: Path) -> None:
    source = MANIFEST.read_text("utf-8")
    duplicate = source.replace('"schema_version": 1', '"schema_version": 1,\n  "schema_version": 1', 1)
    path = tmp_path / "duplicate.json"
    path.write_text(duplicate, encoding="utf-8", newline="\n")
    with pytest.raises(BoundaryError, match="duplicate JSON key"):
        audit.load_manifest(path)

    parsed = json.loads(source)
    parsed["schema_version"] = True
    path.write_text(json.dumps(parsed), encoding="utf-8", newline="\n")
    with pytest.raises(BoundaryError, match="non-Boolean"):
        audit.load_manifest(path)

    parsed = json.loads(source)
    parsed["expected"]["anchors"].append(copy.deepcopy(parsed["expected"]["anchors"][0]))
    path.write_text(json.dumps(parsed), encoding="utf-8", newline="\n")
    with pytest.raises(BoundaryError, match="duplicate anchor"):
        audit.load_manifest(path)

    parsed = json.loads(source)
    parsed["expected"]["direct_transfers"][0]["calls"].reverse()
    path.write_text(json.dumps(parsed), encoding="utf-8", newline="\n")
    with pytest.raises(BoundaryError, match="unique and sorted"):
        audit.load_manifest(path)


def _small_rootfs(path: Path, app_bytes: bytes) -> tuple[int, str, int, str]:
    with tarfile.open(path, "w:gz", format=tarfile.GNU_FORMAT) as archive:
        info = tarfile.TarInfo("./app/bin/AppLauncher")
        info.mode = 0o755
        info.size = len(app_bytes)
        info.mtime = 0
        archive.addfile(info, io.BytesIO(app_bytes))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    inventory = hashlib.sha256()
    count = 0
    with tarfile.open(path, "r:gz") as archive:
        for index, member in enumerate(archive):
            count += 1
            inventory.update(_inventory_line(index, member))
    return path.stat().st_size, digest, count, inventory.hexdigest()


@pytest.mark.skipif(not APP.is_file(), reason="private AppLauncher is unavailable")
def test_rootfs_replacement_during_streaming_fails_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = tmp_path / "rootfs.tar.gz"
    replacement = tmp_path / "replacement.tar.gz"
    values = _small_rootfs(original, APP.read_bytes())
    shutil.copyfile(original, replacement)
    monkeypatch.setitem(audit.ROOTFS, "size", values[0])
    monkeypatch.setitem(audit.ROOTFS, "sha256", values[1])
    monkeypatch.setitem(audit.ROOTFS, "member_count", values[2])
    monkeypatch.setitem(audit.ROOTFS, "inventory_sha256", values[3])

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
        audit._rootfs_snapshot(original)


def test_report_and_manifest_are_utf8_lf_and_do_not_retain_sensitive_values() -> None:
    for path in (MANIFEST, REPORT):
        raw = path.read_bytes()
        raw.decode("utf-8", "strict")
        assert raw.endswith(b"\n")
        assert b"\r" not in raw
        assert str(ROOT).encode() not in raw
        assert b"NE,o,0x26" not in raw
        assert b"-un:0" not in raw
        assert b"/app/bin/CarOption.csv" not in raw
