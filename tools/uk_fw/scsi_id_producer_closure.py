#!/usr/bin/env python3
"""Close ordinary recovered SCSI producer paths before the vulnerable scsi_id rule."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

from cve_2026_40225_transport_audit import (
    AuditError,
    exact_line_number,
    module_inventory,
    parse_config,
    stable_read,
    strict_json,
)
from elf_reader import Elf64

SCHEMA = "ioniq-scsi-id-producer-closure/v1"
TRANSPORT_SCHEMA = "ioniq-cve-2026-40225-transport-audit/v1"
EXPECTED_CONFIG_SHA256 = "987268a1a4b333d67c219c63b690c3828811136a7a3b203eb6f20552e82dad56"
EXPECTED_RULES_SHA256 = "5757bc1da0b3e07ee1769faa266af7720b8eef21006212051a8720c02eab5a8e"
EXPECTED_ATA_ID_SHA256 = "daea4efb76661e66bf596ceb3529598a25161f21c2d004ba48b20d6924a8d72d"
EXPECTED_MODULE_CANONICAL = "8ca3bb6ea2fcc582d8a3a517ef7124069ea4194830b00b63c893df9b494434c6"
EXPECTED_MODULE_COUNT = 160
EXPECTED_STORAGE_MODULES = [
    "lib/modules/4.1.27-abl/kernel/drivers/ata/ahci.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/ata/ahci_platform.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/ata/ata_piix.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/ata/libahci.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/ata/libahci_platform.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/ata/libata.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/ata/pata_mpiix.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/ata/pata_sch.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/scsi/scsi_mod.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/scsi/scsi_transport_spi.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/scsi/sd_mod.ko",
    "lib/modules/4.1.27-abl/kernel/drivers/usb/storage/usb-storage.ko",
]
CONFIG_EXPECTED = {
    "SCSI": "m",
    "BLK_DEV_SD": "m",
    "SCSI_SPI_ATTRS": "m",
    "SCSI_LOWLEVEL": "n",
    "SCSI_ISCSI_ATTRS": "n",
    "SCSI_FC_ATTRS": "n",
    "SCSI_SAS_ATTRS": "n",
    "SCSI_SAS_LIBSAS": "n",
    "SCSI_SRP_ATTRS": "n",
    "BLK_DEV_SR": "n",
    "CHR_DEV_ST": "n",
    "CHR_DEV_SG": "n",
    "TARGET_CORE": "n",
    "FUSION": "n",
    "FIREWIRE": "n",
    "ATA": "m",
    "USB_STORAGE": "m",
}
RULE_LINES = {
    "ata_scsi": 'KERNEL=="sd*[!0-9]|sr*", ENV{ID_SERIAL}!="?*", SUBSYSTEMS=="scsi", ATTRS{vendor}=="ATA", IMPORT{program}="ata_id --export $devnode"',
    "usb_ata_passthrough": 'KERNEL=="sd*[!0-9]|sr*", ENV{ID_SERIAL}!="?*", ATTR{removable}=="0", SUBSYSTEMS=="usb", IMPORT{program}="ata_id --export $devnode"',
    "usb_id": 'KERNEL=="sd*[!0-9]|sr*", ENV{ID_SERIAL}!="?*", SUBSYSTEMS=="usb", IMPORT{builtin}="usb_id"',
    "scsi_id": 'KERNEL=="sd*[!0-9]|sr*", ENV{ID_SERIAL}!="?*", IMPORT{program}="scsi_id --export --whitelisted -d $devnode", ENV{ID_BUS}="scsi"',
    "cciss_scsi_id": 'KERNEL=="cciss*", ENV{DEVTYPE}=="disk", ENV{ID_SERIAL}!="?*", IMPORT{program}="scsi_id --export --whitelisted -d $devnode", ENV{ID_BUS}="cciss"',
}
RANGES = {
    "ata_identity_sanitizer_calls": (0x2D1D, 0x2D82, "c91cdb89bcf2d8e7b668cea78b687e0eb31866c7854ddca5312f64834052db96"),
    "ata_property_output": (0x3182, 0x320B, "e82aef0e6aad2a25fdc79a6406dcc15eacf40ff67122998360a357ead17940a2"),
    "ata_allowed_character_predicate": (0x5AE0, 0x5B50, "b6df7075de2009d50feb6191e7a032a92dd92eedb1a9bf5446bc9a63f2e4d6c9"),
    "ata_invalid_character_replacement": (0x5B50, 0x5C30, "dac300803f02a51d13818f7cb75341c990a6b06571b075877a0ac9c1df943408"),
}
STRINGS = {
    0x674F: "ID_ATA=1",
    0x67A8: "ID_MODEL=%s\n",
    0x67B5: "ID_MODEL_ENC=%s\n",
    0x67D6: "ID_SERIAL=%s_%s\n",
    0x67E7: "ID_SERIAL_SHORT=%s\n",
    0x67FB: "ID_SERIAL=%s\n",
    0x6AC9: "#+-.:=@_",
}
PATTERNS = {
    "model_sanitizer_call": ("ata_identity_sanitizer_calls", bytes.fromhex("4c89f7e8082e0000")),
    "serial_sanitizer_call": ("ata_identity_sanitizer_calls", bytes.fromhex("4c89efe8e72d0000")),
    "revision_sanitizer_call": ("ata_identity_sanitizer_calls", bytes.fromhex("4c89f7e8ce2d0000")),
    "invalid_character_becomes_underscore": ("ata_invalid_character_replacement", bytes.fromhex("41c604245f")),
    "allowed_extra_character_lookup": ("ata_allowed_character_predicate", bytes.fromhex("488d3daf0f0000")),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_canonical(report: dict[str, Any], schema: str, label: str) -> str:
    if report.get("schema") != schema:
        raise AuditError(f"{label} schema must be {schema}")
    supplied = report.get("canonical_sha256")
    if not isinstance(supplied, str) or len(supplied) != 64:
        raise AuditError(f"{label} canonical_sha256 is malformed")
    subject = dict(report)
    subject.pop("canonical_sha256")
    computed = digest(json.dumps(subject, separators=(",", ":"), sort_keys=True).encode())
    if supplied != computed:
        raise AuditError(f"{label} canonical_sha256 mismatch")
    return supplied


def read_string(elf: Elf64, address: int) -> str:
    data = elf.read_vaddr(address, 128)
    if data is None or b"\x00" not in data:
        raise AuditError(f"unmapped or unterminated ata_id string at 0x{address:x}")
    return data.split(b"\x00", 1)[0].decode("ascii", "strict")


def build_report(rootfs: Path, config_path: Path, transport_path: Path) -> dict[str, Any]:
    config_data = stable_read(config_path)
    if digest(config_data) != EXPECTED_CONFIG_SHA256:
        raise AuditError("kernel config identity mismatch")
    config = parse_config(config_data)
    for name, expected in CONFIG_EXPECTED.items():
        if config.get(name) != expected:
            raise AuditError(f"CONFIG_{name}: expected {expected}, got {config.get(name)!r}")

    rules_path = rootfs / "lib/udev/rules.d/60-persistent-storage.rules"
    rules_data = stable_read(rules_path)
    if digest(rules_data) != EXPECTED_RULES_SHA256:
        raise AuditError("persistent storage rule identity mismatch")
    line_numbers = {
        name: exact_line_number(rules_data, line, "persistent storage rules")
        for name, line in RULE_LINES.items()
    }
    if not (
        line_numbers["ata_scsi"]
        < line_numbers["usb_ata_passthrough"]
        < line_numbers["usb_id"]
        < line_numbers["scsi_id"]
        < line_numbers["cciss_scsi_id"]
    ):
        raise AuditError("reviewed storage rule order differs")

    modules, module_canonical = module_inventory(rootfs)
    if len(modules) != EXPECTED_MODULE_COUNT or module_canonical != EXPECTED_MODULE_CANONICAL:
        raise AuditError("complete module inventory identity mismatch")
    storage_modules = sorted(
        record["path"]
        for record in modules
        if record["path"].startswith("lib/modules/4.1.27-abl/kernel/drivers/ata/")
        or record["path"].startswith("lib/modules/4.1.27-abl/kernel/drivers/scsi/")
        or record["path"].endswith("/drivers/usb/storage/usb-storage.ko")
    )
    if storage_modules != EXPECTED_STORAGE_MODULES:
        raise AuditError("ATA/SCSI/USB-storage module subset differs")

    transport_data = stable_read(transport_path)
    transport = strict_json(transport_data, transport_path)
    transport_canonical = validate_canonical(transport, TRANSPORT_SCHEMA, "transport report")
    if transport.get("transports", {}).get("ordinary_usb_mass_storage_to_scsi_id", {}).get("state") != "suppressed-by-prior-usb-id":
        raise AuditError("ordinary USB transport conclusion differs")

    ata_path = rootfs / "lib/udev/ata_id"
    ata_data = stable_read(ata_path)
    if digest(ata_data) != EXPECTED_ATA_ID_SHA256:
        raise AuditError("ata_id identity mismatch")
    elf = Elf64(str(ata_path))
    if elf.data != ata_data:
        raise AuditError("ata_id changed between stable read and ELF parse")
    range_records: dict[str, Any] = {}
    range_bytes: dict[str, bytes] = {}
    for name, (start, end, expected_hash) in RANGES.items():
        data = elf.read_vaddr(start, end - start)
        if data is None or digest(data) != expected_hash:
            raise AuditError(f"ata_id range identity mismatch: {name}")
        range_bytes[name] = data
        range_records[name] = {
            "start": hex(start),
            "end": hex(end),
            "size": end - start,
            "sha256": expected_hash,
        }
    pattern_offsets: dict[str, str] = {}
    for name, (range_name, pattern) in PATTERNS.items():
        data = range_bytes[range_name]
        offset = data.find(pattern)
        if offset < 0 or data.find(pattern, offset + 1) >= 0:
            raise AuditError(f"ata_id critical pattern absent or non-unique: {name}")
        pattern_offsets[name] = hex(offset)
    strings = {f"0x{address:x}": read_string(elf, address) for address in sorted(STRINGS)}
    expected_strings = {f"0x{address:x}": value for address, value in sorted(STRINGS.items())}
    if strings != expected_strings:
        raise AuditError("ata_id reviewed strings differ")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "inputs": {
            "kernel_config": {"sha256": digest(config_data), "bytes": len(config_data)},
            "persistent_storage_rules": {"sha256": digest(rules_data), "bytes": len(rules_data)},
            "ata_id": {"sha256": digest(ata_data), "bytes": len(ata_data)},
            "transport_report": {"sha256": digest(transport_data), "canonical_sha256": transport_canonical},
            "module_inventory": {"count": len(modules), "canonical_sha256": module_canonical},
        },
        "config": {name: config[name] for name in sorted(CONFIG_EXPECTED)},
        "rule_lines": line_numbers,
        "storage_modules": storage_modules,
        "ata_id_review": {
            "ranges": range_records,
            "pattern_offsets": pattern_offsets,
            "strings": strings,
            "identity_fields_sanitized_before_output": ["model", "serial", "revision"],
            "allowed_characters": "ASCII alphanumeric plus #+-.:=@_",
            "invalid_single_byte_replacement": "_",
            "control_characters_preserved_in_id_serial": False,
        },
        "producer_matrix": {
            "ordinary_usb_mass_storage": {
                "state": "suppressed-by-prior-usb-id",
                "basis": "accepted exact no-iSerial VM control and rule 31 before rule 34",
            },
            "ordinary_ata_disk": {
                "state": "suppressed-by-prior-sanitizing-ata-id",
                "basis": "rule 22 before rule 34; exact ata_id sanitizes model and serial before ID_SERIAL output",
            },
            "scsi_optical": {"state": "not-built", "basis": "CONFIG_BLK_DEV_SR=n"},
            "scsi_tape": {"state": "not-built", "basis": "CONFIG_CHR_DEV_ST=n"},
            "scsi_generic": {"state": "not-built", "basis": "CONFIG_CHR_DEV_SG=n"},
            "iscsi": {"state": "not-built", "basis": "CONFIG_SCSI_ISCSI_ATTRS=n and no module"},
            "sas_fc_srp": {"state": "not-built", "basis": "SAS/FC/SRP attributes and libsas disabled"},
            "firewire_scsi": {"state": "not-built", "basis": "CONFIG_FIREWIRE=n"},
            "cciss": {"state": "not-built", "basis": "CONFIG_SCSI_LOWLEVEL=n and no cciss module"},
            "other_low_level_scsi": {"state": "not-built", "basis": "CONFIG_SCSI_LOWLEVEL=n and complete module subset"},
            "malformed_identity_or_prior_import_failure": {
                "state": "unproved",
                "basis": "normal precedence does not prove behavior when ata_id/usb_id fails after enumeration",
            },
        },
        "verdict": {
            "complete_recovered_scsi_producer_classes_enumerated": True,
            "ordinary_usb_reaches_scsi_id": False,
            "ordinary_ata_reaches_scsi_id": False,
            "ordinary_ata_control_characters_reach_id_serial": False,
            "stock_external_scsi_id_property_injection_demonstrated": False,
            "root_access_demonstrated": False,
            "persistence_demonstrated": False,
        },
        "boundaries": [
            "This closes normal recovered producer classes; it does not prove every malformed enumeration or prior-import failure path.",
            "Enabled ATA controllers are not evidence that an externally accessible production SATA/PATA port exists.",
            "A different installed owner-unit kernel, module set, or rule set remains unverified.",
            "No device, VM, ioctl, helper, uevent, property, service, network, target write, root transition, or persistence action was executed.",
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
    parser.add_argument("--rootfs", type=Path, required=True)
    parser.add_argument("--kernel-config", type=Path, required=True)
    parser.add_argument("--transport-report", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report(args.rootfs, args.kernel_config, args.transport_report)
        rendered = json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        if args.output:
            write_exclusive(args.output, rendered)
        else:
            sys.stdout.buffer.write(rendered)
    except (AuditError, OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
