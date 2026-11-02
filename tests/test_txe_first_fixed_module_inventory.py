import json
import struct
from pathlib import Path

import pytest

from tools.uk_fw import txe_first_fixed_module_inventory as inventory


ROOT = Path(__file__).resolve().parents[1]
AFFECTED = ROOT / "work/decrypted-eu-260128/extracted-safe/update/abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin"
FIRST_FIXED = ROOT / "work/online-fixed-txe-search-20261102/X541NA-AS.321-ifwi.bin"
ARTIFACT = ROOT / "evidence/artifacts/update-candidates/txe-first-fixed-module-inventory.json"


def test_differing_byte_count_includes_length_delta():
    assert inventory.differing_byte_count(b"abc", b"axc!") == 2


def test_synthetic_syslib_relocation_only_review():
    affected_stub = 0x6465
    first_fixed_stub = affected_stub + 5
    affected_displacement = affected_stub - (inventory.MODULE_BASE + 5)
    first_displacement = first_fixed_stub - (inventory.MODULE_BASE + 5)
    affected = b"\xe8" + struct.pack("<i", affected_displacement) + b"\xc3"
    first_fixed = b"\xe8" + struct.pack("<i", first_displacement) + b"\xc3"
    affected_syslib = bytearray(0x13000)
    first_syslib = bytearray(0x13000)
    affected_syslib[affected_stub - inventory.SYSLIB_BASE] = 0xE9
    first_syslib[first_fixed_stub - inventory.SYSLIB_BASE] = 0xE9

    review = inventory.relocation_review(
        affected,
        first_fixed,
        bytes(affected_syslib),
        bytes(first_syslib),
    )

    assert review["reviewed_external_rel32_site_count"] == 1
    assert review["unexplained_differing_byte_count"] == 0
    assert review["equal_after_reviewed_external_rel32_normalization"] is True


@pytest.mark.skipif(
    not (AFFECTED.is_file() and FIRST_FIXED.is_file()),
    reason="canonical offline firmware inputs unavailable",
)
def test_canonical_inventory_matches_reviewed_artifact():
    report = inventory.build_report(
        inventory.fixed.stable_read(AFFECTED),
        inventory.fixed.stable_read(FIRST_FIXED),
    )
    assert report["schema"] == inventory.SCHEMA
    assert report["summary"]["module_count"] == 34
    assert report["summary"]["decoded_module_count"] == 33
    assert report["summary"]["classification_counts"] == {
        "byte_identical": 1,
        "syslib_relocation_only": 9,
        "changed_with_unexplained_bytes": 23,
        "opaque_changed": 1,
    }
    assert set(report["summary"]["classification_modules"]["syslib_relocation_only"]) == inventory.EXPECTED_RELOCATION_ONLY
    assert report["summary"]["classification_modules"]["byte_identical"] == ["ish_bup"]
    assert report["summary"]["classification_modules"]["opaque_changed"] == ["pavp"]
    assert report["summary"]["smallest_unexplained_equal_size_modules"][:4] == [
        {"name": "ish_srv", "unexplained_differing_byte_count": 1},
        {"name": "loadmgr", "unexplained_differing_byte_count": 1},
        {"name": "gpio", "unexplained_differing_byte_count": 2},
        {"name": "pm", "unexplained_differing_byte_count": 7},
    ]
    assert report["modules"]["heci"]["relocation_review"]["equal_after_reviewed_external_rel32_normalization"] is True
    assert report["modules"]["pavp"]["affected"]["module_extension_flag_byte_9"] == 1
    length_review = report["minimal_length_delta_review"]
    assert length_review["module_count"] == 4
    assert length_review["site_count"] == 11
    assert length_review["message_dword_zero"] == 0x02000200
    assert length_review["all_reviewed_lengths_increment_by_one"] is True
    assert length_review["constructor_stores_first_argument_dword_at_message_offset_zero"] is True
    assert length_review["constructor_stores_second_argument_low_byte_at_message_offset_four"] is True
    assert json.loads(ARTIFACT.read_text(encoding="utf-8")) == report
