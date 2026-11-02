import json
import struct
from pathlib import Path

import pytest

from tools.uk_fw import txe_first_fixed_module_inventory as inventory


ROOT = Path(__file__).resolve().parents[1]
AFFECTED = ROOT / "work/decrypted-eu-260128/extracted-safe/update/abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin"
FIRST_FIXED = ROOT / "work/online-fixed-txe-search-20261102/X541NA-AS.321-ifwi.bin"
ARTIFACT = ROOT / "evidence/artifacts/update-candidates/txe-first-fixed-module-inventory.json"


def test_differing_byte_count_includes_one_byte_delta():
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
    event_review = report["vfs_event_ordinal_delta_review"]
    assert event_review["module_count"] == 4
    assert event_review["site_count"] == 11
    assert event_review["message_dword_zero"] == 0x02000200
    assert event_review["all_reviewed_event_ordinals_increment_by_one"] is True
    assert event_review["submit_wrapper_stores_first_argument_dword_at_message_offset_zero"] is True
    assert event_review["constructor_stores_second_argument_low_byte_at_message_offset_four"] is True
    assert event_review["message_offset_four_role"].startswith("VFS event ordinal")
    assert event_review["message_offset_five_role"].startswith("separate payload-length byte")
    assert event_review["kernel_input_geometry_sha256"] == "e527f5d670d725147c91ea62459bfde546253bbd8ecab5c7f1602ba49061f96a"
    assert [site["affected_event_ordinal"] for site in event_review["sites"]] == [
        0x13, 0x15, 0x16, 0x0E, 0x0B, 0x0D, 0x10, 0x18, 0x0E, 0x13, 0x15,
    ]
    inserted_event = event_review["first_fixed_inserted_event_producer"]
    assert inserted_event["module"] == "maestro"
    assert inserted_event["inserted_event_ordinal"] == 0x0B
    assert inserted_event["recipient_process"] == "vfs"
    assert inserted_event["function_sha256"] == "0be9ef6f8034023db17a6c6740045b7523198fdb73d11098fb92e49d67c0e903"
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
    assert ordinal["site_count"] == 16
    assert ordinal["all_reviewed_values_follow_expected_translation"] is True
    assert ordinal["affected_to_first_fixed_value_counts"] == {
        "0xc4_to_0xc6": 2,
        "0xc5_to_0xc7": 2,
        "0xc6_to_0xc8": 2,
        "0xc7_to_0xca": 1,
        "0xc8_to_0xcb": 2,
        "0x100_to_0x103": 2,
        "0x101_to_0x104": 1,
        "0x102_to_0x105": 4,
    }
    assert [site["value"] for site in ordinal["first_fixed_inserted_numeric_ordinals"]] == [0xC4, 0xC5, 0xC9]
    producers = kernel_review["shifted_memory_status_producers"]
    assert producers["status_0xfd_to_0x100"]["affected_direct_call_sites"] == [0x85AA6, 0x85AE9, 0x88118]
    assert producers["status_0xfd_to_0x100"]["first_fixed_direct_call_sites"] == [0x85E86, 0x85EC9, 0x880BA]
    assert producers["status_0xfe_to_0x101"]["affected_direct_call_sites"] == [0x854CA]
    assert producers["status_0xfe_to_0x101"]["first_fixed_direct_call_sites"] == [0x85936]
    assert producers["status_0xfd_to_0x100"]["affected_sha256"] == "6a5da5501dac433546a2c08220ddff17b80ef4160549b9c6cde38da2a9f8df19"
    assert producers["status_0xfd_to_0x100"]["first_fixed_sha256"] == "b12ad8b0c4e784655e76de10ba1977c906bb55c14d0b7eccfd2c62479b96d930"
    assert producers["status_0xfe_to_0x101"]["affected_sha256"] == "1e17058b43cdf950a3abdcb1c729565d66171a19d319c431fc8843c7903a2063"
    assert producers["status_0xfe_to_0x101"]["first_fixed_sha256"] == "004b911c32d58e78d2ffb3aab766308fb6b9168b35781208021eeabeb2f0f10e"
    role_map = kernel_review["kernel_status_site_role_map"]
    assert role_map["producer_site_count"] == 3
    assert role_map["consumer_site_count"] == 12
    assert role_map["covers_complete_fifteen_site_census"] is True
    assert len(role_map["generic_completion_filter_sites"]) == 10
    assert [site["role"] for site in role_map["producer_sites"]] == [
        "list_registration_return",
        "selector_0x10_handler_immediate_return",
        "linked_tail_helper_return",
    ]
    assert role_map["dispatch_queue_continue"]["affected_runtime_address"] == 0x8EC67
    census = kernel_review["kernel_global_immediate_census"]
    assert census["affected_total_site_count"] == 15
    assert census["first_fixed_total_site_count"] == 15
    assert census["affected_mov_edx_0xff"] == [0x8C08A]
    assert census["first_fixed_mov_edx_0x102"] == [0x8C02C]
    assert len(census["affected_cmp_eax_0xff"]) == 12
    assert len(census["first_fixed_cmp_eax_0x102"]) == 12
    identity = report["vfs_process_identity_review"]
    assert identity["vfs_process_identifier"] == 0x0200
    assert identity["vfs_current_identity_value"] == 0x02000200
    assert identity["pm_process_identifier"] == 0x0100
    assert identity["pm_current_identity_value"] == 0x01000100
    assert [site["export_body_sha256"] for site in identity["syslib_current_identity_exports"]] == [
        "7f59ad5a4926a195de4fba5e9ec57eb623c56238ceddd8dc7995fb9294a5e235",
        "7f59ad5a4926a195de4fba5e9ec57eb623c56238ceddd8dc7995fb9294a5e235",
    ]
    assert [site["tls_value_source"] for site in identity["syslib_current_identity_exports"]] == [
        "dereference of gs:0 minus four bytes", "dereference of gs:0 minus four bytes",
    ]
    assert [site["expected_current_identity"] for site in identity["startup_identity_checks"]] == [
        0x02000200, 0x02000200, 0x01000100, 0x01000100,
    ]
    assert [site["current_identity_export_stub_runtime_address"] for site in identity["startup_identity_checks"]] == [
        0x67B2, 0x67B7, 0x67B2, 0x67B7,
    ]
    assert identity["vfs_process_attributes"]["affected"]["user_id"] == 0
    assert identity["vfs_process_attributes"]["first_fixed"]["trusted_send_receive_sender"] is True
    assert identity["pm_process_attributes"]["affected"]["user_id"] == 0x53
    assert identity["pm_process_attributes"]["first_fixed"]["trusted_send_receive_sender"] is False
    ipc = report["ipc_drv_stack_initialization_review"]
    assert ipc["affected_callback_runtime_range"] == [0x274BD, 0x2780D]
    assert ipc["first_fixed_callback_runtime_range"] == [0x274E5, 0x27849]
    assert ipc["affected_callback_sha256"] == "b7e498a3daa735910a68d49d69beb32b0159611b301e304bf0b5c4ac04c569b9"
    assert ipc["first_fixed_callback_sha256"] == "31079b2150e42e39209b3eed814d1c4de2bfc7875003a7ec8b85f05b41f2436f"
    assert ipc["affected_call_sites"]["zero_fill_0x103d"] == []
    assert ipc["first_fixed_call_sites"]["zero_fill_0x103d"] == [0x27516]
    assert ipc["first_fixed_new_initialization"]["size"] == 0x88
    assert ipc["shared_buffer_use"]["payload_bound"] == 0x80
    assert ipc["shared_buffer_use"]["fixed_transfer_size"] == 0x88
    assert ipc["special_file_metadata"]["major"] == 39
    assert [entry["name"] for entry in ipc["special_file_metadata"]["entries"]] == [
        "ipc_boot", "ipc_mctp", "ipc_dd", "ipc_pmc", "ipc_prtc", "ipc_iun",
    ]
    assert ipc["static_context_minor_groups"] == [[1, 2, 3], [4, 5], [6]]
    assert [site["operation_table_index"] for site in ipc["syslib_event_0xf4_dispatch_sites"]] == [2, 2]
    assert [site["body_runtime_address"] for site in ipc["syslib_fixed_transfer_exports"]] == [
        0x7849, 0x784E,
    ]
    assert [site["alternate_transfer_syscall_selector"] for site in ipc["syslib_fixed_transfer_exports"]] == [7, 7]
    assert [site["alternate_transfer_syscall_argument_size"] for site in ipc["syslib_fixed_transfer_exports"]] == [0x20, 0x20]
    selector_7 = ipc["kernel_selector_7_transfer_handlers"]
    assert [site["handler_runtime_range"] for site in selector_7] == [
        [0x8BBC2, 0x8BCE1], [0x8BB64, 0x8BC83],
    ]
    assert [site["process_identifier_argument_offset"] for site in selector_7] == [0x0C, 0x0C]
    assert [site["accepted_process_table_index_range"] for site in selector_7] == [[1, 47], [1, 47]]
    transfer_role = ipc["message_dword_zero_transfer_role"]
    assert transfer_role["value"] == 0x02000200
    assert transfer_role["low_16_bits_consumed_by_transfer_wrapper"] == 0x0200
    assert transfer_role["kernel_selector_7_process_identifier"] == 0x0200
    assert transfer_role["kernel_process_table_index"] == 2
    assert transfer_role["vendor_process_or_recipient_name"] == "vfs"
    assert json.loads(ARTIFACT.read_text(encoding="utf-8")) == report
