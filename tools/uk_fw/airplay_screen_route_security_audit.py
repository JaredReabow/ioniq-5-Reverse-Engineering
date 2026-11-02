#!/usr/bin/env python3
"""Verify the recovered AirPlay screen listener and security route offline."""

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

SCHEMA = "ioniq-airplay-screen-route-security-audit/v1"
TOOL_VERSION = "1.1.0"
MAX_FILE_BYTES = 64 * 1024 * 1024
ELF_HEADER = struct.Struct("<16sHHIQQQIHHHHHH")
PROGRAM_HEADER = struct.Struct("<IIQQQQQQ")
PT_LOAD = 1

SUBJECTS = {
    "airplay": {
        "basename": "libAirPlay.so",
        "size": 215_896,
        "sha256": "ef9e69e3b3388d4a7a1d185827c710af25b8ee99d406c60c664a9609b00aada0",
    },
    "coreutils": {
        "basename": "libCoreUtils.so",
        "size": 1_200_368,
        "sha256": "9104e2c16ee27e647fac090ee7f3aa4cc686b8caaea1dc24763af2950c0ebfae",
    },
}

RANGES = {
    "http_delegate_install": (
        "airplay", 0xC750, 0xC7D2,
        "89012ad230f7302e6d6d77fa90b67db910e417c929eb2ac1208adc6195c75ba5",
    ),
    "setup_callback_encryption_to_session_setup": (
        "airplay", 0x103C3, 0x10637,
        "5cde34310a8cdf36004c110ed3f9656dbdadaacf2b808fb12dc057e1fce57a81",
    ),
    "receiver_session_create": (
        "airplay", 0x16E90, 0x172C2,
        "1a4852541d7e277ff9b2de1b7d0cff7bb9795cb930ec5fe178e7be9f11c7bc62",
    ),
    "receiver_session_zero_initialization": (
        "airplay", 0x16EC4, 0x16F23,
        "5790f507c7df6f73bb0f512a7f81454dfca0fd4a2df3ca0d3690a81e50951eda",
    ),
    "receiver_session_set_security_info": (
        "airplay", 0x17515, 0x175D5,
        "7b8cee275a7702e4c9948e380144ecae461b03dc9a3d336d3e94fb042a9ba64b",
    ),
    "screen_type_dispatch": (
        "airplay", 0x19F3F, 0x19F71,
        "24a836755508aba236f508184264747e42fb1d6d3ef8edd7eb91598d26adab7d",
    ),
    "screen_setup_security_and_listener": (
        "airplay", 0x1B665, 0x1B92B,
        "494935dce8d51a8da5cb51ebd00fa6d9b5236f5d1e2565bffea52c5c3b4f6b63",
    ),
    "screen_start_thread": (
        "airplay", 0x134F0, 0x135D6,
        "47a54d3ebb0561039dd3fb779d7edbd6f6088d3e39fd4e21dc78c80a42aba59e",
    ),
    "screen_thread_accept_to_parser": (
        "airplay", 0x135D6, 0x138F5,
        "9833c94f4dddfd8ca3199fc34dc146ed4f9d2f129be2133798d39da2bcdaf0f6",
    ),
    "screen_set_chacha_security": (
        "airplay", 0x1F0E0, 0x1F151,
        "ca7fb1554218e07d51f5f30e7eaa61170c6f75438380293d74c384e87a823e21",
    ),
    "screen_set_aes_security": (
        "airplay", 0x1F151, 0x1F1F6,
        "2b69348fe1442c3935a0fa8af00b68fa0219797d481434e4280b4fb1b72cd3de",
    ),
    "screen_body_crypto_dispatch": (
        "airplay", 0x1F5E5, 0x1F74C,
        "146bc2d367c4eecb4e4d9822e2f8f47d0e892a34f0376f5595b14628459d67b3",
    ),
    "derive_aes_key_sha512": (
        "airplay", 0x21234, 0x2135A,
        "b94de2155c65cd4269b8d7d45a55bdd89d514c0c79e06937aa6c1fadd249d60a",
    ),
    "derive_screen_key": (
        "airplay", 0x2135A, 0x21478,
        "1e5e4c0fa02925c4985e5adcd42924bac894fa9ab2799095f4a2fdefda9a9c11",
    ),
    "dictionary_get_int64": (
        "coreutils", 0x43D18, 0x43D87,
        "be58439ad302800e4b0330e1d8120ff2be822aab800238e7220ee4e71badb202",
    ),
    "http_connection_set_delegate": (
        "coreutils", 0x75E63, 0x75EB1,
        "03bbd091b0ecba150867d6a1b022ad866bf2e126b1a151bf5c62039834a1ceaa",
    ),
    "http_connection_state_machine": (
        "coreutils", 0x76E94, 0x77153,
        "4130bd9de44106e7e08f072cbd83da4fccd2fcacffffb533c23ee3f62a6e473e",
    ),
    "socket_accept": (
        "coreutils", 0x87AE3, 0x87CCC,
        "91f051bbf297b0b5adca67abbb9c61cc161f6afa9023ba55228efd226fc343f2",
    ),
    "server_socket_open": (
        "coreutils", 0x88F84, 0x89420,
        "2f850a99c9164348285e59b94c967255d8b5f6223912d069ee486ebef77a05ee",
    ),
}

