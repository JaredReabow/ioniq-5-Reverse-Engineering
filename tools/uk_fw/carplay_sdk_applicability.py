#!/usr/bin/env python3
"""Inventory the recovered CarPlay/iAP2 surface without executing target code."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import struct
import sys
from pathlib import Path
from typing import Any

SCHEMA = "ioniq-carplay-sdk-applicability/v1"
TOOL_VERSION = "1.3.0"
MAX_FILE_BYTES = 128 * 1024 * 1024
ELF_HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
PROGRAM_HEADER = struct.Struct("<IIQQQQQQ")
PT_INTERP = 3
PT_GNU_STACK = 0x6474E551
PT_GNU_RELRO = 0x6474E552
PF_X = 1

EXPECTED_HASHES = {
    "lib/systemd/system/carplay_iAP2.service": "f7cf915509005a4aaa18d09e3a6ccd0abdd72ef2b2816641ea9a592a1e3f4495",
    "etc/iap2_mod.sh": "ecec04580a09b258796e96e20835deab60479b76edaceaaca01d58097b19656b",
    "etc/smack-relabel-ro.sh": "8275625764c30b6e82d99e5fdf887038261f97e9f0ef5a36da8faa743a35a15f",
    "etc/smack_setup.sh": "847af53be34d0e325c738a4ae26d11f7ed69b940cf2aa53d27e3b422e8a8ebb6",
    "etc/smack/accesses.d/projection": "978ccab43e6724df0bb74c4f84e3319ab3f0022dec442f4389fba140f6b3c1c9",
    "app/bin/iAP2Service-2.0": "38419131df82ec7e3c3b29a68ecc1a078c7f0b403051f137fe9f46f82b99f26e",
    "app/bin/AppProjection": "8f0096bcc0734d4c9766c15bac54c42f302ed7057182c2573b5ac543913960e3",
    "app/bin/mdnsd": "71122d8f59cdfd248f80414014e22114b0ee486415e5a7de23f5acd1676b9cdd",
    "app/lib/libiAP2AppFramework-2.0.so": "d4d0558c9c53f02ee14024c081ccd83a02ca29404ef400131e2951f68a388120",
    "app/lib/libAirPlay.so": "ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0",
    "app/lib/libCoreUtils.so": "9104e2c16ee27e647fac090ee7f3aa4cc686b8caaea1dc24763af2950c0ebfae",
    "app/lib/libAirPlaySupport.so": "1e57d807c320999fda35ac08e7e213f6533014f8d68391b1c33b00505b175893",
    "app/lib/libCarPlayAppFramework.so": "e3603e6b0744cf07724cc5cc79ea01ea3d9207d7eaf37c544c7ce26536ecd7a2",
    "app/lib/libCarPlayMediaFramework.so": "69690210d1aa4dec33c77b0e80f1d3368f8a70bcb507c1b158b6245dc29eb2f3",
    "lib/modules/4.1.27-abl/kernel/drivers/usb/gadget/function/usb_f_ncm.ko": "bb4c508c17d7c292d806f98d2d135a00949b2c144b57837194aa574c9a10cfaa",
    "lib/modules/4.1.27-abl/kernel/drivers/usb/gadget/function/usb_f_iap2.ko": "13bb79d9d9e991fdb9a950fc4ef8d65491c804a061208acb669ba54683e1e7bd",
    "lib/modules/4.1.27-abl/kernel/drivers/lge/mfd/mfd-iap2.ko": "1276cee2d1a2eca5e2c8d5c7f49eb813ffeae6b81ee490ba3abfc176ae2040c4",
}
ELF_PATHS = tuple(path for path in EXPECTED_HASHES if path.startswith("app/"))
ENABLE_LINK = "lib/systemd/system/multi-user.target.wants/carplay_iAP2.service"
ENABLE_TARGET = "/lib/systemd/system/carplay_iAP2.service"
LINKAGE_STRINGS = {
    "app/bin/iAP2Service-2.0": ("libiAP2AppFramework-2.0.so",),
    "app/bin/AppProjection": ("libiAP2AppFramework-2.0.so", "libCarPlayAppFramework.so"),
    "app/lib/libCarPlayAppFramework.so": ("libAirPlay.so", "libAirPlaySupport.so"),
}
LINEAGE_STRINGS = {
    "app/bin/iAP2Service-2.0": ("CarPlay.LHW.230712.a", "/dev/mfd-iap2"),
    "app/lib/libAirPlay.so": ("320.17.6",),
    "app/lib/libAirPlaySupport.so": (
        "CarPlayFramework/0.1.89-189.180620M.38-r8",
        "AppleCarPlay_CommunicationPlugin/320.17",
    ),
}
MARSHAL_RANGES = {
    "iAp2MarshalGetBytes": (0x21A56, 0x21B21, "601fc208cd6c41eb6926c782dcafcedd47c88785516c98c1290ebcdd2e08ac31"),
    "bounded_byte_span_helper": (0x21645, 0x2176A, "98cbc5af41238b006a7497dfce512b59c21b448f616a55ff641597a058303fcf"),
    "iAp2MarshalGetUint32": (0x2182B, 0x21885, "9470cb639a4bd1c95813d61f134f6b0bd8a4d64fc0af0ff0b49cc2a7d777af46"),
}
AIRPLAY_REQUEST_RANGE = (
    0xF3D1,
    0x11A3B,
    "fccea004635853ec3d685f24815e548a227bf8f65853f5e025e4115cda0cfc10",
)
SETUP_KEY_PATH_RANGE = (
    0x103C3,
    0x10580,
    "93bcf61544059dc8e162d80012a9527905fc3a26cee51bac471634678b110d67",
)
SETUP_ROUTE_RANGES = {
    "setup_method_and_plist_dispatch": (
        0xFF0D,
        0x100B6,
        "c208fb3bb3d4ff1c63a25e39dc7b2263aed1258cd62d73797bd591576f52304a",
    ),
    "setup_prekey_metadata_and_session": (
        0x100A3,
        0x103C3,
        "44ad05b420c93321d8bef6dd724d52eed547ca9e0274ef8399f8424f5e368b39",
    ),
    "post_auth_setup_dispatch": (
        0x1094D,
        0x10B3F,
        "4220993de1cc6fd57f9cfd5234217482a5001b5dffe8e5b4604b08cd94a87163",
    ),
}
MFI_AUTH_RANGES = {
    "MFiSAP_server_M1": (
        0x7F184,
        0x7F6D2,
        "82f0acf4129488fd468c797af0ab57fc997ec9f8900558ff1537f437d312c00d",
    ),
    "MFiSAP_Exchange": (
        0x7F8CE,
        0x7F99B,
        "366334d17eabce1093798b600a43004e4b8140230ecb8fb4c178421899d63a6c",
    ),
    "MFiPlatform_CreateSignature": (
        0x8068A,
        0x80D6C,
        "923e37d7fd3828db659fd135fd652a0c35b9e6f17f030946d1bf702a21648677",
    ),
    "MFiPlatform_CopyCertificate": (
        0x80D6C,
        0x8129F,
        "0b1160862646812e44f1e019eab17f6545cc4e58c601611e8ddb758e994c035e",
    ),
}
SETUP_KEY_CORE_RANGES = {
    "CFGetData": (0x47075, 0x4720F, "714c493f4fef6c0807b8fa82458806df30ea98f87cf9a58d84959393c7be7e19"),
    "CFDictionaryGetData": (0x472A0, 0x4733F, "615a9d9fde2ef58caf77a8f6cc7a59f1a206bdc7cb885e90a7a06629d49f85f7"),
    "MFiSAP_Decrypt": (0x7FA41, 0x7FAE7, "d73d2a706aaf00c7eaa472e9c9f2f1110834bc029f59581a7cd7d1f7b1c5e5e7"),
    "AES_CTR_Update": (0x1F373, 0x1F578, "6f3b5d9b617ee004f966833d32539166615cc2e12adc0fc9afaeda5bcdbfa610"),
}
BPLIST_RANGES = {
    "CFStringCreateWithBytes": (0x299E4, 0x29B11, "fb6c03d8ad313a1dd91026cece624b2ce1529fb6b56b2bcf2f09deee002c161b"),
    "read_sized_integer": (0x3964B, 0x396DD, "2054c003efe46884944f96f0790084b092a4f8d48c51b923e79d547f74a48c24"),
    "read_extended_count": (0x396DD, 0x3975D, "7b2ad966d067e523a2e7caf20a375b74182572be39d6332db8b26cae207e790d"),
    "read_object_reference": (0x3975D, 0x39867, "d16bc0d58e25b9415efec660dd96f07f7888729f1b2aa138d312df1a9843b75d"),
    "read_v0_object": (0x39A42, 0x3A25B, "311b21c47180959ed11e36874aefd57aa62a6b625e4c2061b2c7b2b15aca12cc"),
    "CFBinaryPlistV0CreateWithData": (0x3B605, 0x3B8FC, "c03a2284cb4fcc1b8fc71dd44653d9250c74e8149d285efd8b87296527c2e625"),
    "utf8_encodelen": (0xC356B, 0xC36DD, "8291feddc85ed5bc7ff032a2615aae0f54e4c40c906435e70dc4f8d473369ba2"),
    "utf8_encodestr": (0xC36DD, 0xC39EE, "c6beb495d5117cebf4e0883fa60ac3fe65fdc3f3409b608d8878d8a9a46effcd"),
    "utf8_encodestr_copy": (0xC44C9, 0xC459E, "6a51fe798013ec28857712bc2f381f26279c6b620ee5d4258a696ac2bad08cbe"),
}
AIRPLAY_PROTOCOL_MARKERS = (
    "/auth-setup",
    "/command",
    "/feedback",
    "/info",
    "/logs",
    "/pair-setup",
    "/pair-verify",
    "application/x-apple-binary-plist",
    "text/x-apple-plist+xml",
    "AirPlayReceiverServerHTTP",
    "_requestProcessSetupPlist",
)
AIRPLAY_PARSER_API_MARKERS = (
    "CFBinaryPlistV0CreateWithData",
    "CFDictionaryGetTypeID",
    "CFPropertyListCreateWithData",
    "HTTPServerCreate",
    "_HTTPServerControl",
)
PUBLIC_COMPARATORS = (
    {
        "cve": "CVE-2024-23933",
        "advisory": "ZDI-24-877",
        "product": "Sony XAV-AX5500",
        "public_mechanism": "physically delivered CarPlay TLV reaches an unchecked copy into a fixed stack buffer",
        "public_impact": "code execution in the device context",
        "url": "https://www.zerodayinitiative.com/advisories/ZDI-24-877/",
    },
    {
        "cve": "CVE-2025-8474",
        "advisory": "ZDI-25-763",
        "product": "Alpine iLX-507",
        "public_mechanism": "physically delivered CarPlay data reaches an unchecked copy into a fixed stack buffer",
        "public_impact": "code execution in the root context on the named Alpine product",
        "url": "https://www.zerodayinitiative.com/advisories/ZDI-25-763/",
    },
    {
        "cve": "CVE-2024-37602",
        "advisory": None,
        "product": "Mercedes-Benz NTG6 through 2021",
        "public_mechanism": "prepared HTTP requests reach an AirTunes/AirPlay null-pointer dereference",
        "public_impact": "CarPlay service failure",
        "url": "https://securelist.com/mercedes-benz-head-unit-security-research/115218/",
    },
    {
        "cve": "CVE-2025-24132",
        "advisory": "Apple AirPlay SDK security update",
        "product": "AirPlay audio SDK before 2.7.1 / video SDK before 3.6.0.126",
        "public_mechanism": "vendor: memory-handling issue; researcher: CWE-121 stack-based buffer overflow",
        "public_impact": "vendor: termination; researcher: CarPlay RCE under stated Wi-Fi, Bluetooth, or physical-USB conditions",
        "url": "https://support.apple.com/en-us/122403",
    },
    {
        "cve": "CVE-2025-30422",
        "advisory": "Apple AirPlay SDK security update",
        "product": "AirPlay audio SDK before 2.7.1 / video SDK before 3.6.0.126",
        "public_mechanism": "vendor: buffer overflow; researcher: CWE-190 integer overflow or wraparound",
        "public_impact": "vendor: termination; researcher: potential RCE",
        "url": "https://support.apple.com/en-us/122403",
    },
)


class AuditError(ValueError):
    """A reviewed input or deterministic-output invariant failed."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_read(path: Path, limit: int = MAX_FILE_BYTES) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise AuditError(f"not a regular file: {path}")
        if before.st_size < 0 or before.st_size > limit:
            raise AuditError(f"file exceeds {limit} byte limit: {path}")
        chunks: list[bytes] = []
        remaining = before.st_size
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                raise AuditError(f"short read: {path}")
            chunks.append(chunk)
            remaining -= len(chunk)
        if os.read(descriptor, 1):
            raise AuditError(f"file grew during read: {path}")
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
        ):
            raise AuditError(f"file identity changed during read: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def strict_ascii(data: bytes, label: str) -> str:
    try:
        return data.decode("ascii", "strict")
    except UnicodeDecodeError as exc:
        raise AuditError(f"{label} is not strict ASCII: {exc}") from exc


def _inside(root: Path, relative: str) -> Path:
    if not relative or relative.startswith("/") or ".." in Path(relative).parts:
        raise AuditError(f"unsafe relative path: {relative!r}")
    return root / relative


def parse_elf(data: bytes, label: str) -> dict[str, Any]:
    if len(data) < ELF_HEADER.size:
        raise AuditError(f"{label}: truncated ELF header")
    values = ELF_HEADER.unpack_from(data)
    ident = values[0]
    if ident[:4] != b"\x7fELF" or ident[4:7] != b"\x02\x01\x01":
        raise AuditError(f"{label}: expected ELF64 little-endian version 1")
    elf_type, machine, version, entry = values[1:5]
    phoff, phentsize, phnum = values[5], values[9], values[10]
    if version != 1 or machine != 62:
        raise AuditError(f"{label}: expected x86-64 ELF")
    if phentsize != PROGRAM_HEADER.size or phnum <= 0 or phnum > 256:
        raise AuditError(f"{label}: invalid program-header table")
    table_size = phentsize * phnum
    if phoff > len(data) or table_size > len(data) - phoff:
        raise AuditError(f"{label}: program-header table outside file")
    has_interp = False
    stack_executable: bool | None = None
    gnu_relro = False
    for index in range(phnum):
        p_type, p_flags, p_offset, _vaddr, _paddr, p_filesz, p_memsz, _align = PROGRAM_HEADER.unpack_from(
            data, phoff + index * phentsize
        )
        if p_filesz > p_memsz or p_offset > len(data) or p_filesz > len(data) - p_offset:
            raise AuditError(f"{label}: invalid program header {index}")
        if p_type == PT_INTERP:
            has_interp = True
        elif p_type == PT_GNU_STACK:
            stack_executable = bool(p_flags & PF_X)
        elif p_type == PT_GNU_RELRO:
            gnu_relro = True
    return {
        "elf_type": elf_type,
        "machine": machine,
        "entry": entry,
        "has_interpreter": has_interp,
        "position_independent_executable": elf_type == 3 and has_interp,
        "gnu_stack_present": stack_executable is not None,
        "stack_executable": stack_executable,
        "gnu_relro_segment": gnu_relro,
        "stack_canary_reference": b"__stack_chk_fail\x00" in data,
        "fortified_memory_reference": any(
            name in data
            for name in (b"__memcpy_chk\x00", b"__strcpy_chk\x00", b"__sprintf_chk\x00")
        ),
    }


def elf_vaddr_bytes(data: bytes, address: int, size: int, label: str) -> bytes:
    values = ELF_HEADER.unpack_from(data)
    phoff, phentsize, phnum = values[5], values[9], values[10]
    matches = []
    for index in range(phnum):
        p_type, _flags, p_offset, p_vaddr, _paddr, p_filesz, _p_memsz, _align = PROGRAM_HEADER.unpack_from(
            data, phoff + index * phentsize
        )
        if p_type != 1:
            continue
        if p_vaddr <= address and size <= p_filesz and address - p_vaddr <= p_filesz - size:
            offset = p_offset + address - p_vaddr
            matches.append(data[offset:offset + size])
    if len(matches) != 1 or len(matches[0]) != size:
        raise AuditError(f"{label}: virtual range is not uniquely file-backed")
    return matches[0]


def _require_text(text: str, needles: tuple[str, ...], label: str) -> None:
    for needle in needles:
        if needle not in text:
            raise AuditError(f"{label}: required text absent: {needle!r}")


def build_report(rootfs: Path) -> dict[str, Any]:
    root_stat = os.lstat(rootfs)
    if not stat.S_ISDIR(root_stat.st_mode) or stat.S_ISLNK(root_stat.st_mode):
        raise AuditError("rootfs must be a real directory, not a symlink")

    files: dict[str, bytes] = {}
    identities: dict[str, Any] = {}
    for relative, expected in EXPECTED_HASHES.items():
        data = stable_read(_inside(rootfs, relative))
        observed = digest(data)
        if observed != expected:
            raise AuditError(f"identity mismatch for {relative}: {observed}")
        files[relative] = data
        identities[relative] = {"bytes": len(data), "sha256": observed}

    link_path = _inside(rootfs, ENABLE_LINK)
    link_stat = os.lstat(link_path)
    if not stat.S_ISLNK(link_stat.st_mode):
        raise AuditError("CarPlay enable path is not a symlink")
    link_target = os.readlink(link_path)
    if link_target != ENABLE_TARGET:
        raise AuditError(f"CarPlay enable-link target drift: {link_target!r}")

    service = strict_ascii(files["lib/systemd/system/carplay_iAP2.service"], "service")
    module_script = strict_ascii(files["etc/iap2_mod.sh"], "module script")
    relabel = strict_ascii(files["etc/smack-relabel-ro.sh"], "SMACK relabel script")
    smack_setup = strict_ascii(files["etc/smack_setup.sh"], "SMACK setup script")
    projection_policy = strict_ascii(
        files["etc/smack/accesses.d/projection"], "projection policy"
    )
    _require_text(
        service,
        (
            "ExecStartPre=/etc/iap2_mod.sh",
            "ExecStart=/app/bin/iAP2Service-2.0",
            "Restart=always",
            "WantedBy=multi-user.target",
        ),
        "service",
    )
    if "User=" in service:
        raise AuditError("service unexpectedly declares User=")
    _require_text(
        module_script,
        ("modprobe usb_f_ncm", "modprobe usb_f_iap2", "modprobe mfd-iap2"),
        "module script",
    )
    _require_text(relabel, ('("iAP2Service-2.0" "App::projection")',), "relabel")
    _require_text(
        smack_setup,
        ('dir_labeling /dev/mfd-iap2 "System::iap20"',),
        "SMACK setup",
    )
    _require_text(
        projection_policy,
        ("App::projection System::iap20 rw----", "App::projection _ rwxa--"),
        "projection policy",
    )

    elf_reports: dict[str, Any] = {}
    for relative in ELF_PATHS:
        elf_reports[relative] = parse_elf(files[relative], relative)

    linkage: dict[str, list[str]] = {}
    for relative, expected_strings in LINKAGE_STRINGS.items():
        observed = []
        for value in expected_strings:
            if value.encode("ascii") not in files[relative]:
                raise AuditError(f"{relative}: linkage string absent: {value}")
            observed.append(value)
        linkage[relative] = observed

    marshal_library = files["app/lib/libiAP2AppFramework-2.0.so"]
    marshal_ranges: dict[str, Any] = {}
    for name, (start, end, expected_hash) in MARSHAL_RANGES.items():
        body = elf_vaddr_bytes(marshal_library, start, end - start, name)
        if digest(body) != expected_hash:
            raise AuditError(f"{name}: reviewed range identity drift")
        marshal_ranges[name] = {
            "start": hex(start),
            "end": hex(end),
            "size": len(body),
            "sha256": digest(body),
        }
    span_helper = elf_vaddr_bytes(marshal_library, 0x21645, 0x2176A - 0x21645, "span helper")
    for pattern, meaning in (
        (bytes.fromhex("837dd4fc762e"), "reject lengths above 0xfffffffc before round-up"),
        (bytes.fromhex("8b45d483c00383e0fc"), "round requested length up to four-byte alignment"),
        (bytes.fromhex("8b400c3b45d4735f"), "compare remaining bytes with aligned request"),
        (bytes.fromhex("8b400c2b45d4"), "subtract aligned request from remaining bytes"),
    ):
        if span_helper.count(pattern) != 1:
            raise AuditError(f"marshal span helper pattern drift: {meaning}")

    lineage: dict[str, list[str]] = {}
    for relative, expected_strings in LINEAGE_STRINGS.items():
        observed = []
        for value in expected_strings:
            if value.encode("ascii") not in files[relative]:
                raise AuditError(f"{relative}: lineage string absent: {value}")
            observed.append(value)
        lineage[relative] = observed

    airplay_library = files["app/lib/libAirPlay.so"]
    for marker in AIRPLAY_PROTOCOL_MARKERS + AIRPLAY_PARSER_API_MARKERS:
        if marker.encode("ascii") not in airplay_library:
            raise AuditError(f"libAirPlay.so: reviewed HTTP/plist marker absent: {marker}")
    request_start, request_end, request_hash = AIRPLAY_REQUEST_RANGE
    request_body = elf_vaddr_bytes(
        airplay_library,
        request_start,
        request_end - request_start,
        "_requestProcessSetupPlist",
    )
    if digest(request_body) != request_hash:
        raise AuditError("HTTP delegate/inlined setup: reviewed range identity drift")
    key_start, key_end, key_hash = SETUP_KEY_PATH_RANGE
    key_path_body = elf_vaddr_bytes(
        airplay_library,
        key_start,
        key_end - key_start,
        "setup encryption-key path",
    )
    if digest(key_path_body) != key_hash:
        raise AuditError("setup encryption-key path: reviewed range identity drift")
    for pattern, meaning in (
        (bytes.fromhex("31c931d24c8db424800000004d89f9"), "request ekey with null destination and zero maximum"),
        (bytes.fromhex("4183fd10"), "select MFi-SAPv1 encryption type 0x10"),
        (bytes.fromhex("488b942480000000488d8c24080100004889c6"), "pass returned ekey length and rsp+0x108 destination to MFiSAP_Decrypt"),
        (bytes.fromhex("4883bc248000000010"), "require the separately copied IV length to equal 16"),
    ):
        if key_path_body.count(pattern) != 1:
            raise AuditError(f"setup encryption-key path pattern drift: {meaning}")
    for pattern, meaning in (
        (bytes.fromhex("4c8dac2408010000488d9424180100004c89ee"), "pass rsp+0x108 key and rsp+0x118 IV to session security setup"),
        (bytes.fromhex("498d4c150048ffc24883fa117405c60100"), "securely zero exactly 16 key bytes after session setup"),
    ):
        if request_body.count(pattern) != 1:
            raise AuditError(f"setup encryption-key use pattern drift: {meaning}")

    setup_route_ranges: dict[str, Any] = {}
    for name, (start, end, expected_hash) in SETUP_ROUTE_RANGES.items():
        body = elf_vaddr_bytes(airplay_library, start, end - start, name)
        if digest(body) != expected_hash:
            raise AuditError(f"{name}: reviewed setup-route identity drift")
        setup_route_ranges[name] = {
            "start": hex(start),
            "end": hex(end),
            "size": len(body),
            "sha256": digest(body),
        }
    auth_route = elf_vaddr_bytes(
        airplay_library, 0x1094D, 0x10B3F - 0x1094D, "POST /auth-setup route"
    )
    for pattern, meaning in (
        (bytes.fromhex("80bbe800000000"), "test the per-connection MFiSAP-done byte"),
        (bytes.fromhex("488dbbe0000000be01000000"), "create a version-1 server MFiSAP context"),
        (bytes.fromhex("4c8d8be8000000488bbbe0000000"), "pass the connection done flag and context to MFiSAP_Exchange"),
    ):
        if auth_route.count(pattern) != 1:
            raise AuditError(f"POST /auth-setup route pattern drift: {meaning}")

    core_utils = files["app/lib/libCoreUtils.so"]
    mfi_auth_ranges: dict[str, Any] = {}
    for name, (start, end, expected_hash) in MFI_AUTH_RANGES.items():
        body = elf_vaddr_bytes(core_utils, start, end - start, name)
        if digest(body) != expected_hash:
            raise AuditError(f"{name}: reviewed MFi authentication range identity drift")
        mfi_auth_ranges[name] = {
            "start": hex(start),
            "end": hex(end),
            "size": len(body),
            "sha256": digest(body),
        }
    mfi_exchange = elf_vaddr_bytes(core_utils, 0x7F8CE, 0x7F99B - 0x7F8CE, "MFiSAP_Exchange")
    for pattern, meaning in (
        (bytes.fromhex("803f01750e4883fe0119c083e0fd83c0058807"), "select server-M1 state 5 for non-null input"),
        (bytes.fromhex("fe0341c60101"), "advance successful server M1 to done state 6 and set outDone"),
        (bytes.fromhex("c60300"), "invalidate the MFiSAP state after an exchange error"),
    ):
        if mfi_exchange.count(pattern) != 1:
            raise AuditError(f"MFiSAP_Exchange pattern drift: {meaning}")
    if b"/dev/i2c-1\x00" not in core_utils:
        raise AuditError("libCoreUtils.so: exact MFi authentication I2C path absent")

    setup_key_core_ranges: dict[str, Any] = {}
    for name, (start, end, expected_hash) in SETUP_KEY_CORE_RANGES.items():
        body = elf_vaddr_bytes(core_utils, start, end - start, name)
        if digest(body) != expected_hash:
            raise AuditError(f"{name}: reviewed setup-key range identity drift")
        setup_key_core_ranges[name] = {
            "start": hex(start),
            "end": hex(end),
            "size": len(body),
            "sha256": digest(body),
        }
    cf_get_data = elf_vaddr_bytes(core_utils, 0x47075, 0x4720F - 0x47075, "CFGetData")
    mfi_decrypt = elf_vaddr_bytes(core_utils, 0x7FA41, 0x7FAE7 - 0x7FA41, "MFiSAP_Decrypt")
    aes_update = elf_vaddr_bytes(core_utils, 0x1F373, 0x1F578 - 0x1F373, "AES_CTR_Update")
    for body, pattern, meaning in (
        (cf_get_data, bytes.fromhex("4885db0f84dc000000"), "return CFData bytes without a destination copy when inBuf is null"),
        (mfi_decrypt, bytes.fromhex("4883c738e8"), "forward caller pointer, length, and destination to AES_CTR_Update"),
        (aes_update, bytes.fromhex("4889d34883ec38"), "retain the caller-supplied size for the update loops"),
        (aes_update, bytes.fromhex("41881402"), "store each full-block output byte through the caller destination"),
        (aes_update, bytes.fromhex("88540500"), "store each trailing output byte through the caller destination"),
    ):
        if body.count(pattern) < 1:
            raise AuditError(f"setup encryption-key callee pattern drift: {meaning}")

    bplist_ranges: dict[str, Any] = {}
    for name, (start, end, expected_hash) in BPLIST_RANGES.items():
        body = elf_vaddr_bytes(core_utils, start, end - start, name)
        if digest(body) != expected_hash:
            raise AuditError(f"{name}: reviewed binary-plist range identity drift")
        bplist_ranges[name] = {
            "start": hex(start),
            "end": hex(end),
            "size": len(body),
            "sha256": digest(body),
        }
    read_object = elf_vaddr_bytes(core_utils, 0x39A42, 0x3A25B - 0x39A42, "read_v0_object")
    if read_object.count(bytes.fromhex("4801d2")) < 1:
        raise AuditError("read_v0_object: UTF-16 length doubling instruction drift")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "tool_version": TOOL_VERSION,
        "inputs": identities,
        "activation": {
            "enabled_by_multi_user_symlink": True,
            "enable_link": ENABLE_LINK,
            "enable_target": link_target,
            "exec_start_pre": "/etc/iap2_mod.sh",
            "exec_start": "/app/bin/iAP2Service-2.0",
            "restart": "always",
            "explicit_user_directive": None,
            "configured_systemd_default_uid": 0,
        },
        "transport_configuration": {
            "normal_script_branch_modules": ["usb_f_ncm", "usb_f_iap2", "mfd-iap2"],
            "device_path_in_service_binary": "/dev/mfd-iap2",
            "mfi_auth_chip_device_path_in_core_utils": "/dev/i2c-1",
            "exact_module_files_bound": True,
            "physical_phone_or_network_delivery_observed": False,
        },
        "smack": {
            "service_exec_label": "App::projection",
            "iap2_device_label": "System::iap20",
            "service_to_iap2_device_access": "rw----",
            "projection_to_floor_access": "rwxa--",
            "runtime_labels_observed": False,
        },
        "linkage_strings": linkage,
        "lineage_strings": lineage,
        "elf_static_properties": elf_reports,
        "airplay_http_plist_review": {
            "binary": "app/lib/libAirPlay.so",
            "request_processor": {
                "reviewed_name": "HTTP connection delegate containing inlined _requestProcessSetupPlist",
                "name_evidence": "the FDE starts at the installed HTTP delegate callback; embedded _requestProcessSetupPlist and _requestDecryptKey strings are referenced by assertions in their inlined branches",
                "start": hex(request_start),
                "end": hex(request_end),
                "size": len(request_body),
                "sha256": digest(request_body),
                "stack_frame_bytes": 0x178,
                "stack_canary_load_present": bytes.fromhex("64488b042528000000") in request_body[:0x50],
                "binary_plist_parse_call_sites": ["0x10032", "0x107a7", "0x10b75", "0x10e1a"],
                "dictionary_type_check_call_sites": [
                    "0x100ae", "0x107bf", "0x10bac", "0x10c54", "0x10e51"
                ],
                "bounded_text_write_callees": ["TruncateUTF8", "snprintf", "strlcpy"],
                "direct_unbounded_copy_or_concatenation_callees": [],
                "direct_rep_operations": [
                    {"address": "0xf817", "operation": "rep stosd"},
                    {"address": "0xfc4a", "operation": "rep stosd"},
                    {"address": "0x102a3", "operation": "rep stosd"},
                ],
                "direct_dispatcher_interpretation": "Across the FDE-bounded HTTP callback, the direct libc-style call inventory contains bounded text writes and structure clears rather than memcpy/strcpy/sprintf/strcat. Deeper review of the inlined setup encryption-key branch, however, establishes a distinct unbounded MFiSAP_Decrypt to AES_CTR_Update stack-write chain described below.",
            },
            "protocol_markers": list(AIRPLAY_PROTOCOL_MARKERS),
            "parser_api_markers": list(AIRPLAY_PARSER_API_MARKERS),
            "request_body_to_parser_path": {
                "call_site": "0x10032",
                "body_pointer_field": "HTTP message + 0x518",
                "body_length_field": "HTTP message + 0x530",
                "error_checked_after_call": True,
                "dictionary_type_checked_at": "0x100a3..0x100b6",
                "runtime_delivery_observed": False,
            },
            "setup_route_and_mfisap_review": {
                "airplay_ranges": setup_route_ranges,
                "core_utils_ranges": mfi_auth_ranges,
                "setup_dispatch": {
                    "method": "SETUP",
                    "method_compare_call_site": "0xff1b",
                    "accepted_content_types": [
                        "application/x-apple-binary-plist",
                        "text/x-apple-plist+xml",
                    ],
                    "content_type_header_lookup": "0xff2f..0xff5e",
                    "plist_parse_call_site": "0x10032",
                    "url_specific_acceptance_gate_observed": False,
                },
                "setup_prekey_field_inventory": {
                    "range": "0x100a3..0x103c3",
                    "fields": [
                        {"name": "deviceID", "call_site": "0x100f2", "operation": "six-byte hardware address conversion to scalar"},
                        {"name": "interfaceName", "call_site": "0x10122", "operation": "snprintf", "destination_capacity_bytes": 17},
                        {"name": "macAddress", "call_site": "0x10146", "operation": "hardware-address copy", "destination_capacity_bytes": 6},
                        {"name": "name", "call_site": "0x10161", "operation": "CFDictionaryGetCString", "destination_capacity_bytes": 128},
                        {"name": "sessionUUID", "call_site": "0x10186", "operation": "CFDictionaryGetData", "destination_capacity_bytes": 16, "post_copy_exact_length_check": "0x10192"},
                        {"name": "sourceVersion", "call_site": "0x10207", "operation": "CFDictionaryGetCString", "destination_capacity_bytes": 64},
                        {"name": "model", "call_site": "0x10245", "operation": "CFDictionaryGetCString", "destination_capacity_bytes": 64},
                    ],
                    "session_create_parameter_structure_cleared_before_population": True,
                    "session_create_call_site": "0x10333",
                    "capacity_argument_absent_for_reviewed_direct_string_or_data_writes": False,
                    "downstream_session_setup_handlers_reviewed_by_this_inventory": False,
                    "interpretation": "The direct pre-key setup metadata writes carry explicit capacities, and sessionUUID is additionally required to return exactly 16 bytes. This closes only the listed callback-local field handling; CF helper implementations and downstream AirPlayReceiverSession setup consumers remain separate review surfaces.",
                },
                "auth_setup_dispatch": {
                    "method": "POST",
                    "path_suffix": "/auth-setup",
                    "method_compare_call_site": "0x1095b",
                    "path_compare_call_site": "0x10975",
                    "requires_nonempty_body": True,
                    "completed_context_is_deleted_before_restart": True,
                    "creates_server_mfisap_version": 1,
                    "exchange_call_site": "0x10a8f",
                    "exchange_receives_http_body_pointer_and_length": True,
                    "exchange_writes_connection_done_flag": "connection + 0xe8",
                    "success_response_content_type": "application/octet-stream",
                },
                "mfisap_state_machine": {
                    "non_null_input_selects_server_m1_state": 5,
                    "successful_server_m1_advances_to_server_done_state": 6,
                    "successful_server_m1_sets_connection_done_flag": True,
                    "exchange_error_invalidates_state": True,
                    "decrypt_accepts_states": [4, 6],
                    "server_m1_requires_exact_version1_plus_32_byte_public_key": True,
                    "server_m1_uses_mfi_platform_certificate_and_signature": True,
                    "mfi_platform_device_path": "/dev/i2c-1",
                },
                "local_callback_gate_review": {
                    "http_authorization_check_before_setup_observed": False,
                    "pair_verify_or_pair_setup_state_required_before_setup_observed": False,
                    "homekit_pair_verify_context_presence_diverts_away_from_ekey_path": True,
                    "homekit_pair_verify_context_null_check": "0x103a9..0x103c3",
                    "completed_mfisap_required_when_encryption_type_is_0x10": True,
                    "interpretation": "The exact callback directly dispatches SETUP by method and plist content type. For encryption type 0x10, MFiSAP_Decrypt independently requires state 4 or 6; the normal exact route to server-done state 6 is a successful POST /auth-setup exchange backed by certificate/signature operations on /dev/i2c-1. No HTTP Authorization or pair-verify state check appears in the reviewed callback before SETUP, but an upstream generic HTTPConnection gate outside this callback has not been excluded.",
                },
                "runtime_mfi_chip_or_protocol_success_observed": False,
                "fixed_r18_1_bytes_available": False,
            },
            "setup_encryption_key_review": {
                "airplay_binary": "app/lib/libAirPlay.so",
                "core_utils_binary": "app/lib/libCoreUtils.so",
                "inlined_path_range": {
                    "start": hex(key_start),
                    "end": hex(key_end),
                    "size": len(key_path_body),
                    "sha256": digest(key_path_body),
                },
                "core_ranges": setup_key_core_ranges,
                "request_dictionary_field": "ekey",
                "encryption_type": {"value": 0x10, "comparative_public_name": "kAirPlayEncryptionType_MFi_SAPv1"},
                "key_retrieval": {
                    "call_site": "0x1040f",
                    "destination_argument": None,
                    "maximum_length_argument": 0,
                    "full_cfdata_length_returned_at": "stack + 0x80",
                    "returned_data_pointer_used": True,
                    "pre_decrypt_length_equals_16_check_present": False,
                },
                "decrypt_call": {
                    "call_site": "0x1048c",
                    "source_pointer": "CFDictionaryGetData return value",
                    "length": "stack + 0x80, unchanged",
                    "destination": "stack + 0x108",
                    "destination_capacity_bytes": 16,
                    "capacity_evidence": "the session-security call consumes key at +0x108 and IV at +0x118; the post-call secure-zero loop clears exactly 16 key bytes",
                },
                "separate_iv_copy": {
                    "destination": "stack + 0x118",
                    "maximum_length_bytes": 16,
                    "post_copy_length_equals_16_check": "0x1053f",
                },
                "stack_geometry": {
                    "frame_allocation_bytes": 0x178,
                    "key_buffer_offset": "stack + 0x108",
                    "iv_buffer_offset": "stack + 0x118",
                    "canary_offset": "stack + 0x168",
                    "key_buffer_bytes": 16,
                    "bytes_from_key_start_to_canary": 0x60,
                    "stack_canary_checked_at": "0x11728..0x11742",
                },
                "callee_semantics": {
                    "CFGetData_null_destination_returns_underlying_cfdata_pointer_and_full_length": True,
                    "MFiSAP_Decrypt_forwards_caller_length_and_destination_to_AES_CTR_Update": True,
                    "AES_CTR_Update_writes_caller_length_bytes_to_destination": True,
                    "destination_capacity_passed_to_decrypt_or_update": False,
                },
                "exact_unbounded_stack_write_mechanism_present": True,
                "static_preconditions": [
                    "the HTTP callback has received a SETUP request with a recognized plist content type",
                    "the setup body has parsed as a dictionary",
                    "the connection has no HomeKit pair-verify security context; a non-null context takes the alternate security-context branch at 0x103a9..0x103c3",
                    "the encryption type is 0x10",
                    "the connection has a non-null MFiSAP context",
                    "MFiSAP state is client-done or server-done; the exact server route reaches server-done only after successful POST /auth-setup certificate/signature exchange",
                ],
                "runtime_phone_delivery_or_authentication_observed": False,
                "public_comparison": {
                    "source": "TheGamingGallifreyan/LiberationPlay-CVE-2025-24132-AirBourne-POC",
                    "source_url": "https://github.com/TheGamingGallifreyan/LiberationPlay-CVE-2025-24132-AirBourne-POC",
                    "retrieved": "2026-11-02",
                    "commit": "ffd24a03dc5425dd89f6352bf588fcde5f4081ff",
                    "public_source_sha256": "dafbad8b342e705543ee03f132ab09c320fecf719503b735ac8d6d99ba3fb6e7",
                    "reported_mechanism_matches": ["setup request", "ekey field", "MFi-SAP state", "AES-CTR write into a 16-byte key buffer"],
                    "third_party_cve_2025_24132_mechanism_match_established": True,
                    "vendor_confirmed_function_or_patch_match": False,
                    "interpretation": "A public third-party report that claims vulnerable-versus-patched binary analysis identifies the same field and cryptographic call chain. The recovered bytes independently establish the memory-safety mechanism, but Apple and Oligo have not publicly confirmed this function or supplied fixed bytes for comparison.",
                },
                "impact_boundary": "The exact bytes establish an unbounded stack write and a canary-mediated failure boundary. They do not establish live phone-to-handler delivery, authentication bypass, reliable instruction-pointer control, code execution, SMACK escape, unrestricted root, or persistence on the recovered or installed unit.",
            },
            "binary_plist_parser_review": {
                "binary": "app/lib/libCoreUtils.so",
                "ranges": bplist_ranges,
                "requires_bplist00_header": True,
                "accepted_offset_and_reference_widths": [1, 2, 4, 8],
                "rejects_input_pointer_wrap": True,
                "requires_nonzero_object_count": True,
                "requires_top_object_below_object_count": True,
                "bounds_offset_table_with_division_before_multiplication": True,
                "bounds_sized_integer_reads_to_remaining_input": True,
                "bounds_data_and_single_byte_string_lengths_to_remaining_input": True,
                "bounds_dictionary_reference_count_with_division_before_multiplication": True,
                "unguarded_utf16_byte_length_doubling": {
                    "instruction": "0x39e89: add rdx, rdx",
                    "subsequent_check_uses_wrapped_value": True,
                    "wrapped_value_passed_as_CFStringCreateWithBytes_length": True,
                    "CFStringCreateWithBytes_signed_32bit_narrowing": "0x299eb: movsxd rsi, edx",
                    "high_bit_32bit_length_causes_zero_input_iterations": True,
                    "nonnegative_truncated_length_not_greater_than_parser_checked_length": True,
                    "direct_out_of_bounds_read_or_copy_excluded_for_this_chain": True,
                    "security_relevant_semantic_truncation_established": False,
                    "cve_2025_30422_attribution_established": False,
                    "interpretation": "An exact unsigned length-wrap and later signed-32-bit narrowing exist for binary-plist UTF-16 objects. A high-bit 32-bit result exits both UTF-16 conversion loops before input reads; a nonnegative truncated result is no larger than the parser-checked wrapped length. This excludes a direct OOB read/copy in this exact chain, while leaving unproved semantic-truncation effects and other integer paths open.",
                },
            },
            "public_architecture_overlap": "The recovered library contains an HTTP/RTSP-style AirPlay receiver, binary/XML plist content types, route strings, and plist/dictionary parser APIs of the same broad class discussed by Oligo.",
            "limitation": "The setup ekey path now has an exact recovered unbounded-stack-write mechanism and a matching third-party CVE-2025-24132 report. No vendor-confirmed function mapping, fixed-build bytes, runtime delivery, or exploitability evidence is available; the CVE identity therefore remains third-party-attributed rather than vendor byte-confirmed.",
        },
        "iap2_marshal_getbytes_review": {
            "ranges": marshal_ranges,
            "length_prefix_source": "iAp2MarshalGetUint32",
            "maximum_accepted_unaligned_length": 0xFFFFFFFC,
            "rounds_length_to_four_byte_alignment": True,
            "checks_aligned_length_against_remaining_bytes": True,
            "advances_pointer_only_after_remaining_check": True,
            "subtracts_aligned_length_from_remaining_bytes": True,
            "copies_to_fixed_stack_buffer": False,
            "bounded_interpretation": "The generic exported byte-string decoder is not the unchecked fixed-stack copy described by the public Sony/Alpine advisories; other TLV, HTTP, pairing, media, and vendor handlers remain unreviewed.",
        },
        "public_comparators": list(PUBLIC_COMPARATORS),
        "verdict": {
            "recovered_carplay_iap2_service_enabled": True,
            "configured_uid_zero": True,
            "recovered_iap2_gadget_and_mfd_modules_selected": True,
            "apple_communication_plugin_320_17_string_present": True,
            "generic_iap2_getbytes_unchecked_stack_copy_present": False,
            "airplay_setup_dispatcher_direct_unbounded_libc_copy_present": False,
            "airplay_setup_ekey_unbounded_stack_write_present": True,
            "cve_2025_24132_third_party_mechanism_match_present": True,
            "cve_2025_24132_vendor_confirmed_function_or_patch_match": False,
            "binary_plist_utf16_length_wrap_candidate_present": True,
            "binary_plist_utf16_direct_out_of_bounds_chain_excluded": True,
            "binary_plist_utf16_security_relevant_semantic_truncation_established": False,
            "exact_public_cve_code_match_established": False,
            "phone_to_parser_delivery_observed": False,
            "crash_observed": False,
            "code_execution_observed": False,
            "root_transition_observed": False,
            "persistence_observed": False,
        },
        "boundaries": [
            "The recovered service, enable link, module script, binaries, labels, hashes, and lineage strings are exact static facts for EU 260128.",
            "The public Sony and Alpine findings concern different products and disclose no function bytes or patch suitable for an exact code match.",
            "Apple's public SDK advisory names fixed AirPlay and CarPlay SDK releases, but the recovered private 320.17 lineage string has no public version mapping to those releases.",
            "Oligo classifies CVE-2025-24132 as CarPlay stack-overflow RCE and CVE-2025-30422 as potential integer-overflow RCE, but withholds the exact vulnerable route and implementation details in the reviewed publication.",
            "A later public third-party demonstration attributes CVE-2025-24132 to the same setup ekey/MFiSAP/AES-CTR chain found independently in the recovered bytes; this is strong comparative mechanism evidence, not vendor confirmation or a fixed-byte match.",
            "The exact callback routes SETUP by method and plist content type and has no observed local HTTP-Authorization or pair-state gate before that branch; this does not exclude an upstream generic HTTPConnection gate outside the callback.",
            "For encryption type 0x10, decryption still requires a completed MFiSAP state. The exact server path reaches that state only after POST /auth-setup successfully obtains certificate/signature results through /dev/i2c-1; static node strings and code do not prove a chip, certificate, exchange, or phone is present at runtime.",
            "The exact unbounded stack write does not by itself establish live route reachability, authentication bypass, reliable code execution, or impact beyond the configured App::projection process context.",
            "Stack canary, non-executable stack, RELRO, or fortify references constrain some outcomes but do not prove parser safety.",
            "No target executable, module, service, USB device, network endpoint, parser, or malformed input was executed by this audit.",
        ],
    }
    canonical = json.dumps(report, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    report["canonical_sha256"] = digest(canonical)
    return report


def write_exclusive(path: Path, data: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "wb") as output:
        output.write(data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rootfs", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report(args.rootfs)
        rendered = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
        if args.output:
            write_exclusive(args.output, rendered)
        else:
            sys.stdout.buffer.write(rendered)
    except (AuditError, OSError, ValueError, struct.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
