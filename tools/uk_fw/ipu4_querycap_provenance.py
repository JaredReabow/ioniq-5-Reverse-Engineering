#!/usr/bin/env python3
"""Bind recovered Intel IPU4 QUERYCAP card metadata to its exact producer."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

from cve_2026_40225_transport_audit import AuditError, stable_read, strict_json
from elf_reader import Elf64

SCHEMA = "ioniq-ipu4-querycap-provenance/v1"
TRANSPORT_SCHEMA = "ioniq-cve-2026-40225-transport-audit/v1"
EXPECTED_VMLINUX_SHA256 = "f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b"
EXPECTED_KALLSYMS_SHA256 = "2cfba917c1c8e7444e393e8d94ebfe367e2ba348be4f35ce10fbb331822e3c1f"
QUERYCAP_START = 0xFFFFFFFF81432125
QUERYCAP_END = 0xFFFFFFFF814321CD
QUERYCAP_SHA256 = "ecdb0fb41f9152ba713928857ca552e9645baaf94be49b20657624d7abae9a35"
PRODUCER_START = 0xFFFFFFFF8142B35E
PRODUCER_END = 0xFFFFFFFF8142B427
PRODUCER_SHA256 = "ff54919e0ebea913c993f7ef499a634a1cdd387824aa459f7954d60ddc922193"
SYMBOLS = {
    "intel_ipu4_isys_vidioc_querycap": QUERYCAP_START,
    "fmt_mp_to_sp": QUERYCAP_END,
    "isys_register_devices": PRODUCER_START,
    "isys_probe": 0xFFFFFFFF8142BB57,
    "video_drvdata": 0xFFFFFFFF81431EA6,
    "strlcpy": 0xFFFFFFFF8120532E,
}
STRINGS = {
    0xFFFFFFFF818805C8: "intel-ipu4-isys",
    0xFFFFFFFF81881E7D: "ipu4/Broxton B",
    0xFFFFFFFF81881E8C: "ipu5/A",
    0xFFFFFFFF81881E93: "pci:%s",
}
QUERYCAP_PATTERNS = {
    "video_drvdata_call": bytes.fromhex("e872fdffff"),
    "driver_destination_and_length": bytes.fromhex("ba10000000"),
    "card_pointer_and_copy_geometry": bytes.fromhex(
        "498b8424a8070000488d7b10ba20000000488db020030000"
    ),
    "bus_pointer_and_copy_geometry": bytes.fromhex(
        "498b8424a8070000488d7b30ba20000000488db068030000"
    ),
}
PRODUCER_PATTERNS = {
    "default_ipu5_string": bytes.fromhex("48c7c68c1e8881"),
    "card_destination_offset_0x320": bytes.fromhex("488d9f20030000"),
    "pci_device_id_load": bytes.fromhex("668b403e"),
    "pci_device_id_mask": bytes.fromhex("80e4bf"),
    "pci_device_id_compare_0x1a88": bytes.fromhex("663d881a"),
    "ipu4_string_candidate": bytes.fromhex("48c7c07d1e8881"),
    "conditional_string_select": bytes.fromhex("480f44f0"),
    "card_strlcpy_call": bytes.fromhex("e85a9fddff"),
    "bus_destination_offset_0x368": bytes.fromhex("498dbf68030000"),
    "pci_bus_format": bytes.fromhex("48c7c2931e8881"),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_kallsyms(data: bytes) -> dict[str, int]:
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise AuditError(f"kallsyms is not strict UTF-8: {exc}") from exc
    result: dict[str, int] = {}
    for line in text.splitlines():
        fields = line.split("\t")
        if len(fields) < 3:
            raise AuditError(f"malformed kallsyms line: {line!r}")
        try:
            address = int(fields[0], 16)
        except ValueError as exc:
            raise AuditError(f"malformed kallsyms address: {fields[0]!r}") from exc
        name = fields[2]
        if name not in SYMBOLS:
            continue
        if name in result:
            raise AuditError(f"duplicate reviewed kallsyms symbol: {name}")
        result[name] = address
    return result


def require_unique_patterns(data: bytes, patterns: dict[str, bytes], label: str) -> dict[str, int]:
    offsets: dict[str, int] = {}
    for name, pattern in patterns.items():
        first = data.find(pattern)
        if first < 0 or data.find(pattern, first + 1) >= 0:
            raise AuditError(f"{label}: pattern {name} is absent or non-unique")
        offsets[name] = first
    return offsets


def read_c_string(elf: Elf64, address: int, limit: int = 128) -> str:
    data = elf.read_vaddr(address, limit)
    if data is None or b"\x00" not in data:
        raise AuditError(f"unterminated or unmapped string at 0x{address:x}")
    raw = data.split(b"\x00", 1)[0]
    try:
        return raw.decode("ascii", "strict")
    except UnicodeDecodeError as exc:
        raise AuditError(f"non-ASCII string at 0x{address:x}") from exc


def validate_transport(report: dict[str, Any]) -> str:
    if report.get("schema") != TRANSPORT_SCHEMA:
        raise AuditError(f"transport schema must be {TRANSPORT_SCHEMA}")
    supplied = report.get("canonical_sha256")
    if not isinstance(supplied, str) or len(supplied) != 64:
        raise AuditError("transport canonical_sha256 is malformed")
    subject = dict(report)
    subject.pop("canonical_sha256")
    computed = digest(json.dumps(subject, separators=(",", ":"), sort_keys=True).encode())
    if supplied != computed:
        raise AuditError("transport canonical_sha256 mismatch")
    transports = report.get("transports")
    if not isinstance(transports, dict):
        raise AuditError("transport matrix is missing")
    usb_v4l = transports.get("generic_usb_v4l_to_v4l_id")
    if not isinstance(usb_v4l, dict) or usb_v4l.get("state") != "not-built":
        raise AuditError("generic USB V4L transport is not accepted as not-built")
    return supplied


def build_report(vmlinux_path: Path, kallsyms_path: Path, transport_path: Path) -> dict[str, Any]:
    vmlinux_data = stable_read(vmlinux_path)
    kallsyms_data = stable_read(kallsyms_path)
    transport_data = stable_read(transport_path)
    if digest(vmlinux_data) != EXPECTED_VMLINUX_SHA256:
        raise AuditError("vmlinux identity mismatch")
    if digest(kallsyms_data) != EXPECTED_KALLSYMS_SHA256:
        raise AuditError("kallsyms identity mismatch")
    symbols = parse_kallsyms(kallsyms_data)
    for name, expected in SYMBOLS.items():
        if symbols.get(name) != expected:
            raise AuditError(
                f"symbol {name}: expected 0x{expected:x}, observed {symbols.get(name)!r}"
            )
    transport = strict_json(transport_data, transport_path)
    transport_canonical = validate_transport(transport)

    elf = Elf64(str(vmlinux_path))
    if elf.data != vmlinux_data:
        raise AuditError("vmlinux changed between stable read and ELF parse")
    querycap = elf.read_vaddr(QUERYCAP_START, QUERYCAP_END - QUERYCAP_START)
    producer = elf.read_vaddr(PRODUCER_START, PRODUCER_END - PRODUCER_START)
    if querycap is None or producer is None:
        raise AuditError("reviewed function range is not mapped")
    if digest(querycap) != QUERYCAP_SHA256:
        raise AuditError("querycap range identity mismatch")
    if digest(producer) != PRODUCER_SHA256:
        raise AuditError("registration producer range identity mismatch")
    query_offsets = require_unique_patterns(querycap, QUERYCAP_PATTERNS, "querycap")
    producer_offsets = require_unique_patterns(producer, PRODUCER_PATTERNS, "producer")
    resolved_strings = {
        f"0x{address:x}": read_c_string(elf, address)
        for address in sorted(STRINGS)
    }
    expected_strings = {f"0x{address:x}": value for address, value in sorted(STRINGS.items())}
    if resolved_strings != expected_strings:
        raise AuditError("resolved IPU4 strings differ")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "inputs": {
            "vmlinux": {"sha256": digest(vmlinux_data), "bytes": len(vmlinux_data)},
            "kallsyms": {"sha256": digest(kallsyms_data), "bytes": len(kallsyms_data)},
            "transport_report": {
                "sha256": digest(transport_data),
                "canonical_sha256": transport_canonical,
            },
        },
        "ranges": {
            "querycap": {
                "start": hex(QUERYCAP_START),
                "end": hex(QUERYCAP_END),
                "size": len(querycap),
                "sha256": digest(querycap),
                "next_symbol": "fmt_mp_to_sp",
            },
            "card_bus_producer_prefix": {
                "start": hex(PRODUCER_START),
                "end": hex(PRODUCER_END),
                "size": len(producer),
                "sha256": digest(producer),
                "function": "isys_register_devices",
            },
        },
        "pattern_offsets": {
            "querycap": {name: hex(offset) for name, offset in query_offsets.items()},
            "producer": {name: hex(offset) for name, offset in producer_offsets.items()},
        },
        "strings": resolved_strings,
        "dataflow": {
            "driver": {
                "destination": "v4l2_capability.driver (+0x00)",
                "source": "fixed rodata 'intel-ipu4-isys'",
                "maximum_copy": 16,
            },
            "card": {
                "destination": "v4l2_capability.card (+0x10)",
                "query_source": "video_drvdata->isys pointer at +0x7a8, then isys +0x320",
                "producer_destination": "isys +0x320",
                "producer_sources": ["ipu4/Broxton B", "ipu5/A"],
                "selector": "masked PCI device ID equals 0x1a88 selects ipu4/Broxton B; otherwise ipu5/A",
                "maximum_copy": 32,
            },
            "bus_info": {
                "destination": "v4l2_capability.bus_info (+0x30)",
                "query_source": "isys +0x368",
                "producer_destination": "isys +0x368",
                "producer_format": "pci:%s",
                "maximum_copy": 32,
            },
        },
        "verdict": {
            "generic_usb_v4l_transport_built": False,
            "ipu4_card_selected_from_fixed_driver_strings": True,
            "ipu4_card_selected_by_pci_identity": True,
            "camera_pixels_control_querycap_card": False,
            "sensor_stream_metadata_controls_querycap_card": False,
            "usb_descriptor_controls_ipu4_querycap_card": False,
            "stock_external_v4l_product_injection_demonstrated": False,
            "root_access_demonstrated": False,
        },
        "boundaries": [
            "The reviewed function returns fixed driver identity metadata; it does not parse image pixels or sensor stream payloads.",
            "This closes the public USB-descriptor V4L route for the enabled recovered IPU4 querycap implementation, not every hypothetical vendor camera driver.",
            "Physical owner-unit identity and any alternate installed module remain unverified until a disconnected bench capture.",
            "No ioctl, device, helper, VM, property injection, unit activation, or root action was executed by this audit.",
        ],
    }
    canonical = json.dumps(report, separators=(",", ":"), sort_keys=True).encode()
    report["canonical_sha256"] = digest(canonical)
    return report


def write_exclusive(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vmlinux", type=Path, required=True)
    parser.add_argument("--kallsyms", type=Path, required=True)
    parser.add_argument("--transport-report", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report(args.vmlinux, args.kallsyms, args.transport_report)
        rendered = json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        if args.output:
            write_exclusive(args.output, rendered)
        else:
            sys.stdout.buffer.write(rendered)
    except (AuditError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