ANCHORS = {
    "airplay_callback_installed_as_http_delegate": (
        "airplay", 0xC77B,
        "488d0584faffff4c89c748895424084889442418488d055bf7ffff4889442420488d057cf6ffff4889442428488d05232c00004889442438e848d2ffff",
    ),
    "absent_or_none_encryption_skips_key_install": (
        "airplay", 0x103D7,
        "837c2450004989c50f854102000083f8010f8438020000",
    ),
    "setup_called_after_skip_branch": (
        "airplay", 0x10626,
        "488b7b10488d5424704c89e6e8a97fffff",
    ),
    "fresh_session_body_is_zeroed": (
        "airplay", 0x16EC4,
        "31c931ffbad81a000089c6e80c1effff4885c0753731c031f6415631ff6a004c8d0d3644010041b889010000bdb8e5ffff488d0d1a120100488d15c0010100e8f828ffff415f58e982030000488d50084889c3b9b60600004889d731c0f3ab",
    ),
    "only_direct_base_key_store_site": (
        "airplay", 0x17593,
        "4c89a358020000410f10060f118360020000410f104d000f118b70020000",
    ),
    "screen_stream_type_0x6e_dispatch": (
        "airplay", 0x19F3F,
        "488d35c502010031d24889c7e840eafeff4989c683f866741e770e83f8640f83550d0000e9971a000083f86e0f84f4160000",
    ),
    "nonzero_stream_connection_id_required": (
        "airplay", 0x1B72C,
        "488d3553eb000031d24c89efe853d2feff4889c64885c075364c8d0d64f70000415031ff31c06a0041b800110000bdc5e5ffff488d0db0c90000488d1594e20000e88ee0feff4159415ae916020000",
    ),
    "pair_verify_selects_32_byte_stream_key": (
        "airplay", 0x1B77B,
        "4883bb700400000074694c8dac249801000031c931d2488dbb700400004d89e8e826b3ffff89c585c074154c8d0d03f700005741b8051100006a00e9be010000488bbbb81a0000ba200000004c89eee8e1d3feff89c585c0",
    ),
    "null_pair_verify_derives_aes_from_session_key": (
        "airplay", 0x1B7EE,
        "4c8dac24780100004889c2be100000004c8db424280100004d89e8488dbb600200004c89f1e808cdfeff488bbbb81a00004c89ea4c89f6e8f6d2feff",
    ),
    "secondary_server_socket_open": (
        "airplay", 0x1B86E,
        "ba0600000041b90040fdffb972e8ffff0fb7bbe400000050488d83c01a0000be01000000504c8d8424ec000000e800d4feff",
    ),
    "response_advertises_type_and_data_port": (
        "airplay", 0x1B8BD,
        "8bbbc01a0000be0c000000e873e2feffba6e0000004c89e7488d352fe90000e89fe1feff48639424dc000000488d3558ea00004c89e7e888e1feff488b7c24084c89e6e828a1ffff",
    ),
    "started_session_launches_screen_thread": (
        "airplay", 0x1B951,
        "80bb3e0400000074374889dfe88e7bffff",
    ),
    "accept_has_null_peer_address_output": (
        "airplay", 0x1361B,
        "8bbbc01a000031c9be0a000000488d54240ce8be54ffff",
    ),
    "accepted_socket_reaches_process_frames": (
        "airplay", 0x137C8,
        "488b4310488bb3c81a0000488bbbb81a00008b90ac000000e8ab5fffff",
    ),
    "aes_ctr_enabled_after_init": (
        "airplay", 0x1F19B,
        "4889efe8cd9afeff89c585c07428488d0da0c200005031d289ee6a004c8d0d62c7000031ff31c041b831010000e833a6feff5a59eb07c683e801000001",
    ),
    "chacha_verify_or_aes_ctr_before_parser": (
        "airplay", 0x1F5E5,
        "80bbf0010000000f8403010000837b480f0f86310100004c8d83180300004c8db3f80100004c89c24c89442438488db3f80200004c89f7e8ef90feff4c89feba800000004c89f7e86f91feff8b43484889e94889ee4c89f78d50f0e85b8ffeff488d4c24444c89f74989c78b43484a8d743d008d50f04801eae85d99feff8b7424444c01f84c8b44243885f6741f41b81c020000415131d26a004c8d0d1ac20000488d0dc3bd0000e9e50000008b4b4883e9104839c8743941b81d0200005631ff31f66a004c8d0defc1000031c0488d0d96bd0000488d15f0be0000e83aa1feffc744245496e5ffff5f4158e99d030000894b4831c0418a0c008d51014188140084d2754348ffc04883f80875e8eb3880bbe801000000742f8b5348488dbbc80000004889e94889eee82da2feff8944244485c07412",
    ),
    "screen_derivation_uses_named_salts_and_supplied_inputs": (
        "airplay", 0x2135A,
        "41574d89c74989d041564989ce4155488d0da1a800004989f5be0100000041544989fc55534889d3488d155a7a00004883ec2864488b042528000000488944241831c0488d7c240848c74424080000000048c744241000000000e8c779feff488d7c24104989d8be01000000488d0d55a800004863e831c0488d150a7a0000e8a279feff41574889e94c89ee41564c8b4424204863d84c89e7488b5424184989d9e86072feff",
    ),
    "sha512_derivation_hashes_salt_then_base_key": (
        "airplay", 0x21289,
        "4d85ff7444488d5c24204889dfe81575feff488b5424104889df488b742418e8937afeff4c89f24c89ee4889dfe8857afeff4889de4889efe8fa7bfeff0f108424f8000000410f11074d85e47444488d5c24204889dfe8cc74feff488b5424084889df488b3424e84b7afeff4c89f24c89ee4889dfe83d7afeff4889de4889efe8b27bfeff0f108c24f8000000410f110c24",
    ),
    "http_message_read_flows_directly_to_delegate": (
        "coreutils", 0x76EDC,
        "e8cf4dfaffba010000004889df89c6e82be6ffff83f80b0f843c02000085c00f8502020000488b7b70488d5510488b8d100400004c8b8d200500004c8b85180500004889fee86a69faff488b53204889ee4889dfff5350",
    ),
    "missing_dictionary_integer_sets_error": (
        "coreutils", 0x43D30,
        "4885ff742ae8c67bfdff4885c07420488b4c24086448330c2528000000752d4883c4104889de4889c75be9119bfdff4885db7406c703b9e5ffff",
    ),
    "ipv4_sockaddr_is_zeroed_before_wildcard_bind": (
        "coreutils", 0x88FE4,
        "89eac1fa1f4189d74131ef4129d74183fc020f85ce0100004c8d64241cb904000000ba100000004c89e74c89e64589f9f3ab89df66c744241c02006641c1c9086644894c241ee8c154f9ff",
    ),
    "negative_preferred_port_falls_back_to_dynamic": (
        "coreutils", 0x89162,
        "c1ed1f0f84e8feffffba100000004c89e689df66c744241e0000e86f53f9ff",
    ),
    "stream_socket_listens": (
        "coreutils", 0x8925B,
        "be8000000089dfe89936f9ff85c00f84f6fdffffe8cc45f9ffbe0500000089df4889c5e87d36f9ff",
    ),
}

