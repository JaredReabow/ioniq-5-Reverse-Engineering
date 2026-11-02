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
    assert length_review["submit_wrapper_stores_first_argument_dword_at_message_offset_zero"] is True
    assert length_review["constructor_stores_second_argument_low_byte_at_message_offset_four"] is True
    kernel_review = report["kernel_message_submit_selector_0x10_review"]
    assert kernel_review["selector"] == 0x10
    assert kernel_review["syscall_argument_size"] == 0x40
    assert kernel_review["reviewed_submit_syscall_value"] == 0x10010040
    assert kernel_review["raw_differing_byte_count"] == 7
    assert [site["affected_value"] for site in kernel_review["semantic_immediate_sites"]] == [0xFF, 0xFF]
    assert [site["first_fixed_value"] for site in kernel_review["semantic_immediate_sites"]] == [0x102, 0x102]
    helper = kernel_review["directly_called_helper"]
    assert helper["size"] == 0xB2
    assert helper["affected_sha256"] == "140dff321f92ee9e8fc551ff9e28e7501a97ab81b4b4e5c0f73ed52648cd3cea"
    assert helper["first_fixed_sha256"] == "0a10e5956f69381c8c455af7c14b72320d844709a9304af0ff439d38dfa7c196"
    ordinal = kernel_review["adjacent_ordinal_shift_review"]
    assert ordinal["site_count"] == 7
    assert ordinal["all_reviewed_values_increase_by_three"] is True
    assert ordinal["affected_to_first_fixed_value_counts"] == {
        "0x100_to_0x103": 2,
        "0x101_to_0x104": 1,
        "0x102_to_0x105": 4,
    }
    producers = kernel_review["first_fixed_inserted_status_producer_candidates"]
    assert producers["status_0x100"]["direct_call_sites"] == [0x85E86, 0x85EC9, 0x880BA]
    assert producers["status_0x101"]["direct_call_sites"] == [0x85936]
    assert producers["status_0x100"]["sha256"] == "b12ad8b0c4e784655e76de10ba1977c906bb55c14d0b7eccfd2c62479b96d930"
    assert producers["status_0x101"]["sha256"] == "004b911c32d58e78d2ffb3aab766308fb6b9168b35781208021eeabeb2f0f10e"
    census = kernel_review["kernel_global_immediate_census"]
    assert census["affected_total_site_count"] == 15
    assert census["first_fixed_total_site_count"] == 15
    assert census["affected_mov_edx_0xff"] == [0x8C08A]
    assert census["first_fixed_mov_edx_0x102"] == [0x8C02C]
    assert len(census["affected_cmp_eax_0xff"]) == 12
    assert len(census["first_fixed_cmp_eax_0x102"]) == 12
    assert json.loads(ARTIFACT.read_text(encoding="utf-8")) == report
