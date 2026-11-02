import hashlib
import json
import lzma
from pathlib import Path

import pytest

from tools.uk_fw import txe_fixed_module_diff as diff


ROOT = Path(__file__).resolve().parents[1]
AFFECTED = ROOT / "work/decrypted-eu-260128/extracted-safe/update/abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin"
FIRST_FIXED = ROOT / "work/online-fixed-txe-search-20261102/X541NA-AS.321-ifwi.bin"
LATER = ROOT / "work/online-fixed-txe-search-20261102/AY0076-full-ifwi.bin"
ARTIFACT = ROOT / "evidence/artifacts/update-candidates/txe-fixed-module-diff.json"
EXACT_STATIC = ROOT / "evidence/artifacts/update-candidates/txe-fixed-heci-exact-static.txt"


def test_strict_cse_lzma_round_trip_and_trailing_data_rejection():
    value = (b"bounded-passive-comparison\0" * 64) + bytes(range(256))
    stream = lzma.compress(value, format=lzma.FORMAT_ALONE)
    cse_stream = stream[:0x0E] + b"\0\0\0" + stream[0x0E:]
    assert diff.strict_cse_lzma(cse_stream, len(value), "synthetic") == value
    with pytest.raises(diff.Failure, match="strict decompression drift"):
        diff.strict_cse_lzma(cse_stream + b"trailing", len(value), "synthetic")


def test_stable_read_rejects_symlink(tmp_path):
    source = tmp_path / "source.bin"
    source.write_bytes(b"safe")
    alias = tmp_path / "alias.bin"
    alias.symlink_to(source)
    with pytest.raises(OSError):
        diff.stable_read(alias)


@pytest.mark.skipif(
    not (AFFECTED.is_file() and FIRST_FIXED.is_file() and LATER.is_file()),
    reason="canonical offline firmware inputs unavailable",
)
def test_canonical_fixed_module_diff_matches_reviewed_artifact():
    report = diff.build_report(
        diff.stable_read(AFFECTED),
        diff.stable_read(FIRST_FIXED),
        diff.stable_read(LATER),
    )
    assert report["schema"] == diff.SCHEMA
    assert report["inputs"]["affected"]["nftp_manifest"]["version"] == "3.1.50.2222"
    assert report["inputs"]["first_fixed"]["nftp_manifest"]["version"] == "3.1.55.2269"
    assert report["inputs"]["later"]["nftp_manifest"]["version"] == "3.1.94.3086"
    assert report["inputs"]["affected"]["modules"]["heci"]["decompressed_sha256"] == diff.OLD_HECI_SHA256
    assert report["inputs"]["first_fixed"]["modules"]["heci"]["decompressed_sha256"] == diff.FIRST_FIXED_HECI_SHA256
    assert report["inputs"]["later"]["modules"]["heci"]["decompressed_sha256"] == diff.LATER_HECI_SHA256
    assert report["later_heci_exact_static_review"]["exact_static_observations"]["dma_ring_bit_29_now_rejected_before_payload_dispatch"] is True
    assert report["first_fixed_heci_exact_static_review"]["exact_static_observations"]["entire_heci_module_equal_after_only_external_rel32_relocation_normalization"] is True
    assert report["first_fixed_heci_exact_static_review"]["module_wide_relocation_review"]["external_rel32_site_count"] == 369
    busdrv_review = report["first_fixed_busdrv_exact_static_review"]
    assert busdrv_review["raw_differing_byte_count"] == 97
    assert busdrv_review["external_rel32_call_site_count"] == 96
    assert busdrv_review["distinct_affected_external_target_count"] == 26
    assert busdrv_review["affected_external_target_range"] == [0x6465, 0x67AD]
    assert busdrv_review["exact_static_observations"]["busdrv_local_opcode_or_non_address_data_change_at_first_fixed_boundary"] is False
    syslib_review = report["first_fixed_heci_syslib_import_review"]
    assert syslib_review["imported_destination_count"] == 42
    assert syslib_review["heci_external_reference_count"] == 369
    assert syslib_review["reviewed_body_byte_count"] == 4410
    assert syslib_review["raw_differing_byte_count"] == 39
    assert syslib_review["rel32_relocation_site_count"] == 37
    assert syslib_review["absolute_address_relocation_site_count"] == 1
    assert syslib_review["destination_entry_shift_counts"] == {"5": 33, "8": 2, "34": 7}
    assert syslib_review["exact_static_observations"]["no_directly_imported_syslib_body_has_an_opcode_or_non_address_data_change"] is True
    callee_review = report["first_fixed_heci_syslib_first_level_callee_review"]
    assert callee_review["raw_0xe8_byte_count_in_42_bodies"] == 105
    assert callee_review["reviewed_direct_call_site_count"] == 96
    assert callee_review["reviewed_incidental_0xe8_byte_count"] == 9
    assert callee_review["distinct_direct_call_target_pair_count"] == 33
    assert callee_review["unchanged_external_gate_reference_count"] == 12
    assert callee_review["already_reviewed_body_reference_count"] == 6
    assert callee_review["new_internal_first_level_callee_reference_count"] == 78
    assert callee_review["new_internal_first_level_callee_count"] == 29
    assert callee_review["reviewed_callee_body_byte_count"] == 3911
    assert callee_review["raw_differing_byte_count"] == 34
    assert callee_review["rel32_relocation_site_count"] == 29
    assert callee_review["absolute_address_relocation_site_count"] == 4
    assert callee_review["exact_static_observations"]["no_first_level_callee_body_has_an_opcode_or_non_address_data_change"] is True
    assert report["first_fixed_vfs_exact_static_review"]["exact_static_observations"]["first_fixed_vfs_adds_both_ndl_path_consumers"] is True
    assert report["first_fixed_vfs_exact_static_review"]["first_fixed_syslib"]["new_setter_runtime_range"] == [0x16691, 0x166AB]
    assert report["later_fpf_exact_static_review"]["exact_static_observations"]["affected_fpf_lacks_all_six_field_names"] is True
    assert report["later_fpf_exact_static_review"]["exact_static_observations"]["first_fixed_fpf_lacks_all_six_field_names"] is True
    assert report["later_fpf_exact_static_review"]["fields"]["OemKmArbSvn"]["field_bit_range_inclusive"] == [0x28C, 0x29F]
    assert report["classification"]["cve_2018_12147_exact_bug_identified"] is False
    assert report["classification"]["cve_2018_3655_exact_storage_bug_identified"] is False
    assert json.loads(ARTIFACT.read_text(encoding="utf-8")) == report
    assert hashlib.sha256(EXACT_STATIC.read_bytes()).hexdigest() == "cef4f22d92995e44e18eb75fa024bf6e936581a67d5b8c31cb73bf3029a1cbf3"