PUBLIC_COMPARATOR = {
    "repository": "45clouds/WirelessCarPlay",
    "commit": "51145ef55f8dd9f1cbadd58353cacb5e0ca215e9",
    "session_source": "source/Sources/AirPlayReceiverSession.c",
    "session_source_sha256": "5ed352778a8e786707245ef993994e6e172efd6b89f5fb71893e71e1c8ca3b61",
    "common_header": "source/Sources/AirPlayCommon.h",
    "common_header_sha256": "6774bd04f8889d991caacea613b1873d1ac08e0014f371d8b1c1a42ba86df17d",
    "role": "comparative names and protocol semantics only; recovered bytes and addresses are authoritative",
}


class AuditError(ValueError):
    """An input or deterministic-output invariant failed."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_read(path: Path) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise AuditError(f"not a regular file: {path}")
        if before.st_size < 0 or before.st_size > MAX_FILE_BYTES:
            raise AuditError(f"file exceeds {MAX_FILE_BYTES} byte limit: {path}")
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
        identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        if identity_before != identity_after:
            raise AuditError(f"file identity changed during read: {path}")
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def parse_load_segments(data: bytes) -> list[dict[str, int]]:
    if len(data) < ELF_HEADER.size:
        raise AuditError("truncated ELF header")
    values = ELF_HEADER.unpack_from(data)
    ident = values[0]
    if ident[:4] != b"\x7fELF" or ident[4:7] != b"\x02\x01\x01":
        raise AuditError("expected ELF64 little-endian version 1")
    if values[1] != 3 or values[2] != 62 or values[3] != 1:
        raise AuditError("expected x86-64 ET_DYN ELF version 1")
    phoff, phentsize, phnum = values[5], values[9], values[10]
    if phentsize != PROGRAM_HEADER.size or phnum > 1024:
        raise AuditError("invalid program-header geometry")
    end = phoff + phentsize * phnum
    if phoff > len(data) or end > len(data):
        raise AuditError("program-header table is out of bounds")
    segments: list[dict[str, int]] = []
    for index in range(phnum):
        fields = PROGRAM_HEADER.unpack_from(data, phoff + index * phentsize)
        p_type, p_flags, p_offset, p_vaddr, _p_paddr, p_filesz, p_memsz, p_align = fields
        if p_type != PT_LOAD:
            continue
        if p_filesz > p_memsz or p_offset + p_filesz > len(data):
            raise AuditError("invalid PT_LOAD bounds")
        segments.append({
            "flags": p_flags,
            "offset": p_offset,
            "vaddr": p_vaddr,
            "filesz": p_filesz,
            "memsz": p_memsz,
            "align": p_align,
        })
    if not segments:
        raise AuditError("ELF has no PT_LOAD segment")
    return segments


def va_to_offset(segments: list[dict[str, int]], va: int, size: int) -> int:
    if va < 0 or size < 0 or va + size < va:
        raise AuditError("invalid virtual-address range")
    for segment in segments:
        start = segment["vaddr"]
        end = start + segment["filesz"]
        if va >= start and va + size <= end:
            return segment["offset"] + va - start
    raise AuditError(f"virtual range 0x{va:x}+0x{size:x} is not file-backed")


def _verify_subject(data: bytes, role: str) -> dict[str, Any]:
    expected = SUBJECTS[role]
    if len(data) != expected["size"]:
        raise AuditError(f"{role} size mismatch")
    digest = sha256(data)
    if digest != expected["sha256"]:
        raise AuditError(f"{role} SHA-256 mismatch")
    segments = parse_load_segments(data)
    return {
        "basename": expected["basename"],
        "size": len(data),
        "sha256": digest,
        "load_segments": segments,
    }


def classify_crypto_route(pair_verify_present: bool, base_key_installed: bool) -> str:
    if type(pair_verify_present) is not bool or type(base_key_installed) is not bool:
        raise AuditError("crypto-route inputs must be booleans")
    if pair_verify_present:
        return "pair-verify-derived ChaCha20-Poly1305 with tag verification"
    if base_key_installed:
        return "session-base-key-derived AES-CTR without body authentication"
    return "zero-session-base-key-derived AES-CTR candidate without body authentication"


def _canonical_digest(report: dict[str, Any]) -> str:
    payload = dict(report)
    payload.pop("canonical_sha256", None)
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("ascii")
    return sha256(encoded)


def build_report(airplay: bytes, coreutils: bytes) -> dict[str, Any]:
    data_by_role = {"airplay": airplay, "coreutils": coreutils}
    subjects = {
        role: _verify_subject(data, role) for role, data in data_by_role.items()
    }
    segments = {role: subjects[role]["load_segments"] for role in subjects}

    ranges: dict[str, Any] = {}
    for name, (role, start, end, expected_digest) in RANGES.items():
        if end <= start:
            raise AuditError(f"invalid range: {name}")
        offset = va_to_offset(segments[role], start, end - start)
        body = data_by_role[role][offset : offset + end - start]
        digest = sha256(body)
        if digest != expected_digest:
            raise AuditError(f"range digest mismatch: {name}")
        ranges[name] = {
            "subject": role,
            "start_va": f"0x{start:x}",
            "end_va_exclusive": f"0x{end:x}",
            "size": end - start,
            "sha256": digest,
        }

    anchors: dict[str, Any] = {}
    for name, (role, va, expected_hex) in ANCHORS.items():
        expected = bytes.fromhex(expected_hex)
        offset = va_to_offset(segments[role], va, len(expected))
        actual = data_by_role[role][offset : offset + len(expected)]
        if actual != expected:
            raise AuditError(f"instruction anchor mismatch: {name}")
        anchors[name] = {
            "subject": role,
            "va": f"0x{va:x}",
            "size": len(expected),
            "bytes_hex": expected_hex,
        }

    store_pattern = bytes.fromhex("0f118360020000")
    address_pattern = bytes.fromhex("488dbb60020000")
    store_count = airplay.count(store_pattern)
    address_count = airplay.count(address_pattern)
    if store_count != 1 or address_count != 1:
        raise AuditError("session base-key direct pattern inventory changed")

    report: dict[str, Any] = {
        "schema": SCHEMA,
        "tool_version": TOOL_VERSION,
        "subjects": subjects,
        "ranges": ranges,
        "anchors": anchors,
        "route": {
            "generic_http_dispatch": {
                "airplay_callback_entry": "0xf3d1",
                "airplay_callback_installed_at": "0xc7a7",
                "connection_delegate_call_offset": "0x50",
                "message_read_success_to_delegate_sequence": [
                    "HTTPMessageReadMessage",
                    "I/O error mapping",
                    "LogHTTP",
                    "installed delegate call",
                ],
                "authorization_check_between_message_read_and_delegate": False,
                "qualification": "This closes a separate generic HTTPConnection check in the exact post-read dispatcher only; admission or policy elsewhere remains unproved.",
            },
            "setup_stream": {
                "type": "0x6e",
                "requires_nonzero_stream_connection_id": True,
                "already_initialized_screen_is_rejected": True,
                "listener_created_by": "ServerSocketOpen",
                "response_advertises": ["type", "dataPort"],
                "thread_start_requires_session_started_state": True,
            },
            "listener": {
                "family_source": "control session peer address family",
                "type": "TCP stream",
                "preferred_port_argument": -6030,
                "negative_port_allows_dynamic_fallback": True,
                "ipv4_bind_address": "INADDR_ANY (zero address)",
                "ipv6_bind_address": "in6addr_any",
                "accepted_peer_address_requested_by_caller": False,
                "accepted_socket_reaches_process_frames": True,
            },
            "security": {
                "pair_verify_present": classify_crypto_route(True, False),
                "pair_verify_absent_with_installed_base_key": classify_crypto_route(False, True),
                "pair_verify_absent_without_installed_base_key": classify_crypto_route(False, False),
                "encryption_type_absent_reaches_session_setup_without_base_key_install": True,
                "encryption_type_none_0x01_reaches_session_setup_without_base_key_install": True,
                "fresh_session_base_key_offset": "0x260",
                "fresh_session_base_key_zero_initialized": True,
                "screen_setup_checks_base_key_initialized_marker": False,
                "screen_key_inputs_in_null_pair_verify_branch": [
                    "16-byte session base key at +0x260",
                    "request streamConnectionID",
                    "literal AirPlayStreamKey salt",
                    "literal AirPlayStreamIV salt",
                ],
                "screen_body_cleartext_at_parser": True,
                "chacha_branch_verifies_tag_before_parser": True,
                "aes_ctr_branch_has_body_authentication_check": False,
            },
        },
        "direct_offset_inventory": {
            "session_base_key_offset": "0x260",
            "direct_explicit_store_sites_in_complete_libAirPlay_disassembly": ["0x1759e"],
            "direct_explicit_store_pattern_count": store_count,
            "direct_explicit_read_address_sites_in_complete_libAirPlay_disassembly": ["0x1b809"],
            "direct_explicit_read_address_pattern_count": address_count,
            "qualification": "direct constant-offset instruction inventory only; it does not exclude indirect aliases or writes in other objects",
        },
        "assessment": {
            "classification": "exact-static screen-route prerequisite refinement",
            "no_mfi_fallback_candidate": True,
            "reason": "A fresh session is zero-initialized; absent encryption type or comparative None value 0x01 skips AirPlayReceiverSessionSetSecurityInfo; the type-0x6e screen branch nevertheless derives and installs an AES-CTR screen key from the zero base key and requester-supplied nonzero streamConnectionID.",
            "wildcard_secondary_listener": True,
            "same_peer_enforcement_observed_at_accept_call": False,
            "generic_httpconnection_authorization_gate_observed": False,
            "relationship_to_prior_parser_finding": "This narrows static prerequisites for the separately byte-bound screen parser read/write candidate; it does not change that finding's impact or CVE boundaries.",
            "cve_attribution": None,
        },
        "boundaries": {
            "not_established": [
                "authorization or admission checks before completed-message dispatch or outside the reviewed generic HTTPConnection path",
                "live SETUP or session-start acceptance",
                "runtime listening interface or firewall exposure",
                "phone, USB/NCM peer, or network-peer delivery",
                "ability of an unauthenticated peer to learn the returned dataPort",
                "successful accepted-socket connection",
                "allocator corruption, process exit, or restart behavior",
                "reliable code execution, SMACK escape, unrestricted root, or persistence",
                "installed owner-unit identity or applicability",
                "CVE-2025-30422 or any other CVE identity",
            ],
            "important_qualifications": [
                "The pair-verify branch requires valid ChaCha20-Poly1305 authentication before parsing.",
                "The null-pair-verify branch still applies AES-CTR before parsing; the exact no-MFi candidate is about deterministic non-hardware-backed base material, not cleartext socket input.",
                "Wildcard bind and a null peer-address output do not prove that the port is reachable from an external interface or that no policy exists elsewhere.",
                "The exact generic state machine calls the installed AirPlay delegate directly after successful message read and logging, but this does not exclude admission or policy before that state machine or elsewhere in the system.",
                "Static route acceptance does not prove a sender can complete every preceding control-session state transition.",
            ],
        },
        "public_comparator": PUBLIC_COMPARATOR,
        "prior_screen_parser_artifact": {
            "schema": "ioniq-airplay-screen-parser-bounds-audit/v1",
            "canonical_sha256": "4dbc0a3b6d91cbe988082b271788681380447a6cff2ffeec5258573d63e3822f",
            "role": "separate exact-static parser bounds finding",
        },
    }
    report["canonical_sha256"] = _canonical_digest(report)
    return report


def encode_report(report: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            report, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False
        )
        + "\n"
    ).encode("ascii")


def write_exclusive(path: Path, payload: bytes) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        written = 0
        while written < len(payload):
            count = os.write(descriptor, payload[written:])
            if count <= 0:
                raise OSError("short write")
            written += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("airplay", type=Path)
    parser.add_argument("coreutils", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        report = build_report(stable_read(args.airplay), stable_read(args.coreutils))
        payload = encode_report(report)
        if args.output:
            write_exclusive(args.output, payload)
        else:
            sys.stdout.buffer.write(payload)
    except (AuditError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
