import hashlib
import json
from pathlib import Path

import pytest

from tools.uk_fw import carplay_sdk_applicability as audit


ROOT = Path(__file__).resolve().parents[1]
ROOTFS = ROOT / "work/decrypted-eu-260128/extracted-safe/mango-rootfs"
ARTIFACT = ROOT / "evidence/artifacts/projection-candidates/carplay-sdk-applicability.json"


def canonical_sha256(report):
    subject = dict(report)
    subject.pop("canonical_sha256")
    return hashlib.sha256(
        json.dumps(subject, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def minimal_elf(*, stack_flags=6):
    ident = b"\x7fELF\x02\x01\x01" + b"\x00" * 9
    ehsize = audit.ELF_HEADER.size
    phoff = ehsize
    phnum = 2
    header = audit.ELF_HEADER.pack(
        ident, 3, 62, 1, 0x1000, phoff, 0, 0, ehsize,
        audit.PROGRAM_HEADER.size, phnum, 0, 0, 0,
    )
    interp = b"/lib/ld.so\x00"
    interp_off = ehsize + phnum * audit.PROGRAM_HEADER.size
    programs = b"".join((
        audit.PROGRAM_HEADER.pack(audit.PT_INTERP, 4, interp_off, 0, 0, len(interp), len(interp), 1),
        audit.PROGRAM_HEADER.pack(audit.PT_GNU_STACK, stack_flags, 0, 0, 0, 0, 0, 16),
    ))
    return header + programs + interp + b"__stack_chk_fail\x00"


def test_parse_elf_reports_mitigations_without_execution():
    report = audit.parse_elf(minimal_elf(), "fixture")
    assert report["position_independent_executable"] is True
    assert report["stack_executable"] is False
    assert report["stack_canary_reference"] is True
    assert report["gnu_relro_segment"] is False


def test_stable_read_rejects_symlink(tmp_path):
    target = tmp_path / "target"
    target.write_bytes(b"x")
    link = tmp_path / "link"
    link.symlink_to(target)
    with pytest.raises(OSError):
        audit.stable_read(link)


def test_write_exclusive_refuses_overwrite(tmp_path):
    output = tmp_path / "report.json"
    audit.write_exclusive(output, b"first")
    with pytest.raises(FileExistsError):
        audit.write_exclusive(output, b"second")
    assert output.read_bytes() == b"first"


@pytest.mark.skipif(not ROOTFS.is_dir(), reason="canonical recovered rootfs unavailable")
def test_canonical_carplay_report_matches_reviewed_artifact():
    report = audit.build_report(ROOTFS)
    assert report["schema"] == audit.SCHEMA
    assert report["canonical_sha256"] == canonical_sha256(report)
    assert report["activation"] == {
        "configured_systemd_default_uid": 0,
        "enable_link": "lib/systemd/system/multi-user.target.wants/carplay_iAP2.service",
        "enable_target": "/lib/systemd/system/carplay_iAP2.service",
        "enabled_by_multi_user_symlink": True,
        "exec_start": "/app/bin/iAP2Service-2.0",
        "exec_start_pre": "/etc/iap2_mod.sh",
        "explicit_user_directive": None,
        "restart": "always",
    }
    assert report["transport_configuration"]["normal_script_branch_modules"] == [
        "usb_f_ncm", "usb_f_iap2", "mfd-iap2"
    ]
    assert report["linkage_strings"]["app/bin/AppProjection"] == [
        "libiAP2AppFramework-2.0.so", "libCarPlayAppFramework.so"
    ]
    assert report["lineage_strings"]["app/bin/iAP2Service-2.0"] == [
        "CarPlay.LHW.230712.a", "/dev/mfd-iap2"
    ]
    assert report["lineage_strings"]["app/lib/libAirPlay.so"] == ["320.17.6"]
    assert report["lineage_strings"]["app/lib/libAirPlaySupport.so"] == [
        "CarPlayFramework/0.1.89-189.180620M.38-r8",
        "AppleCarPlay_CommunicationPlugin/320.17",
    ]
    assert {entry["cve"] for entry in report["public_comparators"]} == {
        "CVE-2024-23933", "CVE-2025-8474", "CVE-2024-37602",
        "CVE-2025-24132", "CVE-2025-30422",
    }
    assert report["transport_configuration"]["exact_module_files_bound"] is True
    airplay = report["airplay_http_plist_review"]
    request = airplay["request_processor"]
    assert request["start"] == "0xf3d1"
    assert request["end"] == "0x11a3b"
    assert request["size"] == 0x266A
    assert request["sha256"] == (
        "fccea004635853ec3d685f24815e548a227bf8f65853f5e025e4115cda0cfc10"
    )
    assert request["stack_canary_load_present"] is True
    assert request["direct_unbounded_copy_or_concatenation_callees"] == []
    assert request["bounded_text_write_callees"] == ["TruncateUTF8", "snprintf", "strlcpy"]
    body_path = airplay["request_body_to_parser_path"]
    assert body_path["body_pointer_field"] == "HTTP message + 0x518"
    assert body_path["body_length_field"] == "HTTP message + 0x530"
    parser = airplay["binary_plist_parser_review"]
    assert parser["ranges"]["CFBinaryPlistV0CreateWithData"]["sha256"] == (
        "c03a2284cb4fcc1b8fc71dd44653d9250c74e8149d285efd8b87296527c2e625"
    )
    wrap = parser["unguarded_utf16_byte_length_doubling"]
    assert wrap["instruction"] == "0x39e89: add rdx, rdx"
    assert wrap["CFStringCreateWithBytes_signed_32bit_narrowing"] == (
        "0x299eb: movsxd rsi, edx"
    )
    assert wrap["direct_out_of_bounds_read_or_copy_excluded_for_this_chain"] is True
    assert wrap["security_relevant_semantic_truncation_established"] is False
    assert wrap["cve_2025_30422_attribution_established"] is False
    assert "/pair-setup" in airplay["protocol_markers"]
    assert "CFBinaryPlistV0CreateWithData" in airplay["parser_api_markers"]
    comparators = {entry["cve"]: entry for entry in report["public_comparators"]}
    assert "CWE-121" in comparators["CVE-2025-24132"]["public_mechanism"]
    assert "physical-USB" in comparators["CVE-2025-24132"]["public_impact"]
    assert "CWE-190" in comparators["CVE-2025-30422"]["public_mechanism"]
    marshal = report["iap2_marshal_getbytes_review"]
    assert marshal["checks_aligned_length_against_remaining_bytes"] is True
    assert marshal["copies_to_fixed_stack_buffer"] is False
    assert marshal["ranges"]["iAp2MarshalGetBytes"]["sha256"] == (
        "601fc208cd6c41eb6926c782dcafcedd47c88785516c98c1290ebcdd2e08ac31"
    )
    assert report["verdict"]["generic_iap2_getbytes_unchecked_stack_copy_present"] is False
    assert report["verdict"]["airplay_setup_dispatcher_direct_unbounded_copy_present"] is False
    assert report["verdict"]["binary_plist_utf16_length_wrap_candidate_present"] is True
    assert report["verdict"]["binary_plist_utf16_direct_out_of_bounds_chain_excluded"] is True
    assert report["verdict"]["binary_plist_utf16_security_relevant_semantic_truncation_established"] is False
    assert report["verdict"]["exact_public_cve_code_match_established"] is False
    assert report["verdict"]["code_execution_observed"] is False
    assert json.loads(ARTIFACT.read_text(encoding="utf-8")) == report
