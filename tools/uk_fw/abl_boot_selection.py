#!/usr/bin/env python3
"""Freeze the exact ABL boot-option, forward-fallback, and _sub boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import struct
import subprocess
import sys
import tarfile
from pathlib import Path

SCHEMA = "abl-boot-selection/v1"
VERSION = "1.1.0"
UPDATE_SIZE = 42_101_042
UPDATE_SHA256 = "1e67344a714708733a9158a52ef5d4def95b126e5725d070669ea64e0644c4c8"
ABL_MEMBER = "abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin"
ABL_SHA256 = "f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac"
ROOTFS_SIZE = 879_109_759
ROOTFS_SHA256 = "423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84"
ROOT_MEMBERS = {
    "lib/systemd/esinit": {
        "size": 17_894,
        "mode": 0o755,
        "uid": 0,
        "gid": 0,
        "sha256": "9f39947ec144322b29c0366bb681f0452ae3696139589bc2f4a2f05bf44afa52",
    },
    "app/share/AppEngineerMode/constants/iasimage_update.sh": {
        "size": 1_224,
        "mode": 0o644,
        "uid": 0,
        "gid": 0,
        "sha256": "a22efabdf3604cc57777fdba10ea00119bdc4721a5df8cecc1669b8480a78c2f",
    },
}
CONFIG_OFFSET = 0x102E6A
CONFIG_TOTAL_SIZE = 0xA88
CONFIG_SHA256 = "c9a592afcecb6adefc678d5503f98e946370948264690ef46c2bf39a7c718a9a"
STAGE_SHA256 = "3491be59ef865cb376131b02fa1ff6941e37d1c87ae3c4cf7969b5364785b3c2"
SBL_COMMIT = "5f5c14b10ae6bd3cd0cf7e274142767dc2635a06"
SBL_FILES = {
    "Platform/ApollolakeBoardPkg/Include/ConfigDataDefs.h": "40e988111adf1c01da3598a163f6041eca49b4a55ad5dc4b06898d046f40971c",
    "Platform/ApollolakeBoardPkg/Library/Stage1BBoardInitLib/Stage1BBoardInitLib.c": "e4497d268b295720a3ad40239fa5702b2ba7b72d7128bc3fa31a485337288d9d",
}
STAGE_RANGES = {
    "boot_record_callback": (0xAE16, 0xAFF7, "aa556ed1727d5ea006f9211c536fdc387f117665291b929871b07cbb2b0f0e89"),
    "boot_dispatch_tail": (0x6BA, 0x70D, "bc0cbc9edeeebf6249d1dfa868827cbc6d18fade68d8ae6d03f221665e52144b"),
    "cmdline_builder": (0xBC60, 0xBCD9, "62c47e95d1a3637d3bbc6e9c3cb6e3ab8d775f1af28d482f615b125cb1eb4892"),
    "boot_iterator_wrapper": (0xB034, 0xB05C, "c6fd0193fe3ef42ea3de8d622c218ae9c39f4af9aba828f30291ebb242ac8a46"),
    "config_iterator": (0xD576, 0xD68B, "6272cdba6a4cc163d822e6e92defb5508ded69ed86ad2ab969937bbea3c4789d"),
}


class Failure(Exception):
    pass


def canonical(name: str) -> str | None:
    if name == ".":
        return None
    if not isinstance(name, str) or not name or name.startswith("/") or "\\" in name or "\0" in name:
        raise Failure("unsafe archive member spelling")
    parts = name.split("/")
    if parts and parts[0] == ".":
        parts = parts[1:]
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise Failure("unsafe archive member component")
    return "/".join(parts)


def _identity(st: os.stat_result) -> tuple[int, int, int, int, int]:
    return st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns


def archive_members(path: Path, total: int, digest: str, wanted: dict[str, dict]) -> dict[str, bytes]:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise Failure(f"cannot safely open archive: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size != total:
            raise Failure("archive size/type mismatch")
        h = hashlib.sha256()
        left = total
        while left:
            chunk = os.read(fd, min(left, 1 << 20))
            if not chunk:
                raise Failure("short archive read")
            h.update(chunk)
            left -= len(chunk)
        if h.hexdigest() != digest or _identity(before) != _identity(os.fstat(fd)):
            raise Failure("archive identity mismatch")
        os.lseek(fd, 0, os.SEEK_SET)
        found: dict[str, bytes] = {}
        with os.fdopen(os.dup(fd), "rb") as stream:
            try:
                with tarfile.open(fileobj=stream, mode="r:gz") as archive:
                    seen: set[str] = set()
                    for member in archive:
                        name = canonical(member.name)
                        if name is None:
                            continue
                        if name in seen:
                            raise Failure("duplicate canonical archive identity")
                        seen.add(name)
                        spec = wanted.get(name)
                        if spec is None:
                            continue
                        if (
                            not member.isreg()
                            or member.size != spec["size"]
                            or member.mode & 0o7777 != spec["mode"]
                            or member.uid != spec["uid"]
                            or member.gid != spec["gid"]
                        ):
                            raise Failure(f"selected archive member metadata drift: {name}")
                        source = archive.extractfile(member)
                        if source is None:
                            raise Failure(f"selected archive member unreadable: {name}")
                        data = source.read(member.size + 1)
                        if len(data) != member.size or hashlib.sha256(data).hexdigest() != spec["sha256"]:
                            raise Failure(f"selected archive member content drift: {name}")
                        found[name] = data
            except (tarfile.TarError, OSError, EOFError) as exc:
                raise Failure(f"archive parse failure: {exc}") from exc
        if set(found) != set(wanted) or _identity(before) != _identity(os.fstat(fd)):
            raise Failure("selected archive multiplicity/change")
        return found
    finally:
        os.close(fd)


def lz4_block(raw: bytes, expected: int) -> bytes:
    pos = 0
    out = bytearray()
    while len(out) < expected:
        if pos >= len(raw):
            raise Failure("truncated ABL LZ4 token")
        token = raw[pos]
        pos += 1
        literal = token >> 4
        if literal == 15:
            while True:
                if pos >= len(raw):
                    raise Failure("truncated ABL LZ4 literal length")
                value = raw[pos]
                pos += 1
                literal += value
                if value != 255:
                    break
        if pos + literal > len(raw) or len(out) + literal > expected:
            raise Failure("ABL LZ4 literal bounds drift")
        out += raw[pos : pos + literal]
        pos += literal
        if len(out) == expected:
            break
        if pos + 2 > len(raw):
            raise Failure("truncated ABL LZ4 offset")
        offset = raw[pos] | raw[pos + 1] << 8
        pos += 2
        if offset == 0 or offset > len(out):
            raise Failure("invalid ABL LZ4 offset")
        match = (token & 15) + 4
        if (token & 15) == 15:
            while True:
                if pos >= len(raw):
                    raise Failure("truncated ABL LZ4 match length")
                value = raw[pos]
                pos += 1
                match += value
                if value != 255:
                    break
        if len(out) + match > expected:
            raise Failure("ABL LZ4 match bounds drift")
        for _ in range(match):
            out.append(out[-offset])
    if pos != len(raw):
        raise Failure("ABL LZ4 trailing compressed bytes")
    return bytes(out)


def crc32c(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = (crc >> 1) ^ (0x82F63B78 if crc & 1 else 0)
    return crc


def c_string(data: bytes, start: int, end: int) -> tuple[str, int]:
    stop = data.find(b"\0", start, end)
    if stop < 0:
        raise Failure("unterminated ABL config string")
    try:
        text = data[start:stop].decode("ascii")
    except UnicodeDecodeError as exc:
        raise Failure("non-ASCII ABL config string") from exc
    return text, stop + 1


def config_records(payload: bytes) -> list[dict]:
    records = []
    pos = 0
    while pos + 4 <= len(payload):
        header = struct.unpack_from("<I", payload, pos)[0]
        size = header & 0xFFC
        if size == 0:
            break
        if size < 8 or pos + size > len(payload):
            raise Failure("ABL config record bounds drift")
        variant = header & 3
        descriptor = pos + 4 + 4 * variant
        if descriptor + 6 > pos + size:
            raise Failure("ABL config descriptor bounds drift")
        item = {
            "index": len(records),
            "offset": pos,
            "size": size,
            "tag": (header >> 20) & 0xFF,
            "variant": variant,
            "descriptor_kind": payload[descriptor],
            "descriptor_instance": payload[descriptor + 1],
            "sha256": hashlib.sha256(payload[pos : pos + size]).hexdigest(),
        }
        string_start = descriptor + 6
        # Only the leading boot records are interpreted here. Later tag
        # payloads use unrelated binary layouts and remain hash-bound bytes.
        if len(records) < 5 and string_start < pos + size and payload[string_start] != 0:
            first, next_pos = c_string(payload, string_start, pos + size)
            item["name"] = first
            if next_pos < pos + size and payload[next_pos] != 0:
                second, _ = c_string(payload, next_pos, pos + size)
                item["predicate"] = second
        records.append(item)
        pos += size
    if pos > len(payload):
        raise Failure("ABL config record extent drift")
    return records


def one_count(data: bytes, needle: bytes, label: str) -> None:
    if data.count(needle) != 1:
        raise Failure(f"semantic anchor multiplicity drift: {label}")


def git_blob(repo: Path, name: str, digest: str) -> bytes:
    try:
        process = subprocess.run(
            ["git", "-C", str(repo), "show", f"{SBL_COMMIT}:{name}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Failure(f"public source read failed: {exc}") from exc
    if process.returncode or hashlib.sha256(process.stdout).hexdigest() != digest:
        raise Failure(f"public source identity mismatch: {name}")
    return process.stdout


def extract_stage(abl: bytes) -> bytes:
    if struct.unpack_from("<7I", abl, 0x18B440) != (0x2E6B7069, 0, 0, 0x33CD4, 0x2C, 0x33CD4, 0xF753ACFA):
        raise Failure("IBB IAS header drift")
    sizes = struct.unpack_from("<4I", abl, 0x18B45C)
    if sizes != (0xC0, 0x172D2, 0x44A9, 0x18493):
        raise Failure("IBB subimage table drift")
    compressed_start = (0x18B46C + sizes[0] + 3) & ~3
    compressed = abl[compressed_start : compressed_start + sizes[1]]
    if len(compressed) != sizes[1] or struct.unpack_from("<I", compressed)[0] != 0x1FE00:
        raise Failure("IBB stage-1 compressed identity drift")
    stage = lz4_block(compressed[4:-4], 0x1FE00)
    if hashlib.sha256(stage).hexdigest() != STAGE_SHA256:
        raise Failure("IBB stage-1 identity drift")
    return stage


def analyze(update_archive: Path, rootfs_archive: Path, sbl_repo: Path) -> dict:
    update_spec = {
        ABL_MEMBER: {"size": 8_388_608, "mode": 0o755, "uid": 8100, "gid": 8100, "sha256": ABL_SHA256}
    }
    abl = archive_members(update_archive, UPDATE_SIZE, UPDATE_SHA256, update_spec)[ABL_MEMBER]
    roots = archive_members(rootfs_archive, ROOTFS_SIZE, ROOTFS_SHA256, ROOT_MEMBERS)
    esinit = roots["lib/systemd/esinit"]
    engineer = roots["app/share/AppEngineerMode/constants/iasimage_update.sh"]
    stage = extract_stage(abl)

    for name, (start, end, digest) in STAGE_RANGES.items():
        if hashlib.sha256(stage[start:end]).hexdigest() != digest:
            raise Failure(f"ABL stage range drift: {name}")
    if stage.find(b"ABL.bdev") != 0x1C796 or stage.find(b"ABL.boot") != 0x1C79F:
        raise Failure("ABL command-line literal drift")
    if stage.find((0xFC796).to_bytes(4, "little")) != 0xBC6F or stage.find((0xFC79F).to_bytes(4, "little")) != 0xBC95:
        raise Failure("ABL command-line reference drift")
    if stage.find(b"*** WARNING: old-styleboot image configuration detected!") != 0x1C481:
        raise Failure("ABL boot callback diagnostic drift")
    if stage.find((0xFC481).to_bytes(4, "little")) != 0xAE7C:
        raise Failure("ABL boot callback reference drift")
    c0214_refs = []
    needle = (0xC0214).to_bytes(4, "little")
    cursor = 0
    while True:
        cursor = stage.find(needle, cursor)
        if cursor < 0:
            break
        c0214_refs.append(cursor)
        cursor += 1
    if c0214_refs != [0x509, 0x5FA, 0x611, 0x6BF, 0xAE21, 0xBC7B, 0x133CF, 0x133D6, 0x133E8, 0x13411, 0x13427, 0x13440, 0x1349C]:
        raise Failure("ABL boot-state reference inventory drift")

    config = abl[CONFIG_OFFSET : CONFIG_OFFSET + CONFIG_TOTAL_SIZE]
    if len(config) != CONFIG_TOTAL_SIZE or hashlib.sha256(config).hexdigest() != CONFIG_SHA256:
        raise Failure("ABL configuration container identity drift")
    magic, image_type, version, data_length, data_offset, unpacked_length, header_crc = struct.unpack_from("<7I", config)
    if (magic, image_type, version, data_length, data_offset, unpacked_length) != (0x2E6B7069, 0x60000, 0, 0xA68, 0x1C, 0xA68):
        raise Failure("ABL configuration IAS header drift")
    if crc32c(config[:24]) != header_crc:
        raise Failure("ABL configuration header CRC drift")
    payload = config[data_offset : data_offset + data_length]
    payload_crc = struct.unpack_from("<I", config, data_offset + data_length)[0]
    if crc32c(payload) != payload_crc:
        raise Failure("ABL configuration payload CRC drift")
    records = config_records(payload)
    if len(records) < 5:
        raise Failure("ABL configuration record count drift")
    expected = [
        (0, 0x10, 0x4B, 1, 1, 0, None, None),
        (1, 0x24, 0x4B, 1, 0xFF, 0, None, None),
        (2, 0x2C, 0x4B, 1, 2, 1, "iasImage", "pcbver=10 lge.sign=1"),
        (3, 0x2C, 0x4B, 1, 2, 2, "iasImage", "pcbver=10 lge.sign=1"),
        (4, 0x1C, 0x5C, 1, 2, 2, "iasPreload", None),
    ]
    actual = [
        (r["index"], r["size"], r["tag"], r["variant"], r["descriptor_kind"], r["descriptor_instance"], r.get("name"), r.get("predicate"))
        for r in records[:5]
    ]
    if actual != expected:
        raise Failure("ABL boot-option records drift")
    boot_gpio = records[5]
    if (boot_gpio["offset"], boot_gpio["size"], boot_gpio["tag"], boot_gpio["variant"]) != (0xA8, 0x14, 0x4E, 1):
        raise Failure("ABL BOOT_MODE_GPIO record drift")
    gpio_payload = payload[0xB0:0xBC]
    if struct.unpack("<6H", gpio_payload) != (0x0000, 0x0003, 0xFFFF, 0xFFFF, 0xC184, 0xC103):
        raise Failure("ABL BOOT_MODE_GPIO payload drift")
    if stage[0x1DB80:0x1DB90] != struct.pack("<IIII", 0x4D, 0xFD7F7, 0x4E, 0xFD800) or stage[0x1D800:0x1D80F] != b"BOOT_MODE_GPIO\0":
        raise Failure("ABL config-tag name table drift")
    if b"iasImage_sub" in config or b"_sub" in config or b"iasImage_sub" in abl or b"_sub" in stage:
        raise Failure("unexpected direct _sub literal in exact ABL evidence")

    for needle_text, label in (
        (b"#PLK1: ABL.boot=2", "esinit PLK1 mapping"),
        (b"#PLK2: ABL.boot=3", "esinit PLK2 mapping"),
        (b'grep "ABL.bdev=mmc2:/iasImage" /proc/cmdline >/dev/null', "esinit actual-device check"),
        (b"Boot Mode PLK1 but boot PLK2 for PLK1 crash", "esinit fallback diagnostic"),
        (b"cp /tmp/plk2/iasImage /tmp/plk1/iasImage", "esinit primary repair"),
    ):
        one_count(esinit, needle_text, label)
    one_count(engineer, b"cp -vf ./p2/iasImage_sub ./p1/iasImage", "engineering sub promotion")
    one_count(engineer, b"cp -vf ./p2/iasImage ./p1/iasImage", "engineering normal promotion")

    public_sources = {name: git_blob(sbl_repo, name, digest) for name, digest in SBL_FILES.items()}
    defs = public_sources["Platform/ApollolakeBoardPkg/Include/ConfigDataDefs.h"]
    board = public_sources["Platform/ApollolakeBoardPkg/Library/Stage1BBoardInitLib/Stage1BBoardInitLib.c"]
    one_count(defs, b"#define  ABL_CDATA_BOOT_MODE_GPIO_TAG   0x04E", "public BOOT_MODE_GPIO tag")
    if board.count(b"GetBootModeOption (") != 2:
        raise Failure("public GPIO decoder anchor multiplicity drift")
    one_count(board, b"*BootModeOption = (Data16 ^ BootModeGpio->Invert);", "public GPIO boot option result")
    one_count(board, b"PlatformData->BootModeOption.Uint16 = BootModeOption;", "public platform boot option write")

    selected_records = [
        {
            "boot_index": record["index"],
            "descriptor_kind": record["descriptor_kind"],
            "device_instance": record["descriptor_instance"],
            "basename": record.get("name"),
            "predicate": record.get("predicate"),
            "record_offset": record["offset"],
            "record_size": record["size"],
            "record_sha256": record["sha256"],
        }
        for record in records[2:4]
    ]
    ranges = {
        name: {
            "file_start": start,
            "file_end": end,
            "runtime_start": 0xE0000 + start,
            "runtime_end": 0xE0000 + end,
            "sha256": digest,
        }
        for name, (start, end, digest) in STAGE_RANGES.items()
    }
    return {
        "schema": SCHEMA,
        "tool": {"name": "abl-boot-selection", "version": VERSION},
        "exact_update": {
            "archive": {"size": UPDATE_SIZE, "sha256": UPDATE_SHA256},
            "abl": {"member": ABL_MEMBER, "size": len(abl), "sha256": ABL_SHA256},
            "config_container": {
                "flash_offset": CONFIG_OFFSET,
                "size_with_payload_crc": CONFIG_TOTAL_SIZE,
                "sha256": CONFIG_SHA256,
                "image_type": "0x60000 (ABL configuration)",
                "payload_size": data_length,
                "header_crc32c": f"{header_crc:08x}",
                "payload_crc32c": f"{payload_crc:08x}",
                "boot_records": selected_records,
                "boot_mode_gpio_record": {
                    "tag": "0x04e",
                    "record_offset": boot_gpio["offset"],
                    "record_size": boot_gpio["size"],
                    "record_sha256": boot_gpio["sha256"],
                    "invert": 0,
                    "mask": 3,
                    "alignment": "0xffff",
                    "output_pin": "0xffff",
                    "input_pins": ["0xc184", "0xc103"],
                },
                "direct_sub_literal_present": False,
            },
            "decompressed_stage": {
                "load_base": 0xE0000,
                "size": len(stage),
                "sha256": STAGE_SHA256,
                "ranges": ranges,
                "boot_state_address": "0x000c0214",
                "boot_state_reference_file_offsets": c0214_refs,
                "selected_index_expression": "byte[0x000c0214] & 0x1f",
                "selected_index_skips_earlier_records": True,
                "boot_record_callback_returns_zero_after_returned_load_failure": True,
                "config_iterator_callback_zero_continues_to_next_record": True,
                "later_records_remain_eligible_after_a_returned_failure": True,
                "kernel_cmdline_selected_field": "ABL.boot=<selected index in hexadecimal>",
                "kernel_cmdline_actual_device_field": "ABL.bdev=<actual device and path>",
                "config_tag_name_table": {"0x04e": "BOOT_MODE_GPIO"},
                "direct_sub_literal_present": False,
            },
        },
        "comparative_public_slim_bootloader": {
            "commit": SBL_COMMIT,
            "files": SBL_FILES,
            "platform": "Apollo Lake public source",
            "tag_0x04e_name": "ABL_CDATA_BOOT_MODE_GPIO_TAG",
            "semantics": "decode masked/inverted GPIO input bits and store BootModeOption in platform data",
            "exact_runtime_equivalence_proved": False,
        },
        "canonical_rootfs": {
            "archive": {"size": ROOTFS_SIZE, "sha256": ROOTFS_SHA256},
            "esinit": {
                "member": "lib/systemd/esinit",
                **ROOT_MEMBERS["lib/systemd/esinit"],
                "commented_index_map": {"2": "PLK1", "3": "PLK2"},
                "fallback_detection": "ABL.bdev=mmc2:/iasImage",
                "fallback_repair": "copy p2/iasImage to p1/iasImage",
            },
            "engineering_script": {
                "member": "app/share/AppEngineerMode/constants/iasimage_update.sh",
                **ROOT_MEMBERS["app/share/AppEngineerMode/constants/iasimage_update.sh"],
                "sub_action": "copy p2/iasImage_sub to p1/iasImage",
                "normal_action": "copy p2/iasImage to p1/iasImage",
            },
        },
        "conclusions": {
            "boot_index_2_maps_to_primary_iasimage_record": True,
            "boot_index_3_maps_to_secondary_iasimage_record": True,
            "selected_primary_failure_can_fall_forward_to_secondary_record": True,
            "kernel_cmdline_distinguishes_selected_index_from_actual_device": True,
            "userspace_repairs_primary_from_successful_secondary_fallback": True,
            "abl_configuration_directly_selects_iasimage_sub": False,
            "engineering_script_promotes_sub_by_overwriting_primary_basename": True,
            "exact_config_contains_boot_mode_gpio_record": True,
            "exact_stage_maps_tag_0x04e_to_boot_mode_gpio": True,
            "exact_runtime_boot_state_populated_from_gpio_proved": False,
            "persistent_boot_index_source_proved": False,
            "attempt_counter_proved": False,
            "health_or_mark_good_proved": False,
            "rollback_policy_proved": False,
            "custom_image_acceptance_root_or_persistence_proved": False,
        },
        "limitations": [
            "The exact stage proves ordered record selection and forward eligibility after a returned failure; it does not prove which individual load or authentication failures occurred on a physical unit.",
            "The exact configuration contains tag 0x04e with mask 0x0003 and two GPIO inputs, and the exact stage names tag 0x04e BOOT_MODE_GPIO. Historical public Apollo Lake source decodes that tag into platform BootModeOption, but exact runtime population of 0x000c0214 and persistence semantics remain unproved.",
            "The exact ABL configuration and recovered stage contain no direct _sub pathname. The stock engineering script supplies a separate userspace promotion route by copying p2/iasImage_sub over p1/iasImage; this does not prove that no dynamically constructed proprietary route exists elsewhere.",
            "The userspace recovery copy is attempted after a secondary boot; successful mount, copy, sync, durable repair, future selection, health, mark-good, and rollback are not proved by static code.",
            "No updater, bootloader, target helper, image, mount, copy, flash operation, reset, selector change, or boot attempt was executed.",
        ],
    }


def encode(value: dict) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False, separators=(",", ": ")) + "\n").encode("utf-8")


def exclusive(path: Path, data: bytes) -> None:
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0), 0o600)
    except OSError as exc:
        raise Failure(f"cannot create output exclusively: {exc}") from exc
    try:
        written = 0
        while written < len(data):
            count = os.write(fd, data[written:])
            if count <= 0:
                raise Failure("short output write")
            written += count
    finally:
        os.close(fd)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update-archive", type=Path, required=True)
    parser.add_argument("--rootfs", type=Path, required=True)
    parser.add_argument("--sbl-repo", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data = encode(analyze(args.update_archive, args.rootfs, args.sbl_repo))
        if args.output:
            exclusive(args.output, data)
        else:
            sys.stdout.buffer.write(data)
    except Failure as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
