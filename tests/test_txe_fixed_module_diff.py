import hashlib
import json
import lzma
from pathlib import Path

import pytest

from tools.uk_fw import txe_fixed_module_diff as diff


ROOT = Path(__file__).resolve().parents[1]
AFFECTED = ROOT / "work/decrypted-eu-260128/extracted-safe/update/abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin"
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


@pytest.mark.skipif(not (AFFECTED.is_file() and LATER.is_file()), reason="canonical offline firmware inputs unavailable")
def test_canonical_fixed_module_diff_matches_reviewed_artifact():
    report = diff.build_report(diff.stable_read(AFFECTED), diff.stable_read(LATER))
    assert report["schema"] == diff.SCHEMA
    assert report["inputs"]["affected"]["nftp_manifest"]["version"] == "3.1.50.2222"
    assert report["inputs"]["later"]["nftp_manifest"]["version"] == "3.1.94.3086"
    assert report["inputs"]["affected"]["modules"]["heci"]["decompressed_sha256"] == diff.OLD_HECI_SHA256
    assert report["inputs"]["later"]["modules"]["heci"]["decompressed_sha256"] == diff.FIXED_HECI_SHA256
    assert report["later_heci_exact_static_review"]["exact_static_observations"]["dma_ring_bit_29_now_rejected_before_payload_dispatch"] is True
    assert report["classification"]["cve_2018_12147_exact_bug_identified"] is False
    assert report["classification"]["cve_2018_3655_exact_storage_bug_identified"] is False
    assert json.loads(ARTIFACT.read_text(encoding="utf-8")) == report
    assert hashlib.sha256(EXACT_STATIC.read_bytes()).hexdigest() == "237bab9d1108085a78c093bec2a7ab420ff37db6d6e6ddc988130bea88e98b82"
