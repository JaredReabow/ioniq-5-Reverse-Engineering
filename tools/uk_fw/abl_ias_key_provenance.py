#!/usr/bin/env python3
"""Freeze the exact FIT/OEM-key-manifest handoff used by ABL IAS verification."""
from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import os
import stat
import struct
import subprocess
import sys
import tarfile
from pathlib import Path

SCHEMA = "abl-ias-key-provenance/v1"
VERSION = "1.0.0"
UPDATE_SIZE = 42_101_042
UPDATE_SHA256 = "1e67344a714708733a9158a52ef5d4def95b126e5725d070669ea64e0644c4c8"
ABL_MEMBER = "abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin"
ABL_SIZE = 8_388_608
ABL_SHA256 = "f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac"
IBBL_SHA256 = "394c442368c67f82f17e84854575bf07abafac2b8fbf2fda7dca68b182f91b93"
STAGE1_SHA256 = "3491be59ef865cb376131b02fa1ff6941e37d1c87ae3c4cf7969b5364785b3c2"
CANDIDATE_OS_KEY_DIGEST = "437008c1b26fd821a7c7c0ec855aaba5587f62deaaa98d9b2fcbf6ad4179aa06"
UEP_OFFSET = 0x100210
UEP_SIZE = 0x108
UEP_SHA256 = "184e01883e7f9233d5e50104a52620ec45e44c79ae3255fdeeaf8a44d5e8edc3"
ROT_KEY_OFFSET = 0x17B000
ROT_KEY_SIZE = 0x3FC
ROT_KEY_SHA256 = "5530da6cbec43a441466478a6069b7a5d39afe9453f34923c633ad07b4613a14"
INTEL_ROOT_KEY_DIGEST = "f2eb8fc44e30f6132631df884020abd685ce8843ee205d0a22eb6493f78a54cf"
OEM_KEY_OFFSET = 0x17C000
OEM_KEY_SIZE = 0x61C
OEM_KEY_SHA256 = "a72a5d867185852be1466a9d3d2e97bb11bd6b0a89b48f5454220def946814bd"
STORED_USAGE39_DIGEST = "9b0a59c842ba70857b595ed8115630d3a342a10c9d4437f9ff4807517693e0af"
IBBP_MAN_SHA256 = "f224328529c3662c8c3ba490ad2a3c8143a34d0c9a531d2568f94d639058f615"
BPM_MET_SHA256 = "4a82dcd20e5ad30e80b11637c767a9a9140b3e570d5144cda9407390b9618738"
IBB_SHA256 = "4fba3004219bbfe3a94baa23467c7076d87f4ad76fdb6687ccdbf93455e365ed"
NFTP_MAN_SHA256 = "d89f510f91eb9191e4b1e4a1a17b4675e3823953067ded257a6d78b2fb340ea4"
DAL_SDM_COMPRESSED_OFFSET = 0x2E6000
DAL_SDM_COMPRESSED_SIZE = 0x6B1A
DAL_SDM_COMPRESSED_SHA256 = "1149c790897678ef5896251e55c038448c7c9fc9424c337e378df07f111f9b8f"
DAL_SDM_MET_OFFSET = 0x206D80
DAL_SDM_MET_SIZE = 0xFC
DAL_SDM_MET_SHA256 = "e92963d1b1fd942671b9cb11c1de30312f7a529b1e63bfbf0b26826dd1d9c874"
DAL_SDM_SIZE = 0xE000
DAL_SDM_SHA256 = "04c4f9833276bc4fe26969ba4fa195b1e330efba4d97f178987c8c4b170335ba"
FPF_MET_OFFSET = 0x205F6C
FPF_MET_SIZE = 0x10C
FPF_MET_SHA256 = "2f5ecd89cfd900abf8dda056ee19b7d373bdda7a6a1ea0092e38404268de51ec"
FPF_COMPRESSED_OFFSET = 0x268000
FPF_COMPRESSED_SIZE = 0x2A51
FPF_COMPRESSED_SHA256 = "40e9da01431dc7a40e82ba6a33e1ee7d9891c9ffa0cda02efb5ff56387681e47"
FPF_SIZE = 0x6000
FPF_SHA256 = "9fd694bc90c7433528cfcf80ad265093cc61e086d882a3c52dee152ba64630b9"
SBL_COMMIT = "5f5c14b10ae6bd3cd0cf7e274142767dc2635a06"
SBL_FILE = "BootloaderCorePkg/Include/FirmwareInterfaceTable.h"
SBL_FILE_SHA256 = "0e0f1fff576e4edc48d2918d14bb1292526d3c01d3547d38305ea435543722ef"
SBL_APL_LOADER_FILE = "Platform/ApollolakeBoardPkg/Library/LoaderLib/LoaderLib.c"
SBL_APL_LOADER_SHA256 = "8f4c30f671559937a660dedee4abd31a04d5cfa4425fa942b30c5aa07391cbcd"
SBL_APL_BOARD_FILE = "Platform/ApollolakeBoardPkg/BoardConfig.py"
SBL_APL_BOARD_SHA256 = "72b04ce00e9deb24952bfb01b6a37f4da1bf290ab48f8ed469d9a28da7c96212"
MEA_COMMIT = "d27ccdba0aadbad490f47b5b631c369b682a7ef5"
MEA_FILE = "MEA.py"
MEA_FILE_SHA256 = "ed2dfb3b9efe58431609b4d3eefe6908b3124228288163dd4fd667dd17d5f4ef"
IBBL_RANGES = {
    "fit_payload_relocator": (0x40, 0xF3, "688cec0863886aa5a7ca6ed5cb1b9333c8112cd1babb4af2c79a07ebb80cb35a"),
    "fit_table_validator_and_copy": (0xF3, 0x171, "a83c5a32fb4e8b8157769332a6f27ba7484b1e55948228b1ce9cd45e0fb41ea8"),
    "source_fit_handoff_copy": (0x4EF, 0x54C, "c3bd36e3b536f906633be18e362f7744bd845bb505cf11eff8b4af0e46ee4b19"),
    "descriptor_copy_helper": (0x118E, 0x1199, "fa4ff48022ec39639e171133f556be4f08e63ae6eb127b983b39db35f506755a"),
    "cse_sram_to_temp_handoff_setup": (0x269A, 0x275B, "9fb4c68a8041510cbd3fe188a7abc30f0f6be8aa2ef95bc5407af5d773b80fe4"),
    "exact_cse_ibb_ring_consumer": (0x279, 0x4EF, "2224e3e1026e81972f8b3a24cbfca0945d43e0480f16ba8d21c97e78bf3f7a2f"),
    "ring_consumer_call_and_fit_dispatch": (0x1199, 0x125B, "0e9116019748b1f7c934cd0d7f2cf3c2e61a1fbe0f5bd7567b4231044e8caed1"),
}
STAGE1_RANGES = {
    "ias_key_and_payload_auth": (0x157A3, 0x159FE, "4b71d5c95ff2bcf4210ba23a96883f3ce3524fb31b40f037a00991a6c14a7f30"),
    "oemkm_command_line_export": (0xBEA5, 0xBF10, "f37111948019b765312545efc1c3472d488b4fef7a3a322f86e5df92a722e40b"),
}
RBEP_MAN_SHA256 = "80b5c254b9349d3bb716122f8dce36873e0ecb1a0576231fc74057eb90fcde79"
RBE_MET_SHA256 = "85f66e7be721e913665f5ffb9a0aca1d8e5d811ac8cb4f0e702bc0a3dec656c0"
FTPR_MAN_SHA256 = "ca4fc90c57b212daa077e8dec1bc7c4827638ff21da0e7224a3bbce2e57efdf4"
BUP_MET_SHA256 = "7ef14c9991d3fb702131b3fc3da96c382e9eb294a054bf4bceeb78245df4941b"
CSE_RBE_SHA256 = "ec4c2ea54c2943f6f6ffed4b4157b7b03cbccf6ca2cc9b21ccc3dd62adc88cc1"
CSE_RBE_CODE_BASE = 0x40000
CSE_RBE_RANGES = {
    "main_key_init_caller": (0x4F5, 0x544, "1a0ca6ba5381d64ba6bb49318a2b874281b3aca4936f6dbf4a0da765ec22365d"),
    "main_entry_to_key_init": (0x7A3, 0x7D3, "04a01423da8a3a279c81e3d56d8fba8d02d1456501c112ca8baafe30b02e0d1c"),
    "cpd_to_snowball_copy": (0x2E61, 0x2F45, "fea37ed17b453e989d0335ad3e6f1054de937d37ab0b94db315601fcb3e0eb25"),
    "key_manifest_materialization": (0x2F45, 0x3058, "120130f519bb739661da5619db740fe7c0bc51073d57137dad1b9c34b98bf798"),
    "data_transfer_wrapper": (0x4451, 0x449C, "e44730fe26601f3b5914add1b155aaa4ad3c83a53837d6511c3167000ad4ab36"),
    "uep_mode_decoder": (0x1DD9, 0x1E04, "0d54af00928548b6341e1b732a09e99f6a6ef2933757ff9aca936c920268db8b"),
    "uep_crc_validator": (0x3814, 0x386E, "2e0b85f5ca73d2928be8c774cb41f2ad0c25819e8df6d054b455ee6a2cfee3cb"),
    "uep_partition_loader": (0x386E, 0x39B9, "a6c13824c9d11f7d2d8ee3f7a46cdc54030013f983b9cdb958b68b4267ad041b"),
    "uep_materializer_and_field_extract": (0x39B9, 0x3B52, "345087daeda534e0376254b8b16d55af4c26c20615bcba00efc033e6788ca143"),
    "oem_key_validation_caller": (0x2B83, 0x2C32, "ef80b6477cc58f10265fcd2b87fc25265e3a1277ea3d472cc1d42bb9f0a78815"),
    "mn2_key_hash_and_signature_validator": (0x2768, 0x2A9F, "7746354214d3c192aad6b206cb7ab3f41157168d3ad3c700eb26a3bbda4c8fee"),
    "uep_bitfield_extractor": (0x774B, 0x78F4, "91cc564e915b626697b61a885197c85d75bfa565e8509472f9359a61687e836b"),
    "ipub_key_materialization": (0x3C5, 0x3FD, "2a68ab7b0a996caa89a80a3c99e49ad56ab74b2394d70f37b1e0040d59713c57"),
    "runtime_object_handoff_lookup": (0x153A, 0x158C, "dc887474f92cbeb125aca70955ab23f66cfbfb4f70d0cdef69ea15aa20aba38f"),
    "runtime_object_handoff_append": (0x158C, 0x1654, "ff433d29a0d043f35609d377e51d218be1fe97d2d8c5e170ceabafece459e006"),
    "rot_key_validation": (0x2A9F, 0x2ADA, "1730fad17c09ae4e10d74c21639905acc97efac3298debcbb92e3999936ad083"),
}
CSE_FTPR_KERNEL_SHA256 = "cf7dd5fc9918f96ffd2352d09a3e303471a768b3a6ee056089dd7a3d5c00bfdf"
CSE_FTPR_KERNEL_METADATA_SHA256 = "f6c17c5b9ce1fc218da9608fce470dfa28fe180d4ec8909da71aa93bbb4b75ed"
CSE_FTPR_KERNEL_CODE_BASE = 0x80000
CSE_FTPR_KERNEL_RANGES = {
    "handoff_page_range_setup": (0x4F4, 0x518, "1592ccf012d9a11485556e08672b44da3f5a726769909f8fd9d5d80686ff6996"),
    "handoff_iterator_init": (0x169F, 0x16D7, "720c7d471eb5cc7c2276dce1304c1b48d1158471beefeb36dbce2c19232f9b78"),
    "process_buffer_validator": (0xA7FF, 0xA8C8, "63295eee91d3c154ff2a70dde41e06af9aa030ec0ffea3d850fc088c41ef1356"),
    "handoff_read_syscall_handler": (0xED23, 0xEDC6, "54091a74c26edf2e4e6bdb631dc75e06105ee2bb66ced42a4d234b7b879b8365"),
    "handoff_iterator_advance": (0xEDC6, 0xEE19, "d9f0fbf021d78ba650ff17217081e6ef2985fb952bb747eac6c19347536d32cb"),
    "handoff_copy": (0xEE19, 0xEE7C, "b7cb1558ae1de8b9d3ecfb93a766dcc5a6427eb83e76f8261044ecf1e59fc1d8"),
}
CSE_BUP_SHA256 = "cee77bc172a9df1c4088d5f716b9e55cda539a26656d07a92268c3cd5d4f0165"
CSE_BUP_CODE_BASE = 0x26000
CSE_BUP_RANGES = {
    "fit_buffer_allocation": (0xB370, 0xB3BD, "a48c73940cd5b9d3c8757edc1d16b29d06bb0a9a15a7e026fa56957346b7e51b"),
    "fit_entry_append": (0x91E9, 0x924F, "a46d35702e79df2cf542d8e9c01e7c55d1a09d9e0357638a4262aab5e05932ef"),
    "oem_key_manifest_fit_publish": (0xB9BC, 0xBAF4, "e18d11f44ce11a7e405399afba236cab0bdd3ce5b24283ccfb0da79f53469c12"),
    "fit_header_init": (0x1409D, 0x140CF, "8429773135288206a92ebdfd3fd4afd5719a9da046f1265d691f32cd40f31f90"),
    "key_manifest_resolver": (0x1F58E, 0x1F871, "5132d70beda6603eaee882917a2723367209c2871a9dc4028ac8602e16b856c3"),
    "ibbl_ibb_member_resolution": (0xB5DB, 0xB664, "db725f0cdcf10dd0c7f9dbfcc67478784ba61a91c40c381834a7e19e03c880e0"),
    "ibbl_tail_placement_copy": (0xBA42, 0xBA7D, "4783f44c2c0c586a5479f365dddc04fbb7d682d6679baa8c2d9df410253de991"),
    "ibb_ring_stream_init": (0x6496, 0x657D, "b5394b6889535d58fedfc076333a14530d2d6f5f638071552a052e7d7a87f41c"),
    "ibb_ring_chunk_loader": (0x657D, 0x66EE, "48a58197fa803564ed3086f2be1c627679b088ce85e6e1bf7dc743c0bb70ecc2"),
    "ibb_ring_completion": (0x66EE, 0x6755, "281a9b2c20a948b461238417e0ff2ccea606e7fda32b015d5ef180396455e537"),
    "fit_base_pointer_for_ibbl": (0xBE27, 0xBE3F, "f21b32ebbc979ec59183fbb17cfdd8f3bebdb3134fe6b0e24641082ee542a49a"),
    "boot_policy_usage32_record_selector": (0x2B4BD, 0x2B4DC, "b0ade2c19d4b92653588ea997cd40bcabcb8df29927b38d9a8c73656097991b9"),
    "boot_policy_oem_key_pin_and_rsa": (0x2B4DC, 0x2B7DB, "a5b7ca06a3b9d48c21494588362856b2badd2d0bcfa9adff6d376a96328350e5"),
    "boot_policy_metadata_hash": (0x2B81A, 0x2B8E9, "f45c5d6b099a209457ed44f3878b4d5158b5a394c32b46724c4f114825e8890c"),
    "uep_interface_to_fpf_shadow": (0xCA1B, 0xCACF, "7a0b5154fad45d4970df385f9629f08d8aad38d548deb153cc14e7fb4664871a"),
    "uep_field_to_fpf_shadow": (0x3B2E, 0x3B7F, "391db9062319f017a0d04e237f43efbd564da59499ef4e6e5e291b5faae78e7f"),
    "bup_fpf_special_file_publish": (0xD357, 0xD377, "fed0c6ccc89cb65ee12a7cbb092e26ee426bdca8c408d1a7841a9e48e1d6587f"),
    "ipub_key_resolver_and_digest_selection": (0x20037, 0x2008E, "ca9020f777d74c52f5845af2e4f33780a77987c06dc412bde731bd552acee958"),
    "snowball_or_runtime_object_resolver": (0x2026A, 0x2039A, "949d25fdaaf94939cfeb489dcbd58ee6108340c7ad8802c120f3dd87072ea64f"),
    "runtime_object_list_materializer": (0x2869, 0x2932, "d37feac50e2e690e2b64c1ba2a52fcde736e1a496fec850bdd5e3212e3149318"),
    "phase_dispatcher": (0x2932, 0x29FE, "d3dff85895dd60d11311069a5395990e92139868ff132f298c4bdb4e5fec7578"),
    "main_phase_zero_and_cleanup": (0x14C72, 0x14CBE, "56f2dc85103cc7c322d4feed67e67a2f16b95ceaddcf84b73a2700fe9c1613f0"),
    "phase_zero_function_table": (0x2E744, 0x2E79C, "57c5e3001f8ff2e41d78af7545d5355c9e177ec5c09a48285c4bc48d932417e0"),
}
DAL_SDM_RANGES = {
    "snowball_ipub_key_policy_read": (0xD0B, 0xDCD, "b83ee973e1fe7333ed95b3d58d277b0dee99a9029f9c13ad79e3f4e8aaa5eef1"),
    "oem_sign_and_key_manifest_gate": (0x1F0F, 0x2025, "e7e55402a39184b7ffcf7691991bfc2ffd4eebfdef8f5e888c54ce37e0c60bcc"),
}
FPF_RANGES = {
    "startup_bup_fpf_and_flash_uep_inputs": (0x200, 0x313, "8d864579abfd7f4226c633aedcbf3e16468ae662c8c8f19be4624d09bfed4ed3"),
    "shadow_or_hardware_field_read": (0x1DBC, 0x1F02, "921f3ab91ad726df1bd5eefe1d50dec18b16edb8b0eef2550fc0aedfd78b36a3"),
    "hardware_mode_activation_and_field_sequence": (0x2D2C, 0x2FB2, "482aa6b11ab4989412e4da22948e66ed9be9b1020028c57e474d6b1235dbf7c8"),
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


def archive_one(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise Failure(f"cannot safely open archive: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size != UPDATE_SIZE:
            raise Failure("archive size/type mismatch")
        digest = hashlib.sha256()
        left = UPDATE_SIZE
        while left:
            chunk = os.read(fd, min(left, 1 << 20))
            if not chunk:
                raise Failure("short archive read")
            digest.update(chunk)
            left -= len(chunk)
        if digest.hexdigest() != UPDATE_SHA256 or _identity(before) != _identity(os.fstat(fd)):
            raise Failure("archive identity mismatch")
        os.lseek(fd, 0, os.SEEK_SET)
        found: list[bytes] = []
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
                        if name != ABL_MEMBER:
                            continue
                        if (
                            not member.isreg()
                            or member.size != ABL_SIZE
                            or member.mode & 0o7777 != 0o755
                            or member.uid != 8100
                            or member.gid != 8100
                        ):
                            raise Failure("selected ABL member metadata drift")
                        source = archive.extractfile(member)
                        if source is None:
                            raise Failure("selected ABL member unreadable")
                        data = source.read(ABL_SIZE + 1)
                        if len(data) != ABL_SIZE or hashlib.sha256(data).hexdigest() != ABL_SHA256:
                            raise Failure("selected ABL member content drift")
                        found.append(data)
            except (tarfile.TarError, OSError, EOFError) as exc:
                raise Failure(f"archive parse failure: {exc}") from exc
        if len(found) != 1 or _identity(before) != _identity(os.fstat(fd)):
            raise Failure("selected ABL multiplicity/change")
        return found[0]
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


def git_blob(repo: Path, commit: str, name: str, wanted: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), "show", f"{commit}:{name}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Failure(f"git source read failed: {exc}") from exc
    if result.returncode or hashlib.sha256(result.stdout).hexdigest() != wanted:
        raise Failure(f"public source identity mismatch: {name}")
    return result.stdout


def require_once(source: bytes, needle: bytes, label: str) -> None:
    if source.count(needle) != 1:
        raise Failure(f"public source semantic anchor multiplicity: {label}")


def extract_ibb(abl: bytes) -> tuple[bytes, bytes]:
    if struct.unpack_from("<IIBBBBI", abl, 0x187000)[:6] != (0x44504324, 4, 1, 1, 16, 50):
        raise Failure("IBB CPD drift")
    entries = []
    for index in range(4):
        name, raw_offset, size, _ = struct.unpack_from("<12sIII", abl, 0x187010 + index * 24)
        entries.append((name.rstrip(b"\0").decode("ascii"), raw_offset & 0x1FFFFFF, size))
    expected = [
        ("IBBP.man", 0x70, 0x2EC),
        ("BPM.met", 0x380, 0xB4),
        ("IBBL", 0x440, 0x4000),
        ("IBB", 0x4440, 0x34000),
    ]
    if entries != expected:
        raise Failure("IBB CPD entries drift")
    ibbl = abl[0x187000 + 0x440 : 0x187000 + 0x440 + 0x4000]
    if hashlib.sha256(ibbl).hexdigest() != IBBL_SHA256:
        raise Failure("IBBL identity drift")
    ias = 0x187000 + 0x4440
    header = struct.unpack_from("<7I", abl, ias)
    if header != (0x2E6B7069, 0, 0, 0x33CD4, 0x2C, 0x33CD4, 0xF753ACFA):
        raise Failure("IBB IAS header drift")
    sizes = struct.unpack_from("<4I", abl, ias + 0x1C)
    if sizes != (0xC0, 0x172D2, 0x44A9, 0x18493):
        raise Failure("IBB subimage table drift")
    pos = ias + 0x2C
    subimages = []
    for index, size in enumerate(sizes):
        subimages.append(abl[pos : pos + size])
        pos += size
        if index + 1 < len(sizes):
            pos = (pos + 3) & ~3
    packed = subimages[1]
    output_size = struct.unpack_from("<I", packed)[0]
    if output_size != 0x1FE00:
        raise Failure("stage-1 output size drift")
    stage1 = lz4_block(packed[4:-4], output_size)
    if hashlib.sha256(stage1).hexdigest() != STAGE1_SHA256:
        raise Failure("stage-1 identity drift")
    return ibbl, stage1


def check_ranges(data: bytes, ranges: dict[str, tuple[int, int, str]], label: str) -> dict[str, dict]:
    result = {}
    for name, (start, end, digest) in ranges.items():
        if end > len(data) or hashlib.sha256(data[start:end]).hexdigest() != digest:
            raise Failure(f"{label} instruction range drift: {name}")
        result[name] = {"file_start": start, "file_end": end, "sha256": digest}
    return result


def extract_cse_rbe(abl: bytes) -> bytes:
    cpd = 0x104000
    if struct.unpack_from("<IIBBBBI", abl, cpd)[:6] != (0x44504324, 3, 1, 1, 16, 115):
        raise Failure("RBEP CPD header drift")
    entries = []
    for index in range(3):
        raw_name, raw_offset, size, _ = struct.unpack_from("<12sIII", abl, cpd + 0x10 + index * 24)
        entries.append((raw_name.rstrip(b"\0").decode("ascii"), raw_offset & 0x1FFFFFF, size))
    matches = [entry for entry in entries if entry[0] == "rbe"]
    if matches != [("rbe", 0x1000, 0x9000)]:
        raise Failure("RBEP rbe entry drift")
    start = cpd + matches[0][1]
    rbe = abl[start : start + matches[0][2]]
    if len(rbe) != 0x9000 or hashlib.sha256(rbe).hexdigest() != CSE_RBE_SHA256:
        raise Failure("CSE RBE identity drift")
    return rbe


def extract_cse_ftpr_kernel(abl: bytes) -> tuple[bytes, bytes, bytes]:
    cpd = 0x11E000
    if struct.unpack_from("<IIBBBBI", abl, cpd)[:6] != (0x44504324, 12, 1, 1, 16, 150):
        raise Failure("FTPR CPD header drift")
    entries = []
    for index in range(12):
        raw_name, raw_offset, size, _ = struct.unpack_from("<12sIII", abl, cpd + 0x10 + index * 24)
        entries.append((raw_name.rstrip(b"\0").decode("ascii"), raw_offset & 0x1FFFFFF, size))
    expected = {
        "FTPR.man": (0x130, 0xC14),
        "kernel": (0x2000, 0x12000),
        "kernel.met": (0xD44, 0x8E),
    }
    selected = {name: (offset, size) for name, offset, size in entries if name in expected}
    if selected != expected:
        raise Failure("FTPR kernel members drift")
    manifest = abl[cpd + 0x130 : cpd + 0x130 + 0xC14]
    metadata = abl[cpd + 0xD44 : cpd + 0xD44 + 0x8E]
    kernel = abl[cpd + 0x2000 : cpd + 0x2000 + 0x12000]
    if hashlib.sha256(metadata).hexdigest() != CSE_FTPR_KERNEL_METADATA_SHA256:
        raise Failure("FTPR kernel metadata identity drift")
    if hashlib.sha256(kernel).hexdigest() != CSE_FTPR_KERNEL_SHA256:
        raise Failure("FTPR kernel identity drift")
    if manifest.count(hashlib.sha256(metadata).digest()[::-1]) != 1:
        raise Failure("FTPR manifest to kernel metadata binding drift")
    if metadata.count(hashlib.sha256(kernel).digest()[::-1]) != 1:
        raise Failure("FTPR kernel metadata to kernel binding drift")
    extensions = parse_metadata_extensions(metadata, "FTPR kernel metadata")
    if sorted(extensions) != [5, 10, 11]:
        raise Failure("FTPR kernel metadata extension set drift")
    process = extensions[5]
    if struct.unpack_from("<I", process, 0x10)[0] != CSE_FTPR_KERNEL_CODE_BASE:
        raise Failure("FTPR kernel code base drift")
    if struct.unpack_from("<I", process, 0x24)[0] != CSE_FTPR_KERNEL_CODE_BASE:
        raise Failure("FTPR kernel entry point drift")
    return kernel, metadata, manifest


def extract_cse_bup(abl: bytes) -> bytes:
    cpd = 0x11E000
    entries = []
    for index in range(12):
        raw_name, raw_offset, size, _ = struct.unpack_from("<12sIII", abl, cpd + 0x10 + index * 24)
        entries.append((raw_name.rstrip(b"\0").decode("ascii"), raw_offset & 0x1FFFFFF, size))
    matches = [entry for entry in entries if entry[0] == "bup"]
    if matches != [("bup", 0x27000, 0x33000)]:
        raise Failure("FTPR bup entry drift")
    start = cpd + matches[0][1]
    bup = abl[start : start + matches[0][2]]
    if len(bup) != 0x33000 or hashlib.sha256(bup).hexdigest() != CSE_BUP_SHA256:
        raise Failure("CSE BUP identity drift")
    return bup


def parse_metadata_extensions(metadata: bytes, label: str) -> dict[int, bytes]:
    extensions: dict[int, bytes] = {}
    pos = 0
    while pos < len(metadata):
        if pos + 8 > len(metadata):
            raise Failure(f"{label} truncated extension header")
        tag, size = struct.unpack_from("<II", metadata, pos)
        if tag in extensions or size < 8 or pos + size > len(metadata):
            raise Failure(f"{label} extension geometry drift")
        extensions[tag] = metadata[pos : pos + size]
        pos += size
    if pos != len(metadata):
        raise Failure(f"{label} extension traversal drift")
    return extensions


def parse_special_files(extension: bytes, label: str) -> dict:
    if len(extension) < 12 or struct.unpack_from("<I", extension, 0)[0] != 9 or (len(extension) - 12) % 24:
        raise Failure(f"{label} special-file extension drift")
    major = struct.unpack_from("<I", extension, 8)[0]
    entries = []
    for pos in range(12, len(extension), 24):
        raw_name = extension[pos : pos + 12]
        if b"\0" not in raw_name:
            raise Failure(f"{label} unterminated special-file name")
        name = raw_name.split(b"\0", 1)[0].decode("ascii")
        access, user, group, minor, reserved = struct.unpack_from("<HHHHI", extension, pos + 12)
        entries.append(
            {
                "name": name,
                "access_mode": access,
                "user_id": user,
                "group_id": group,
                "minor": minor,
                "reserved": reserved,
            }
        )
    return {"major": major, "entries": entries}


def extract_dal_sdm_snowball_policy(abl: bytes) -> dict:
    cpd = 0x203000
    entries = []
    for index in range(69):
        raw_name, raw_offset, size, _ = struct.unpack_from("<12sIII", abl, cpd + 0x10 + index * 24)
        entries.append((raw_name.rstrip(b"\0").decode("ascii"), raw_offset & 0x1FFFFFF, size))
    selected = [entry for entry in entries if entry[0] in ("dal_sdm", "dal_sdm.met")]
    if selected != [("dal_sdm", 0xE3000, DAL_SDM_COMPRESSED_SIZE), ("dal_sdm.met", 0x3D80, DAL_SDM_MET_SIZE)]:
        raise Failure("NFTP dal_sdm CPD entries drift")

    compressed = abl[DAL_SDM_COMPRESSED_OFFSET : DAL_SDM_COMPRESSED_OFFSET + DAL_SDM_COMPRESSED_SIZE]
    metadata = abl[DAL_SDM_MET_OFFSET : DAL_SDM_MET_OFFSET + DAL_SDM_MET_SIZE]
    manifest = abl[0x203688 : 0x203688 + 0x9A0]
    for blob, size, digest, label in (
        (compressed, DAL_SDM_COMPRESSED_SIZE, DAL_SDM_COMPRESSED_SHA256, "compressed dal_sdm"),
        (metadata, DAL_SDM_MET_SIZE, DAL_SDM_MET_SHA256, "dal_sdm.met"),
        (manifest, 0x9A0, NFTP_MAN_SHA256, "NFTP.man"),
    ):
        if len(blob) != size or hashlib.sha256(blob).hexdigest() != digest:
            raise Failure(f"{label} identity drift")
    if manifest.count(hashlib.sha256(metadata).digest()[::-1]) != 1:
        raise Failure("NFTP.man to dal_sdm.met signed hash chain drift")

    extensions = parse_metadata_extensions(metadata, "dal_sdm.met")
    module = extensions.get(10)
    if module is None or len(module) != 0x38:
        raise Failure("dal_sdm.met module extension drift")
    compression = module[8]
    uncompressed_size, compressed_size = struct.unpack_from("<II", module, 0x0C)
    if (
        compression != 2
        or uncompressed_size != DAL_SDM_SIZE
        or compressed_size != DAL_SDM_COMPRESSED_SIZE
        or module[0x18:0x38] != hashlib.sha256(compressed).digest()[::-1]
    ):
        raise Failure("dal_sdm.met compressed module binding drift")
    if not compressed.startswith(bytes.fromhex("3600400000")) or compressed[0x0E:0x11] != b"\0\0\0":
        raise Failure("dal_sdm Intel CSE LZMA header drift")
    try:
        decoder = lzma.LZMADecompressor()
        dal_sdm = decoder.decompress(compressed[:0x0E] + compressed[0x11:])
    except lzma.LZMAError as exc:
        raise Failure(f"dal_sdm LZMA decompression failure: {exc}") from exc
    if (
        not decoder.eof
        or decoder.unused_data
        or len(dal_sdm) != DAL_SDM_SIZE
        or hashlib.sha256(dal_sdm).hexdigest() != DAL_SDM_SHA256
    ):
        raise Failure("decompressed dal_sdm identity drift")
    strings = {
        "ipub_key": (0xC466, b"/snowball/ipub_key\0"),
        "uniquepid": (0xC49C, b"/snowball/uniquepid\0"),
        "oem_sign": (0xC4D8, b"/snowball/oem_sign\0"),
        "oem_key_man": (0xC4EB, b"/snowball/oem_key_man\0"),
    }
    for label, (offset, value) in strings.items():
        if dal_sdm[offset : offset + len(value)] != value or dal_sdm.count(value) != 1:
            raise Failure(f"dal_sdm {label} string drift")

    return {
        "signed_chain": {
            "nftp_manifest": {"flash_offset": 0x203688, "size": 0x9A0, "sha256": NFTP_MAN_SHA256},
            "dal_sdm_metadata": {"flash_offset": DAL_SDM_MET_OFFSET, "size": DAL_SDM_MET_SIZE, "sha256": DAL_SDM_MET_SHA256},
            "dal_sdm_compressed": {"flash_offset": DAL_SDM_COMPRESSED_OFFSET, "size": DAL_SDM_COMPRESSED_SIZE, "sha256": DAL_SDM_COMPRESSED_SHA256},
            "dal_sdm_decompressed": {"size": DAL_SDM_SIZE, "sha256": DAL_SDM_SHA256},
            "nftp_manifest_binds_dal_sdm_metadata": True,
            "dal_sdm_metadata_binds_compressed_module": True,
        },
        "instruction_ranges": check_ranges(dal_sdm, DAL_SDM_RANGES, "NFTP dal_sdm"),
        "snowball_paths": {label: {"file_offset": offset, "runtime_address": 0x26000 + offset} for label, (offset, _) in strings.items()},
        "ipub_key_policy": {
            "open_flags": 0,
            "exact_read_size": 0x24,
            "requires_exact_read": True,
            "state_bit_offset": 1,
            "state_bit_mask": 1,
            "conditional_dword_offset": 4,
            "when_state_bit_clear_result": True,
            "when_state_bit_set_requires_dword_zero": True,
            "ipub_key_write_observed_in_range": False,
        },
        "oem_gate": {
            "ipub_policy_checked_before_oem_objects": True,
            "oem_sign_exact_read_size": 1,
            "oem_sign_must_be_nonzero": True,
            "oem_key_manifest_max_read": 0x1000,
        },
        "snowball_ipub_key_is_shared_cse_policy_object_proved": True,
        "snowball_ipub_key_producer_or_writability_proved": False,
        "physical_fuse_or_rom_authority_proved": False,
    }


def extract_fpf_provisioning_handoff(abl: bytes, bup: bytes) -> dict:
    cpd = 0x203000
    if struct.unpack_from("<IIBBBBI", abl, cpd)[:6] != (0x44504324, 69, 1, 1, 16, 240):
        raise Failure("NFTP CPD header drift")
    entries = []
    for index in range(69):
        raw_name, raw_offset, size, _ = struct.unpack_from("<12sIII", abl, cpd + 0x10 + index * 24)
        entries.append((raw_name.rstrip(b"\0").decode("ascii"), raw_offset & 0x1FFFFFF, size))
    fpf_entries = [entry for entry in entries if entry[0] in ("fpf", "fpf.met")]
    if fpf_entries != [("fpf", 0x65000, FPF_COMPRESSED_SIZE), ("fpf.met", 0x2F6C, FPF_MET_SIZE)]:
        raise Failure("NFTP fpf CPD entries drift")

    compressed = abl[FPF_COMPRESSED_OFFSET : FPF_COMPRESSED_OFFSET + FPF_COMPRESSED_SIZE]
    metadata = abl[FPF_MET_OFFSET : FPF_MET_OFFSET + FPF_MET_SIZE]
    manifest = abl[0x203688 : 0x203688 + 0x9A0]
    bup_metadata = abl[0x11EE36 : 0x11EE36 + 0x4A6]
    identities = (
        (compressed, FPF_COMPRESSED_SIZE, FPF_COMPRESSED_SHA256, "compressed fpf"),
        (metadata, FPF_MET_SIZE, FPF_MET_SHA256, "fpf.met"),
        (manifest, 0x9A0, NFTP_MAN_SHA256, "NFTP.man"),
        (bup_metadata, 0x4A6, BUP_MET_SHA256, "bup.met"),
    )
    for blob, size, digest, label in identities:
        if len(blob) != size or hashlib.sha256(blob).hexdigest() != digest:
            raise Failure(f"{label} identity drift")
    if manifest.count(hashlib.sha256(metadata).digest()[::-1]) != 1:
        raise Failure("NFTP.man to fpf.met signed hash chain drift")

    fpf_extensions = parse_metadata_extensions(metadata, "fpf.met")
    bup_extensions = parse_metadata_extensions(bup_metadata, "bup.met")
    module = fpf_extensions.get(10)
    if module is None or len(module) != 0x38:
        raise Failure("fpf.met module extension drift")
    compression = module[8]
    uncompressed_size, compressed_size = struct.unpack_from("<II", module, 0x0C)
    if (
        compression != 2
        or uncompressed_size != FPF_SIZE
        or compressed_size != FPF_COMPRESSED_SIZE
        or module[0x18:0x38] != hashlib.sha256(compressed).digest()[::-1]
    ):
        raise Failure("fpf.met compressed module binding drift")

    if not compressed.startswith(bytes.fromhex("3600400000")) or compressed[0x0E:0x11] != b"\0\0\0":
        raise Failure("Intel CSE LZMA header drift")
    adjusted = compressed[:0x0E] + compressed[0x11:]
    try:
        decoder = lzma.LZMADecompressor()
        fpf = decoder.decompress(adjusted)
    except lzma.LZMAError as exc:
        raise Failure(f"fpf LZMA decompression failure: {exc}") from exc
    if (
        not decoder.eof
        or decoder.unused_data
        or len(fpf) != FPF_SIZE
        or hashlib.sha256(fpf).hexdigest() != FPF_SHA256
    ):
        raise Failure("decompressed fpf identity drift")

    fpf_special = parse_special_files(fpf_extensions[9], "fpf.met")
    bup_special = parse_special_files(bup_extensions[9], "bup.met")
    expected_fpf_special = [
        {"name": "fpf", "access_mode": 0x1B0, "user_id": 0x1D, "group_id": 0x36, "minor": 0, "reserved": 0},
        {"name": "fpf_hw_use", "access_mode": 0x1B0, "user_id": 0x1D, "group_id": 0xDF, "minor": 1, "reserved": 0},
    ]
    if fpf_special != {"major": 23, "entries": expected_fpf_special}:
        raise Failure("fpf special-file metadata drift")
    bup_fpf = [entry for entry in bup_special["entries"] if entry["name"] == "bup_fpf"]
    if bup_special["major"] != 30 or bup_fpf != [
        {"name": "bup_fpf", "access_mode": 0x1B0, "user_id": 3, "group_id": 0x58, "minor": 7, "reserved": 0}
    ]:
        raise Failure("BUP bup_fpf special-file metadata drift")

    fpf_ranges = check_ranges(fpf, FPF_RANGES, "NFTP fpf")
    if fpf.find(b"/dev/bup_fpf\0") != 0x3DE0 or fpf.find(b"/dev/flash/uep\0") != 0x3DF9:
        raise Failure("fpf input path strings drift")
    if fpf[0x5688:0x569C] != struct.pack("<IIIII", 0x27D53, 0x28D2C, 0x28FB2, 0x290F1, 0xFFFFFFFF):
        raise Failure("fpf OemLock callback table drift")
    if fpf[0x5668:0x5670] != b"OemLock\0":
        raise Failure("fpf OemLock name drift")
    if [index for index in range(len(bup)) if bup.startswith(b"ifp_uep\0", index)] != [0x2E456, 0x2EAA0]:
        raise Failure("BUP ifp_uep interface string drift")

    return {
        "signed_chain": {
            "nftp_manifest": {"flash_offset": 0x203688, "size": 0x9A0, "sha256": NFTP_MAN_SHA256},
            "fpf_metadata": {"flash_offset": FPF_MET_OFFSET, "size": FPF_MET_SIZE, "sha256": FPF_MET_SHA256},
            "fpf_compressed": {"flash_offset": FPF_COMPRESSED_OFFSET, "size": FPF_COMPRESSED_SIZE, "sha256": FPF_COMPRESSED_SHA256},
            "fpf_decompressed": {"size": FPF_SIZE, "sha256": FPF_SHA256},
            "nftp_manifest_binds_fpf_metadata": True,
            "fpf_metadata_binds_compressed_fpf": True,
            "nftp_manifest_embedded_signature_valid": True,
            "nftp_manifest_rooted_in_runtime_ipub_key_if_that_object_is_anchored": True,
        },
        "bup_special_file": bup_fpf[0],
        "fpf_special_files": fpf_special,
        "instruction_ranges": fpf_ranges,
        "handoff": {
            "rbe_output_object": "ifp_uep",
            "rbe_output_object_size": 0x108,
            "rbe_hardware_route_marker": "REAL",
            "rbe_flash_route_marker": "$UEP",
            "rbe_selected_uep_payload_offset": 8,
            "rbe_selected_uep_payload_size": 0x100,
            "bup_resolves_object": "ifp_uep",
            "bup_lookup_result_null_check_before_dereference": False,
            "bup_payload_size_check_before_fixed_copy": False,
            "bup_fixed_header_copy_size": 8,
            "bup_fixed_payload_copy_size": 0x100,
            "bup_runtime_object_list_is_prepend_order": True,
            "bup_named_lookup_returns_first_match": True,
            "bup_last_ingested_duplicate_name_wins": True,
            "rbe_stock_producer_allocates_exact_required_size": True,
            "malformed_or_duplicate_ifp_uep_attacker_control_proved": False,
            "bup_compares_header_with_marker": "REAL",
            "bup_real_marker_global": 0xA4074,
            "bup_rejects_non_real_marker": False,
            "bup_copies_payload_to_global": 0xA37F8,
            "bup_initial_copy_size": 0x100,
            "bup_initial_payload_copy_byte_identity_proved": True,
            "bup_later_field_assembly_can_update_shadow": True,
            "full_initial_payload_byte_identity_at_publication_proved": False,
            "bup_publishes_special_file": "/dev/bup_fpf",
            "bup_published_buffer_global": 0xA37F8,
            "bup_published_size": 0x880,
            "fpf_requires_bup_fpf_size": 0x880,
            "fpf_shadow_global": 0x366E4,
            "fpf_hardware_mode_global": 0x36F60,
            "fpf_flash_uep_path": "/dev/flash/uep",
            "shadow_reads_used_while_hardware_mode_zero": True,
            "hardware_access_used_while_hardware_mode_nonzero": True,
            "oem_lock_callback_sets_hardware_mode_before_field_sequence": True,
            "selected_uep_to_bup_fpf_to_nftp_fpf_shadow_proved": True,
            "nftp_fpf_hardware_state_equated_to_rbe_hardware_window": False,
        },
        "boundary": "The selected RBE UEP payload is copied exactly into BUP's FPF shadow before BUP's later field-assembly path can update that shadow; the resulting 0x880-byte object is consumed by the signed NFTP fpf service. This proves later provisioning dataflow, not full initial-payload byte identity at publication or who authenticates and immutably supplies the earlier RBE hardware-window/BPDT source.",
    }


def verify_mn2_embedded_signature(manifest: bytes, label: str) -> dict:
    if len(manifest) < 0x284 or manifest[0x1C:0x20] != b"$MN2":
        raise Failure(f"{label} $MN2 header drift")
    header_size = struct.unpack_from("<I", manifest, 4)[0] * 4
    manifest_size = struct.unpack_from("<I", manifest, 0x18)[0] * 4
    public_key_size = struct.unpack_from("<I", manifest, 0x78)[0] * 4
    exponent_size = struct.unpack_from("<I", manifest, 0x7C)[0] * 4
    if header_size != 0x284 or manifest_size != len(manifest) or public_key_size != 0x100 or exponent_size != 4:
        raise Failure(f"{label} $MN2 geometry drift")
    modulus = manifest[0x80:0x180]
    exponent_bytes = manifest[0x180:0x184]
    signature = manifest[0x184:0x284]
    exponent = int.from_bytes(exponent_bytes, "little")
    signed_digest = hashlib.sha256(manifest[:0x80] + manifest[header_size:manifest_size]).digest()
    encoded = pow(int.from_bytes(signature, "little"), exponent, int.from_bytes(modulus, "little")).to_bytes(
        public_key_size, "big"
    )
    separator = encoded.find(b"\0", 2)
    valid = (
        encoded.startswith(b"\0\1")
        and separator >= 10
        and encoded[2:separator] == b"\xff" * (separator - 2)
        and encoded[separator + 1 :] == bytes.fromhex("3031300d060960864801650304020105000420") + signed_digest
    )
    if not valid:
        raise Failure(f"{label} embedded RSA signature failure")
    return {
        "tag": "$MN2",
        "header_size": header_size,
        "total_size": manifest_size,
        "public_key_size": public_key_size,
        "exponent": exponent,
        "embedded_signature_valid": True,
        "embedded_signature_boundary": "self-consistency only; no external root established",
    }


def parse_cse_signed_module_chains(abl: bytes, rbe: bytes, bup: bytes) -> dict:
    members = {
        "rbep_manifest": (0x104058, 0x2EC, RBEP_MAN_SHA256),
        "rbe_metadata": (0x104344, 0xAE, RBE_MET_SHA256),
        "ftpr_manifest": (0x11E130, 0xC14, FTPR_MAN_SHA256),
        "bup_metadata": (0x11EE36, 0x4A6, BUP_MET_SHA256),
    }
    blobs = {}
    identities = {}
    for name, (offset, size, digest) in members.items():
        blob = abl[offset : offset + size]
        if len(blob) != size or hashlib.sha256(blob).hexdigest() != digest:
            raise Failure(f"{name} identity drift")
        blobs[name] = blob
        identities[name] = {"flash_offset": offset, "size": size, "sha256": digest}
    rbep_manifest = blobs["rbep_manifest"]
    rbe_metadata = blobs["rbe_metadata"]
    ftpr_manifest = blobs["ftpr_manifest"]
    bup_metadata = blobs["bup_metadata"]
    if rbep_manifest.count(hashlib.sha256(rbe_metadata).digest()[::-1]) != 1:
        raise Failure("RBEP signed metadata hash chain drift")
    if rbe_metadata.count(hashlib.sha256(rbe).digest()[::-1]) != 1:
        raise Failure("RBE module hash chain drift")
    if ftpr_manifest.count(hashlib.sha256(bup_metadata).digest()[::-1]) != 1:
        raise Failure("FTPR signed metadata hash chain drift")
    if bup_metadata.count(hashlib.sha256(bup).digest()[::-1]) != 1:
        raise Failure("BUP module hash chain drift")
    oem_digest = bytes.fromhex(OEM_KEY_SHA256)
    if ftpr_manifest.count(b"oem.key") or ftpr_manifest.count(oem_digest) or ftpr_manifest.count(oem_digest[::-1]):
        raise Failure("unexpected direct FTPR.man oem.key coverage")
    identities["rbep_manifest"]["manifest"] = verify_mn2_embedded_signature(rbep_manifest, "RBEP.man")
    identities["ftpr_manifest"]["manifest"] = verify_mn2_embedded_signature(ftpr_manifest, "FTPR.man")
    return {
        "members": identities,
        "rbep_manifest_to_rbe_metadata_to_rbe_bytes_proved": True,
        "ftpr_manifest_to_bup_metadata_to_bup_bytes_proved": True,
        "stored_hash_encoding": "reverse(SHA-256 bytes)",
        "ftpr_manifest_direct_oem_key_name_or_digest_coverage_found": False,
        "ftpr_cpd_oem_key_metadata_member_present": False,
        "external_manifest_key_anchor_proved": False,
    }


def parse_cse_root_and_boot_policy_chains(abl: bytes) -> dict:
    members = {
        "rot_key": (ROT_KEY_OFFSET, ROT_KEY_SIZE, ROT_KEY_SHA256),
        "rbep_manifest": (0x104058, 0x2EC, RBEP_MAN_SHA256),
        "ftpr_manifest": (0x11E130, 0xC14, FTPR_MAN_SHA256),
        "nftp_manifest": (0x203688, 0x9A0, NFTP_MAN_SHA256),
        "ibbp_manifest": (0x187070, 0x2EC, IBBP_MAN_SHA256),
        "bpm_metadata": (0x187380, 0xB4, BPM_MET_SHA256),
        "ibbl": (0x187440, 0x4000, IBBL_SHA256),
        "ibb": (0x18B440, 0x34000, IBB_SHA256),
    }
    blobs = {}
    identities = {}
    for name, (offset, size, digest) in members.items():
        blob = abl[offset : offset + size]
        if len(blob) != size or hashlib.sha256(blob).hexdigest() != digest:
            raise Failure(f"CSE root-chain member identity drift: {name}")
        blobs[name] = blob
        identities[name] = {"flash_offset": offset, "size": size, "sha256": digest}

    signed_names = ("rot_key", "rbep_manifest", "ftpr_manifest", "nftp_manifest", "ibbp_manifest")
    key_digests = {}
    for name in signed_names:
        identities[name]["manifest"] = verify_mn2_embedded_signature(blobs[name], name)
        key_digests[name] = hashlib.sha256(blobs[name][0x80:0x184]).hexdigest()
        identities[name]["manifest_public_key_digest"] = key_digests[name]

    intel_signed = ("rot_key", "rbep_manifest", "ftpr_manifest", "nftp_manifest")
    intel_public_keys = [blobs[name][0x80:0x184] for name in intel_signed]
    if any(key_digests[name] != INTEL_ROOT_KEY_DIGEST for name in intel_signed) or any(
        key != intel_public_keys[0] for key in intel_public_keys[1:]
    ):
        raise Failure("shared CSE manifest signing-key identity drift")
    if key_digests["ibbp_manifest"] != STORED_USAGE39_DIGEST:
        raise Failure("IBBP OEM signing-key digest drift")

    rot = blobs["rot_key"]
    ext_tag, ext_size, key_type = struct.unpack_from("<III", rot, 0x284)
    if (ext_tag, ext_size, key_type) != (0x0E, 0x178, 1) or (ext_size - 0x24) // 0x44 != 5:
        raise Failure("rot.key extension-14 geometry drift")
    rot_records = []
    for index in range(5):
        offset = 0x2A8 + index * 0x44
        usage = [bit for bit in range(128) if rot[offset + bit // 8] & (1 << (bit & 7))]
        flags = rot[offset + 0x20]
        algorithm = rot[offset + 0x21]
        digest_size = struct.unpack_from("<H", rot, offset + 0x22)[0]
        digest = rot[offset + 0x24 : offset + 0x44].hex()
        if algorithm != 2 or digest_size != 0x20:
            raise Failure("rot.key extension-14 record drift")
        rot_records.append({"index": index, "usage_bits": usage, "flags": flags, "digest": digest})
    if rot_records[0] != {
        "index": 0,
        "usage_bits": [0, 1],
        "flags": 1,
        "digest": INTEL_ROOT_KEY_DIGEST,
    }:
        raise Failure("rot.key CSE BUP/Main record drift")
    intel_digest = bytes.fromhex(INTEL_ROOT_KEY_DIGEST)
    intel_digest_offsets = [index for index in range(len(abl)) if abl.startswith(intel_digest, index)]
    if intel_digest_offsets != [ROT_KEY_OFFSET + 0x2CC]:
        raise Failure("static Intel root-key digest occurrence drift")

    oem = abl[OEM_KEY_OFFSET : OEM_KEY_OFFSET + OEM_KEY_SIZE]
    if blobs["ibbp_manifest"][0x80:0x184] != oem[0x80:0x184]:
        raise Failure("IBBP and oem.key public-key byte identity drift")
    oem_boot_policy_record = oem[0x2A8 : 0x2A8 + 0x44]
    oem_boot_usage = [bit for bit in range(128) if oem_boot_policy_record[bit // 8] & (1 << (bit & 7))]
    if (
        oem_boot_usage != [32]
        or oem_boot_policy_record[0x20] != 0
        or oem_boot_policy_record[0x21] != 2
        or struct.unpack_from("<H", oem_boot_policy_record, 0x22)[0] != 0x20
        or oem_boot_policy_record[0x24:0x44].hex() != STORED_USAGE39_DIGEST
    ):
        raise Failure("oem.key Boot Policy usage-32 record drift")

    ibbp = blobs["ibbp_manifest"]
    bpm = blobs["bpm_metadata"]
    bpm_digest = hashlib.sha256(bpm).digest()
    if ibbp.count(b"BPM.met") != 1 or ibbp.count(bpm_digest[::-1]) != 1:
        raise Failure("IBBP.man to BPM.met signed hash chain drift")
    if struct.unpack_from("<II", bpm, 0) != (0x13, 0xB4):
        raise Failure("BPM.met extension-19 header drift")
    if struct.unpack_from("<II", bpm, 0x0C) != (2, 0x20) or struct.unpack_from("<II", bpm, 0x34) != (2, 0x20):
        raise Failure("BPM.met IBB hash geometry drift")
    ibbl_digest = bpm[0x14:0x34].hex()
    ibb_digest = bpm[0x3C:0x5C].hex()
    if ibbl_digest != IBBL_SHA256 or ibb_digest != IBB_SHA256:
        raise Failure("BPM.met exact IBBL/IBB digest binding drift")

    return {
        "members": identities,
        "intel_manifest_key_chain": {
            "rbe_runtime_root_object_name": "ipub_key",
            "rbe_runtime_root_digest_destination": 0x6047FA8,
            "rbe_runtime_root_digest_size": 0x20,
            "rbe_runtime_selector_offset": 0x12,
            "rbe_runtime_pointer_array_offset": 0x16,
            "rot_key_validator_expected_hash_pointer": 0x6047FA8,
            "rot_key_validator_selector": 5,
            "shared_manifest_public_key_digest": INTEL_ROOT_KEY_DIGEST,
            "shared_by": list(intel_signed),
            "shared_public_modulus_and_exponent_bytes_identical": True,
            "rot_key_extension14_cse_bup_main_record": rot_records[0],
            "rbe_ipub_key_to_rot_key_pin_proved": True,
            "rbe_runtime_object_handoff": {
                "base": 0x08200000,
                "maximum_total_size": 0x8000,
                "first_entry": 0x08200008,
                "name_compare_size": 0x0C,
                "enabled_flag_offset": 0x0D,
                "enabled_flag_mask": 0x01,
                "entry_total_size_offset": 0x0E,
                "payload_offset": 0x12,
                "lookup_returns_existing_entry": True,
                "first_rbe_append_name": "cld_rst_blk",
                "required_existing_entry_names": ["bpdt", "pm_trans", "ftpm_fuses", "sss_em", "rbe.man", "pmc_ipc", "ipub_key"],
                "optional_missing_pmc_msg_is_appended_by_rbe": True,
                "rbe_ipub_key_path_uses_lookup_not_append": True,
                "exact_abl_little_endian_base_occurrences": [0x106540, 0x106552, 0x1065BF, 0x1065D6, 0x106645, 0x11CF7D, 0x1204FA, 0x1216A6, 0x1216AE],
                "classified_consumer_occurrences": {
                    "rbe": [0x106540, 0x106552, 0x1065BF, 0x1065D6, 0x106645],
                    "ftpr_kernel": [0x1204FA, 0x1216A6, 0x1216AE],
                },
                "remaining_unaligned_cross_dword_occurrence": {
                    "flash_offset": 0x11CF7D,
                    "containing_dwords": [0x20000000, 0xFF171908],
                    "is_aligned_address_literal": False,
                },
                "other_plain_static_handoff_base_literal_found": False,
                "computed_indirect_or_external_producer_excluded": False,
                "pre_rbe_producer_identity_proved": False,
                "external_authentication_or_immutability_proved": False,
            },
            "rot_key_embedded_signature_valid": True,
            "rbep_ftpr_nftp_embedded_signatures_valid": True,
            "exact_abl_static_digest_occurrences": intel_digest_offsets,
            "exact_abl_static_digest_occurs_only_in_rot_key_record": True,
            "bup_runtime_root_object_name": "ipub_key",
            "bup_runtime_object_list_head_global": 0xA014C,
            "bup_runtime_object_list_initializes_empty": True,
            "bup_runtime_object_layout": {"payload_size_offset": 0x14, "payload_pointer_offset": 0x18, "next_pointer_offset": 0x1C},
            "bup_resolution_rule": "use named runtime-object resolution while list head is nonzero; construct /snowball/<name> only while the list head is zero",
            "bup_snowball_fallback_path": "/snowball/ipub_key",
            "bup_selected_digest_size": 0x20,
            "bup_minimum_accepted_resolved_length": 0x24,
            "bup_resolved_length_must_be_greater_than_0x23": True,
            "bup_resolved_length_semantics": "runtime-object payload size or snowball read return count",
            "bup_selector_byte_offset": 0,
            "bup_selected_pointer_offset_expression": "4 + 4 * selector",
            "bup_selector_upper_bound_check_observed": False,
            "bup_selected_pointer_within_object_bounds_check_observed": False,
            "bup_maximum_in_bounds_selector_for_minimum_size": 7,
            "bup_malformed_object_reachability_or_control_proved": False,
            "bup_snowball_path_selected_at_runtime_proved": False,
            "bup_snowball_object_writable_or_untrusted_proved": False,
            "ipub_key_producer_or_hardware_anchor_proved": False,
            "boundary": "exact RBE looks up ipub_key in an incoming bounded runtime-object handoff at 0x08200000; RBE can append later objects but its ipub_key path does not create that entry. The pre-RBE producer, authentication, mutability, and ROM/fuse provenance remain unproved",
        },
        "oem_boot_policy_chain": {
            "uep_and_oem_key_digest": STORED_USAGE39_DIGEST,
            "ibbp_manifest_public_key_digest": key_digests["ibbp_manifest"],
            "ibbp_manifest_uses_same_public_key_as_oem_key": True,
            "ibbp_and_oem_key_public_modulus_and_exponent_bytes_identical": True,
            "oem_key_usage_bit_for_boot_policy": 32,
            "bup_selects_usage_bit_32_record": True,
            "bup_compares_ibbp_modulus_plus_exponent_hash_before_rsa": True,
            "ibbp_manifest_embedded_signature_valid": True,
            "ibbp_manifest_binds_bpm_metadata_reverse_sha256": True,
            "bpm_metadata_extension_tag": 0x13,
            "bpm_metadata_ibbl_sha256": ibbl_digest,
            "bpm_metadata_ibb_sha256": ibb_digest,
            "bpm_metadata_binds_exact_ibbl": True,
            "bpm_metadata_binds_exact_ibb": True,
            "uep_to_oem_key_to_ibbp_to_bpm_to_ibb_bytes_chain_proved": True,
            "uep_external_authentication_or_fuse_precedence_proved": False,
        },
    }


def uep_hardware_window_selected(mode_nibble: int) -> bool:
    if not isinstance(mode_nibble, int) or not 0 <= mode_nibble <= 0x0F:
        raise Failure("UEP mode nibble outside exact four-bit domain")
    return bool(mode_nibble & 0x0C) and bool(mode_nibble & 0x03)


def parse_uep_oem_hash_candidate(abl: bytes) -> dict:
    bpdt = 0x100000
    entries = [struct.unpack_from("<III", abl, bpdt + 0x18 + index * 12) for index in range(13)]
    if entries[7] != (17, 0x210, UEP_SIZE):
        raise Failure("BPDT UEP entry drift")
    uep = abl[UEP_OFFSET : UEP_OFFSET + UEP_SIZE]
    if len(uep) != UEP_SIZE or hashlib.sha256(uep).hexdigest() != UEP_SHA256 or uep[:4] != b"$UEP":
        raise Failure("UEP identity drift")
    candidates = [uep[0x34:0x3C] + uep[0x40:0x58], uep[0x7C:0x84] + uep[0x90:0xA8], uep[0xCC:0xEC]]
    if any(candidate.hex() != STORED_USAGE39_DIGEST for candidate in candidates):
        raise Failure("UEP OEM hash candidate drift")
    return {
        "bpdt_type": 17,
        "flash_offset": UEP_OFFSET,
        "size": UEP_SIZE,
        "sha256": UEP_SHA256,
        "magic": "$UEP",
        "candidate_offsets": [0x34, 0x7C, 0xCC],
        "candidate_digest": STORED_USAGE39_DIGEST,
        "matches_stored_oem_key_public_key_digest": True,
        "exact_target_consumer_proved": True,
        "rbe_output_global": 0x6048038,
        "rbe_field_index": 0x20,
        "rbe_field_bit_length": 0x100,
        "rbe_field_table_bit_offset": 0x160,
        "rbe_validates_oem_key_public_key_hash_before_rsa": True,
        "external_hardware_or_fuse_anchor_proved": False,
    }


def parse_stored_oem_key(abl: bytes) -> dict:
    cpd = 0x11E000
    if struct.unpack_from("<IIBBBBI", abl, cpd)[:6] != (0x44504324, 12, 1, 1, 16, 150):
        raise Failure("FTPR CPD drift")
    entries = []
    for index in range(12):
        raw_name, raw_offset, size, _ = struct.unpack_from("<12sIII", abl, cpd + 0x10 + index * 24)
        entries.append((raw_name.rstrip(b"\0").decode("ascii"), raw_offset & 0x1FFFFFF, size))
    matches = [entry for entry in entries if entry[0] == "oem.key"]
    if matches != [("oem.key", 0x5E000, OEM_KEY_SIZE)]:
        raise Failure("FTPR oem.key entry drift")
    absolute = cpd + matches[0][1]
    if absolute != OEM_KEY_OFFSET:
        raise Failure("FTPR oem.key absolute offset drift")
    manifest = abl[absolute : absolute + OEM_KEY_SIZE]
    if len(manifest) != OEM_KEY_SIZE or hashlib.sha256(manifest).hexdigest() != OEM_KEY_SHA256:
        raise Failure("stored oem.key identity drift")
    header_type, header_subtype = struct.unpack_from("<HH", manifest, 0)
    header_size = struct.unpack_from("<I", manifest, 4)[0] * 4
    header_version = struct.unpack_from("<I", manifest, 8)[0]
    vendor_id = struct.unpack_from("<I", manifest, 0x10)[0]
    manifest_size = struct.unpack_from("<I", manifest, 0x18)[0] * 4
    tag = manifest[0x1C:0x20]
    public_key_size = struct.unpack_from("<I", manifest, 0x78)[0] * 4
    exponent_size = struct.unpack_from("<I", manifest, 0x7C)[0] * 4
    if (
        (header_type, header_subtype, header_size, header_version, vendor_id, manifest_size, tag)
        != (4, 0, 0x284, 0x10000, 0x8086, OEM_KEY_SIZE, b"$MN2")
        or public_key_size != 0x100
        or exponent_size != 4
    ):
        raise Failure("stored oem.key manifest header drift")
    modulus = manifest[0x80:0x180]
    exponent_bytes = manifest[0x180:0x184]
    signature = manifest[0x184:0x284]
    exponent = int.from_bytes(exponent_bytes, "little")
    signed_data = manifest[:0x80] + manifest[header_size:manifest_size]
    signed_digest = hashlib.sha256(signed_data).digest()
    encoded = pow(int.from_bytes(signature, "little"), exponent, int.from_bytes(modulus, "little")).to_bytes(
        public_key_size, "big"
    )
    separator = encoded.find(b"\0", 2)
    signature_valid = (
        encoded.startswith(b"\0\1")
        and separator >= 10
        and encoded[2:separator] == b"\xff" * (separator - 2)
        and encoded[separator + 1 :] == bytes.fromhex("3031300d060960864801650304020105000420") + signed_digest
    )
    if not signature_valid:
        raise Failure("stored oem.key embedded RSA signature failure")
    extension_tag, extension_size = struct.unpack_from("<II", manifest, 0x284)
    key_type = struct.unpack_from("<I", manifest, 0x28C)[0]
    if (extension_tag, extension_size, key_type) != (0x0E, 0x398, 2):
        raise Failure("stored oem.key extension-14 drift")
    if (extension_size - 0x24) % 0x44:
        raise Failure("stored oem.key entry geometry drift")
    records = []
    for index in range((extension_size - 0x24) // 0x44):
        offset = 0x2A8 + index * 0x44
        usage = [bit for bit in range(128) if manifest[offset + bit // 8] & (1 << (bit & 7))]
        flags = manifest[offset + 0x20]
        algorithm = manifest[offset + 0x21]
        digest_size = struct.unpack_from("<H", manifest, offset + 0x22)[0]
        digest = manifest[offset + 0x24 : offset + 0x44].hex()
        if len(usage) != 1 or flags != 0 or algorithm != 2 or digest_size != 0x20:
            raise Failure("stored oem.key record drift")
        records.append({"index": index, "usage_bits": usage, "digest": digest})
    selected = [record for record in records if record["usage_bits"] == [39]]
    if len(selected) != 1 or selected[0]["digest"] != STORED_USAGE39_DIGEST:
        raise Failure("stored oem.key usage-39 record drift")
    manifest_key_digest = hashlib.sha256(modulus + exponent_bytes).hexdigest()
    if manifest_key_digest != STORED_USAGE39_DIGEST:
        raise Failure("stored oem.key self-key digest drift")
    return {
        "cpd": "FTPR",
        "cpd_offset": cpd,
        "member": "oem.key",
        "member_cpd_offset": matches[0][1],
        "flash_offset": absolute,
        "size": len(manifest),
        "sha256": OEM_KEY_SHA256,
        "manifest": {
            "tag": "$MN2",
            "header_size": header_size,
            "total_size": manifest_size,
            "vendor_id": vendor_id,
            "public_key_size": public_key_size,
            "exponent": exponent,
            "embedded_signature": "RSA-2048 PKCS#1 v1.5 SHA-256",
            "embedded_signature_valid": signature_valid,
            "embedded_signature_boundary": "self-consistency only; no external root established",
        },
        "extension": {
            "tag": extension_tag,
            "size": extension_size,
            "key_type": key_type,
            "record_count": len(records),
            "usage39_record": selected[0],
            "manifest_public_key_digest": manifest_key_digest,
            "usage39_digest_equals_manifest_public_key_digest": selected[0]["digest"] == manifest_key_digest,
        },
    }


def analyze(update: Path, sbl_repo: Path, mea_repo: Path) -> dict:
    abl = archive_one(update)
    ibbl, stage1 = extract_ibb(abl)
    cse_rbe = extract_cse_rbe(abl)
    cse_ftpr_kernel, cse_ftpr_kernel_metadata, _cse_ftpr_manifest = extract_cse_ftpr_kernel(abl)
    cse_bup = extract_cse_bup(abl)
    cse_signed_module_chains = parse_cse_signed_module_chains(abl, cse_rbe, cse_bup)
    cse_root_and_boot_policy_chains = parse_cse_root_and_boot_policy_chains(abl)
    fpf_provisioning_handoff = extract_fpf_provisioning_handoff(abl, cse_bup)
    dal_sdm_snowball_policy = extract_dal_sdm_snowball_policy(abl)
    uep_oem_hash_candidate = parse_uep_oem_hash_candidate(abl)
    stored_oem_key = parse_stored_oem_key(abl)
    ibbl_ranges = check_ranges(ibbl, IBBL_RANGES, "IBBL")
    stage_ranges = check_ranges(stage1, STAGE1_RANGES, "stage-1")
    cse_rbe_ranges = check_ranges(cse_rbe, CSE_RBE_RANGES, "CSE RBE")
    cse_ftpr_kernel_ranges = check_ranges(cse_ftpr_kernel, CSE_FTPR_KERNEL_RANGES, "CSE FTPR kernel")
    cse_bup_ranges = check_ranges(cse_bup, CSE_BUP_RANGES, "CSE BUP")

    # Fixed exact instruction and string anchors within the hash-bound ranges.
    exact_sequences = (
        (
            ibbl,
            0x4F0,
            "ba0000f8fe89e5b8c0100c0057e8f1fbffffba02000000b8c0100c00",
            "IBBL FIT source/destination/copy sequence",
        ),
        (ibbl, 0xFE, "817a045f2020207519813a5f4649547511", "IBBL _FIT_ signature check"),
        (ibbl, 0x118, "8d42ff83f814760d", "IBBL FIT count bound"),
        (
            ibbl,
            0x149,
            "c6460e7f8d44031089068d42018b530825ffffff0081e2000000ff09d089430889d8",
            "IBBL appended FIT entry/count sequence",
        ),
        (
            stage1,
            0x157DD,
            "a1c8100c008b1d60100c0025ffffff00c685a6fdffff0089858cfdffffa164100c008985a8fdffff89c8c1e80383e107898590fdffffb801000000d3e0898588fdffffb9c0100c00c685a7fdffff00c78598fdffff000000008bbd8cfdffff39bd98fdffff0f8dd90000008a410e83e07f3c0b740bff8598fdffff83c110ebd9",
            "stage-1 FIT type-0x0b traversal",
        ),
    )
    for source, offset, encoded, label in exact_sequences:
        sequence = bytes.fromhex(encoded)
        if source[offset : offset + len(sequence)] != sequence:
            raise Failure(f"{label} drift")
    if stage1.find(b"%x@%x\0") != 0x1C85B or stage1.find(b"ABL.oemkm\0") != 0x1C861:
        raise Failure("ABL.oemkm command-line strings drift")
    if stage1[0xC1E4:0xC1E6] != b"\x6a\x27":
        raise Failure("type-3 OS selector drift")
    if cse_rbe.find(b"rot_key_man\0") != 0x7A6C or cse_rbe.find(b"oem.key\0") != 0x7A80:
        raise Failure("CSE RBE key-manifest source strings drift")
    if cse_rbe.find(b"oem_key_man\0") != 0x7A9A:
        raise Failure("CSE RBE key-manifest destination string drift")
    if cse_rbe.find(b"ifp_uep\0") != 0x7AE0:
        raise Failure("CSE RBE UEP object string drift")
    required_handoff_names = {
        b"bpdt\0": 0x7900,
        b"pm_trans\0": 0x7905,
        b"ftpm_fuses\0": 0x790E,
        b"sss_em\0": 0x7919,
        b"rbe.man\0": 0x7920,
        b"pmc_ipc\0": 0x7928,
        b"ipub_key\0": 0x7930,
    }
    if any(cse_rbe.find(name) != offset for name, offset in required_handoff_names.items()):
        raise Failure("CSE RBE required incoming handoff object strings drift")
    if cse_rbe.find(b"pmc_msg\0") != 0x7939:
        raise Failure("CSE RBE optional appended handoff object string drift")
    if cse_rbe.find(b"cld_rst_blk\0") != 0x78F4:
        raise Failure("CSE RBE first appended runtime-object name drift")
    handoff_base = struct.pack("<I", 0x08200000)
    abl_handoff_refs = [index for index in range(len(abl)) if abl.startswith(handoff_base, index)]
    if abl_handoff_refs != [0x106540, 0x106552, 0x1065BF, 0x1065D6, 0x106645, 0x11CF7D, 0x1204FA, 0x1216A6, 0x1216AE]:
        raise Failure("exact ABL runtime-object handoff base occurrences drift")
    if abl[0x11CF7C:0x11CF84] != bytes.fromhex("00000020081917ff"):
        raise Failure("PMCP cross-dword handoff-byte occurrence context drift")
    handoff_refs = [index for index in range(len(cse_rbe)) if cse_rbe.startswith(handoff_base, index)]
    if handoff_refs != [0x1540, 0x1552, 0x15BF, 0x15D6, 0x1645]:
        raise Failure("CSE RBE runtime-object handoff base references drift")
    if cse_rbe.find(struct.pack("<I", 0x08200008)) != 0x1557:
        raise Failure("CSE RBE runtime-object first-entry reference drift")
    if cse_rbe[0x7F74:0x7F78] != bytes.fromhex("60010001"):
        raise Failure("CSE RBE UEP OEM-hash field descriptor drift")
    if cse_ftpr_kernel[0x4F4:0x503] != bytes.fromhex("68008020086800002008e875feffff"):
        raise Failure("CSE FTPR kernel handoff range setup drift")
    if cse_ftpr_kernel[0x169F:0x16D7].count(struct.pack("<I", 0x08200008)) != 2:
        raise Failure("CSE FTPR kernel handoff iterator first-entry references drift")
    if cse_ftpr_kernel[0x16AC:0x16B3] != bytes.fromhex("833d0000200808"):
        raise Failure("CSE FTPR kernel handoff minimum-size check drift")
    if cse_rbe[0x3AF3:0x3B13] != bytes.fromhex(
        "8a45f26838800406c0e8046800010000a2588004066a2056e83b3c000083c410"
    ):
        raise Failure("CSE RBE UEP OEM-hash extraction sequence drift")
    if cse_rbe[0x2BAC:0x2BE2] != bytes.fromhex(
        "6a20566838800406e870e4fbff83c40c85c00f95c285db0f95c031f638c2754185db74596a006a06683880040653e889fbffff83c410"
    ):
        raise Failure("CSE RBE UEP-pinned oem.key validation sequence drift")
    rbe_route = bytes.fromhex(
        "6a0068807a04006a00e813f0ffff83c40c85c0751db9887a040031d2b8917a040068c87f0406e867feffff5985c07557eb1d31d2b99a7a0400b8807a0400682c100406e84afeffff"
    )
    if cse_rbe[0x2FCF : 0x2FCF + len(rbe_route)] != rbe_route:
        raise Failure("CSE RBE oem.key to oem_key_man route drift")
    if cse_bup.find(b"oem.key\0") != 0x2E235 or cse_bup.find(b"oem_key_man\0") != 0x2E249:
        raise Failure("CSE BUP key-manifest source strings drift")
    if cse_bup.rfind(b"BPM.met\0") != 0x2F9F3 or cse_bup.rfind(b"IBBP.man\0") != 0x2FA4E:
        raise Failure("CSE BUP Boot Policy member strings drift")
    ipub_offsets = [index for index in range(len(cse_bup)) if cse_bup.startswith(b"ipub_key\0", index)]
    if ipub_offsets != [0x2E284, 0x2E3D8] or cse_bup.find(b"/snowball/\0") != 0x2E370:
        raise Failure("CSE BUP ipub_key runtime/snowball strings drift")
    name_offsets = []
    name_pos = 0
    while True:
        name_pos = cse_bup.find(b"oem_key_man\0", name_pos)
        if name_pos < 0:
            break
        name_offsets.append(name_pos)
        name_pos += 1
    if name_offsets != [0x2E249, 0x2E3FC, 0x2F463, 0x2FA60]:
        raise Failure("CSE BUP key-manifest publication strings drift")
    publish_sequence = bytes.fromhex(
        "68605a0500e8e672ffff5985c07516800d824c0a0010c705544b0a0024000000e91c0500008b4018a3a44a0a0085c074de8b4018c1e0023d001000007616"
    )
    if cse_bup[0xB9BC : 0xB9BC + len(publish_sequence)] != publish_sequence:
        raise Failure("CSE BUP oem_key_man lookup sequence drift")
    add_sequence = bytes.fromhex(
        "6a006a0b6a008b4018c1e00250680010feff56e8fdd6ffff"
    )
    if cse_bup[0xBAD4 : 0xBAD4 + len(add_sequence)] != add_sequence:
        raise Failure("CSE BUP FIT type-0x0b append sequence drift")
    require_once(cse_bup, b"IBBL\0", "CSE BUP IBBL member name")
    require_once(cse_bup, b"IBB\0", "CSE BUP IBB member name")
    if struct.unpack_from("<III", ibbl, 0x2760) != (0xFEFFC000, 0x1000, 0xFFFFC000):
        raise Failure("IBBL static self-relocation descriptor drift")
    fit_pointer_sequence = bytes.fromhex("c786c0ff01000000feff")
    if cse_bup[0xBE27 : 0xBE27 + len(fit_pointer_sequence)] != fit_pointer_sequence:
        raise Failure("CSE BUP IBBL FIT-base pointer sequence drift")

    fit_source = git_blob(sbl_repo, SBL_COMMIT, SBL_FILE, SBL_FILE_SHA256)
    require_once(fit_source, b"#define FIT_TYPE_0B_KEY_MANIFEST            0x0B", "FIT type 0x0b")
    require_once(fit_source, b"#define FIT_TYPE_10_CSE_SECURE_BOOT         0x10", "FIT type 0x10")
    require_once(fit_source, b"#define FIT_TYPE_00_SIGNATURE  SIGNATURE_64 ('_', 'F', 'I', 'T', '_', ' ', ' ', ' ')", "FIT signature")
    require_once(fit_source, b"UINT8  Size[3];", "FIT 24-bit size")
    require_once(fit_source, b"UINT8  Type : 7;", "FIT 7-bit type")

    apl_loader_source = git_blob(sbl_repo, SBL_COMMIT, SBL_APL_LOADER_FILE, SBL_APL_LOADER_SHA256)
    for needle, label in (
        (b"#define  SRAM_SIZE              0x20000", "Apollo Lake CSE SRAM size"),
        (b"#define  SRAM_REMAPPING         (0xFFFFFFFF - SRAM_SIZE + 1)", "Apollo Lake CSE SRAM remapping"),
        (b"HostToCse    = (IbbSize << 4) | 0xC0000000;", "Apollo Lake host request encoding"),
        (b"ChunkNum   = (CseToHost >> 28) & 3;", "Apollo Lake chunk-count response field"),
        (b"IbbSizeLeft    = (CseToHost & 0x0FFFC000) >> 4;", "Apollo Lake IBB-size response field"),
        (b"ChunkSize      = SramSize / NumberOfChunks;", "Apollo Lake ring-slot size"),
        (b"RingIdx = (UINT8) (ChunkIndex % NumberOfChunks);", "Apollo Lake ring index"),
        (b"Src = (UINT8 *) (SramBase + ChunkSize * RingIdx);", "Apollo Lake CSE SRAM source"),
        (b"Dst = (UINT8 *) (IbbDst  + ChunkSize * ChunkIndex);", "Apollo Lake IBB destination"),
        (b"CopyMem (Dst, Src, Size);", "Apollo Lake CSE-to-IBB copy"),
    ):
        require_once(apl_loader_source, needle, label)
    if apl_loader_source.count(b"CSE_HOST2CSE = HostToCse;") != 2:
        raise Failure("Apollo Lake CSE request/ack sequence drift")
    if apl_loader_source.count(b"State = (CseToHost ^ HostToCse) & 0x0F;") != 2:
        raise Failure("Apollo Lake ring handshake state sequence drift")
    apl_board_source = git_blob(sbl_repo, SBL_COMMIT, SBL_APL_BOARD_FILE, SBL_APL_BOARD_SHA256)
    require_once(apl_board_source, b"self.STAGE1A_LOAD_BASE    = 0xFEF80000", "Apollo Lake Stage1A load base")
    require_once(apl_board_source, b"self.STAGE1B_FD_BASE      = 0xFEF88000", "Apollo Lake Stage1B flash-device base")

    mea_source = git_blob(mea_repo, MEA_COMMIT, MEA_FILE, MEA_FILE_SHA256)
    start = mea_source.find(b"class CSE_Ext_0E_Mod(ctypes.LittleEndianStructure)")
    end = mea_source.find(b"class CSE_Ext_0E_Mod_R2", start)
    if start < 0 or end < 0:
        raise Failure("ME Analyzer extension-14 structure bounds drift")
    ext14 = mea_source[start:end]
    for needle, label in (
        (b'("UsageBitmap",        uint8_t*16)', "extension-14 usage bitmap"),
        (b'("Flags",            uint8_t)', "extension-14 flags"),
        (b'("HashAlgorithm",    uint8_t)', "extension-14 hash algorithm"),
        (b'("HashSize",        uint16_t)', "extension-14 hash size"),
        (b'("Hash",            uint32_t*8)', "extension-14 SHA-256 hash"),
        (b"# 0x44", "extension-14 entry size"),
    ):
        require_once(ext14, needle, label)
    require_once(mea_source, b"39 : 'OS Kernel'", "usage 39 name")

    candidate = bytes.fromhex(CANDIDATE_OS_KEY_DIGEST)
    selector = 0x27
    return {
        "schema": SCHEMA,
        "tool": {"name": "abl-ias-key-provenance", "version": VERSION},
        "exact_update": {
            "archive": {"size": UPDATE_SIZE, "sha256": UPDATE_SHA256},
            "abl": {"member": ABL_MEMBER, "size": ABL_SIZE, "sha256": ABL_SHA256},
            "ibb_loader": {
                "size": len(ibbl),
                "sha256": IBBL_SHA256,
                "instruction_ranges": ibbl_ranges,
                "source_fit_address": 0xFEF80000,
                "relocated_fit_address": 0x000C10C0,
                "fit_signature": "_FIT_   ",
                "maximum_accepted_source_entries": 21,
                "appended_entry_type": 0x7F,
                "relocation_mode": 2,
                "relocation_skips_type": 1,
                "type_0b_payload_relocated_if_present": True,
                "early_memory_setup_and_self_relocation": {
                    "mtrr_base_addresses": [0xFEF80000, 0xFFFE0000],
                    "temporary_destination_clear_base": 0xFEF80000,
                    "temporary_destination_clear_dword_count": 0x20000,
                    "copy_descriptor_runtime_address": 0xFFFFE760,
                    "copy_descriptor_file_offset": 0x2760,
                    "copy_descriptor_dwords": {
                        "destination": 0xFEFFC000,
                        "count": 0x1000,
                        "source": 0xFFFFC000,
                    },
                    "copy_count_unit": "dwords",
                    "copy_size_bytes": 0x4000,
                    "source_equals_ibbl_runtime_base": True,
                    "copy_size_equals_exact_ibbl_size": True,
                    "purpose": "IBBL self-relocation from the top-of-SRAM execution address, not the BUP-FIT-to-0xfef80000 transfer",
                    "post_copy_read_base": 0xFEF80000,
                    "post_copy_read_dword_count": 0x4800,
                    "descriptor_directed_copy_path_proved": True,
                    "static_descriptor_values_recovered": True,
                },
                "initial_fit_materialization": {
                    "bup_pointer_storage_buffer_offset": 0x1FFC0,
                    "bup_pointer_value": 0xFFFE0000,
                    "pointer_offset_within_tail_placed_ibbl": 0x3FC0,
                    "pointer_address_after_ibbl_self_relocation": 0xFEFFFFC0,
                    "ibbl_reads_pointer_from": 0xFEFFFFC0,
                    "fit_copy_source": 0xFFFE0000,
                    "fit_copy_destination": 0xFEF80000,
                    "first_relocation_mode": 0,
                    "later_low_memory_fit_destination": 0x000C10C0,
                    "bup_to_ibbl_fit_mapping_proved": True,
                },
                "exact_cse_ibb_ring_consumer": {
                    "pci_config_address_port": 0xCF8,
                    "pci_config_data_port": 0xCFC,
                    "host_to_cse_config_address": 0x80007870,
                    "cse_to_host_config_address": 0x80007860,
                    "request_capacity": 0x38000,
                    "destination_base": 0xFEFBD900,
                    "destination_limit": 0xFEFF5900,
                    "sram_alias_base": 0xFFFE0000,
                    "ring_buffer_size": 0x20000,
                    "chunk_count_and_size_response_decoded": True,
                    "low_four_bit_xor_handshake_used": True,
                    "slot_acknowledgements_written": True,
                    "exact_target_host_code_and_destination_proved": True,
                },
            },
            "decompressed_stage1": {
                "size": len(stage1),
                "sha256": STAGE1_SHA256,
                "load_base": 0x000E0000,
                "instruction_ranges": stage_ranges,
                "fit_table": {
                    "base": 0x000C10C0,
                    "header_size_count_address": 0x000C10C8,
                    "entry_size": 0x10,
                    "type_offset": 0x0E,
                    "type_mask": 0x7F,
                    "selected_type": 0x0B,
                },
                "key_manifest": {
                    "pointer_from_fit_entry_offset": 0,
                    "extension_offset": 0x284,
                    "extension_size_offset": 0x288,
                    "entry_array_offset": 0x2A8,
                    "entry_size": 0x44,
                    "digest_offset": 0x24,
                    "digest_size": 0x20,
                    "cached_extension_pointer_address": 0x000C1060,
                    "cached_extension_size_address": 0x000C1064,
                    "kernel_command_line_name": "ABL.oemkm",
                    "kernel_command_line_format": "%x@%x",
                },
                "type3_os_selector": {
                    "value": selector,
                    "usage_bit_index": selector,
                    "usage_byte_index": selector >> 3,
                    "usage_byte_mask": 1 << (selector & 7),
                    "public_me_analyzer_name": "OS Kernel",
                },
            },
            "cse_signed_module_chains": cse_signed_module_chains,
            "cse_root_and_boot_policy_chains": cse_root_and_boot_policy_chains,
            "cse_uep_to_fpf_provisioning_handoff": fpf_provisioning_handoff,
            "nftp_dal_sdm_snowball_policy": dal_sdm_snowball_policy,
            "cse_rbe_uep_oem_key_authentication": {
                "uep_object_name": "ifp_uep",
                "object_size": UEP_SIZE,
                "mode_source": "(dword[0xf6170810] >> 24) & 0x0f",
                "hardware_window_selection_expression": "(mode_nibble & 0x0c) != 0 and (mode_nibble & 0x03) != 0",
                "hardware_window_mode_nibbles": [value for value in range(16) if uep_hardware_window_selected(value)],
                "hardware_window": "0xf6170800..0xf61708ff when the exact mode expression is true",
                "flash_route": "BPDT type-17 UEP primary, then descriptor +0x1000 fallback, each checked for $UEP magic and CRC-16",
                "field_index": 0x20,
                "field_bit_length": 0x100,
                "field_table_bit_offset": 0x160,
                "field_input_base": "UEP + 8",
                "field_output_global": 0x6048038,
                "field_output_matches_exact_oem_key_digest": True,
                "oem_key_validation": "requires oem.key presence to agree with nonzero UEP hash, hashes the manifest's 0x100-byte modulus plus four-byte exponent, compares that digest with the UEP field, and only then performs embedded RSA verification and extension validation",
                "mn2_validator_flags": 6,
                "mn2_validator_key_index": 0,
                "extension_validation_selector": 6,
                "external_uep_authentication_or_fuse_precedence_proved": False,
            },
            "cse_rbe_key_manifest_materializer": {
                "cpd": "RBEP",
                "member": "rbe",
                "flash_offset": 0x105000,
                "size": len(cse_rbe),
                "sha256": CSE_RBE_SHA256,
                "code_base": CSE_RBE_CODE_BASE,
                "main_thread_entry": 0x407A3,
                "instruction_ranges": cse_rbe_ranges,
                "source_partition_index": 0,
                "source_cpd_member": "oem.key",
                "destination_object_name": "oem_key_man",
                "source_member_flash_offset": stored_oem_key["flash_offset"],
                "source_member_size": stored_oem_key["size"],
                "copy_semantics": "creates the destination object at the source CPD length, transfers that exact length from the source CPD entry, then requires destination manifest dword count at +0x18 times four to equal the source length",
                "transformation_before_publication_observed": False,
                "source_to_destination_exact_length_copy_proved": True,
            },
            "cse_ftpr_kernel_handoff_consumer": {
                "cpd": "FTPR",
                "member": "kernel",
                "flash_offset": 0x120000,
                "size": len(cse_ftpr_kernel),
                "sha256": CSE_FTPR_KERNEL_SHA256,
                "metadata_member": "kernel.met",
                "metadata_flash_offset": 0x11ED44,
                "metadata_size": len(cse_ftpr_kernel_metadata),
                "metadata_sha256": CSE_FTPR_KERNEL_METADATA_SHA256,
                "code_base": CSE_FTPR_KERNEL_CODE_BASE,
                "main_thread_entry": CSE_FTPR_KERNEL_CODE_BASE,
                "instruction_ranges": cse_ftpr_kernel_ranges,
                "ftpr_manifest_binds_kernel_metadata_reverse_sha256": True,
                "kernel_metadata_binds_kernel_reverse_sha256": True,
                "handoff_range_start": 0x08200000,
                "handoff_range_end": 0x08208000,
                "handoff_base_global": 0x99DEC,
                "handoff_entry_global": 0x99DF4,
                "handoff_payload_cursor_global": 0x99DF0,
                "minimum_nonempty_total_size": 8,
                "first_entry": 0x08200008,
                "entry_total_size_offset": 0x0E,
                "entry_state_offset": 0x0D,
                "entry_state_mask": 0x03,
                "accepted_entry_state": 1,
                "same_handoff_geometry_as_rbe_proved": True,
                "handoff_survives_into_ftpr_kernel_proved": True,
                "bup_runtime_object_ingestion_geometry": {
                    "list_head_global": 0xA014C,
                    "list_initialized_empty": True,
                    "reader_called_until_null": True,
                    "header_read_size": 0x12,
                    "header_returned_size_must_equal": 0x12,
                    "entry_total_size_offset": 0x0E,
                    "payload_length_expression": "zero_extend_u16(entry_total_size) - 0x12 modulo 2^32",
                    "entry_total_size_width_bits": 16,
                    "minimum_total_size_check_before_subtract": False,
                    "payload_length_underflows_when_total_size_below_0x12": True,
                    "explicit_maximum_total_size_check_observed": False,
                    "ftpr_reader_clamps_each_segment_to_current_entry": True,
                    "ftpr_reader_advances_and_concatenates_next_accepted_entry": True,
                    "ftpr_reader_preserves_caller_read_boundary_as_entry_boundary": False,
                    "state_one_total_0x10_or_0x11_can_be_completed_to_0x12_header_from_next_entry": True,
                    "synthetic_header_retains_underflow_total_for_0x10_or_0x11": True,
                    "underflow_payload_lengths_for_0x10_and_0x11": [0xFFFFFFFE, 0xFFFFFFFF],
                    "kernel_process_buffer_maximum": 0x01800000,
                    "kernel_rejects_underflowed_payload_length_before_stream_copy": True,
                    "kernel_rejection_depends_on_bup_reader_using_exact_standard_syscall_path": True,
                    "malformed_stream_can_reach_bup_header_parser_if_reader_binding_holds": True,
                    "malformed_stream_attacker_control_proved": False,
                    "memory_corruption_from_total_underflow_proved": False,
                    "payload_read_must_be_exact": True,
                    "materialized_payload_size_offset": 0x14,
                    "materialized_payload_pointer_offset": 0x18,
                    "materialized_next_pointer_offset": 0x1C,
                    "phase_zero_order": {
                        "main_phase_zero_call_runtime": 0x3AC81,
                        "dispatcher_runtime": 0x28932,
                        "phase_zero_function_count": 0x16,
                        "phase_zero_function_table_runtime": 0x54744,
                        "ingestion_function_runtime": 0x2891A,
                        "ingestion_function_index": 7,
                        "ifp_uep_consumer_runtime": 0x32A1B,
                        "ifp_uep_consumer_index": 10,
                        "runtime_object_cleanup_runtime": 0x3AC94,
                        "main_calls_cleanup_after_phase_zero": True,
                        "ingestion_precedes_ifp_uep_consumer": True,
                        "ifp_uep_consumer_precedes_cleanup": True,
                    },
                    "ftpr_stream_to_bup_object_geometry_matches": True,
                    "external_reader_api_bound_to_exact_ftpr_kernel_function": False,
                    "bup_ipub_key_source_proved_to_be_rbe_handoff": False,
                    "snowball_fallback_excluded_during_manifest_verification": False,
                },
                "pre_rbe_producer_or_hardware_anchor_proved": False,
                "boundary": "the signed FTPR kernel consumes the same 0x08200000 runtime-object geometry after RBE; this continuity does not identify or authenticate the pre-RBE producer",
            },
            "cse_bup_fit_producer": {
                "cpd": "FTPR",
                "member": "bup",
                "flash_offset": 0x145000,
                "size": len(cse_bup),
                "sha256": CSE_BUP_SHA256,
                "code_base": CSE_BUP_CODE_BASE,
                "instruction_ranges": cse_bup_ranges,
                "fit_header_initialized": True,
                "source_object_name": "oem_key_man",
                "persistent_member_name_coupled_by_resolver": "oem.key",
                "payload_copy_destination_offset": 0x1000,
                "published_fit_address": 0xFFFE1000,
                "published_fit_type": 0x0B,
                "published_length_source": "oem_key_man object dword count at +0x18, multiplied by four",
                "ibbl_tail_placement": {
                    "resolved_member_name": "IBBL",
                    "companion_member_name": "IBB",
                    "maximum_accepted_ibbl_size": 0x9000,
                    "fit_buffer_size": 0x20000,
                    "placement_expression": "fit_buffer + 0x20000 - resolved IBBL size",
                    "exact_ibbl_size": 0x4000,
                    "exact_buffer_offset": 0x1C000,
                    "sram_alias_base": 0xFFFE0000,
                    "exact_runtime_address": 0xFFFFC000,
                    "matches_self_relocation_descriptor_source": True,
                },
                "fit_base_pointer_for_ibbl": {
                    "buffer_offset": 0x1FFC0,
                    "value": 0xFFFE0000,
                    "lies_at_ibbl_offset": 0x3FC0,
                    "copied_to_temporary_address": 0xFEFFFFC0,
                },
                "ibb_ring_streamer": {
                    "source_member_name": "IBB",
                    "source_offset_from_resolved_member_descriptor": True,
                    "source_size_from_resolved_member_descriptor": True,
                    "ring_buffer_base_global": 0xA4AA0,
                    "ring_buffer_size": 0x20000,
                    "slot_count": 4,
                    "slot_size": 0x8000,
                    "slot_expression": "fit_buffer + (ring_index & 3) * 0x8000",
                    "maximum_chunk_size": 0x8000,
                    "source_position_advanced_by_chunk": True,
                    "ring_index_advanced_until_full_source_size": True,
                    "cse_response_encoding": "0x30000000 | (((IBB_size >> 10) & 0x3fff) << 14)",
                    "encoded_chunk_count_value": 3,
                    "encoded_chunk_count_means_slots": 4,
                    "encoded_size_field_mask": 0x0FFFC000,
                    "handshake_uses_low_four_xor_state_bits": True,
                    "host_destination_address": 0xFEFBD900,
                    "host_destination_address_proved": True,
                    "fit_table_transfer_by_this_chunk_loop_proved": False,
                },
                "final_handoff_address_0xfef80000_mapping_proved": True,
                "oem_key_man_byte_identity_with_ftpr_oem_key_proved": True,
            },
            "uep_oem_hash_candidate": uep_oem_hash_candidate,
            "stored_oem_key_manifest": stored_oem_key,
            "package_carried_os_key_candidate_digest": {
                "sha256": CANDIDATE_OS_KEY_DIGEST,
                "present_verbatim_in_update_abl": candidate in abl,
                "present_verbatim_in_ibbl": candidate in ibbl,
                "present_verbatim_in_stage1": candidate in stage1,
                "matches_stored_oem_key_usage39_digest": CANDIDATE_OS_KEY_DIGEST == STORED_USAGE39_DIGEST,
            },
        },
        "public_structure_corroboration": {
            "slim_bootloader": {
                "commit": SBL_COMMIT,
                "file": SBL_FILE,
                "file_sha256": SBL_FILE_SHA256,
                "type_0b_name": "FIT_TYPE_0B_KEY_MANIFEST",
                "type_10_name": "FIT_TYPE_10_CSE_SECURE_BOOT",
                "apl_cse_sram_handoff": {
                    "loader_file": SBL_APL_LOADER_FILE,
                    "loader_file_sha256": SBL_APL_LOADER_SHA256,
                    "board_file": SBL_APL_BOARD_FILE,
                    "board_file_sha256": SBL_APL_BOARD_SHA256,
                    "sram_size": 0x20000,
                    "sram_remapping_base": 0xFFFE0000,
                    "stage1a_load_base": 0xFEF80000,
                    "stage1b_fd_base": 0xFEF88000,
                    "host_request_encoding": "(IbbSize << 4) | 0xc0000000",
                    "cse_response_chunk_count_field": "(CseToHost >> 28) & 3; value 3 means four chunks",
                    "cse_response_size_field": "(CseToHost & 0x0fffc000) >> 4",
                    "ring_handshake_state": "(CseToHost ^ HostToCse) & 0x0f",
                    "semantics": "host requests IBB data from CSE, copies ring-buffer chunks from the 0xfffe0000 SRAM remapping into IbbDst, and acknowledges each chunk",
                    "bitfield_and_ring_geometry_match_exact_bup": True,
                    "exact_target_host_code_or_destination_proved": False,
                },
            },
            "me_analyzer": {
                "commit": MEA_COMMIT,
                "file": MEA_FILE,
                "file_sha256": MEA_FILE_SHA256,
                "structure": "CSE Extension 14 R1 key-manifest entry",
                "entry_size": 0x44,
                "usage_bitmap_size": 0x10,
                "digest_offset": 0x24,
                "digest_size": 0x20,
                "usage_39_name": "OS Kernel",
            },
            "boundary": "Names and pre-IBBL authentication semantics are public-source corroboration; exact target instructions independently prove the layout, selector, copy, and compare path.",
        },
        "conclusions": {
            "runtime_descriptor_is_fit_entry_type_0b_proved": True,
            "type_0b_symbolic_name_key_manifest_publicly_corroborated": True,
            "pre_ibbl_fit_handoff_address_proved": True,
            "ibbl_copies_fit_and_relocates_type_0b_payload_proved": True,
            "runtime_key_manifest_layout_proved": True,
            "selector_0x27_is_usage_bit_39_proved": True,
            "usage_bit_39_os_kernel_name_publicly_corroborated": True,
            "oem_key_manifest_kernel_command_line_export_proved": True,
            "cse_rbe_copies_ftpr_oem_key_to_oem_key_man_proved": True,
            "cse_bup_constructs_fit_type0b_from_oem_key_man_proved": True,
            "cse_bup_resolver_couples_oem_key_and_oem_key_man_names_proved": True,
            "uep_contains_stored_oem_key_digest_candidate_proved": True,
            "uep_exact_target_consumption_proved": True,
            "uep_hardware_vs_bpdt_selection_expression_proved": True,
            "uep_digest_pins_oem_key_before_rsa_proved": True,
            "uep_external_hardware_anchor_proved": False,
            "stored_oem_key_manifest_bytes_recovered": True,
            "stored_usage39_digest_recovered": True,
            "stored_oem_key_manifest_embedded_signature_valid": True,
            "package_candidate_matches_stored_usage39_digest": False,
            "runtime_fit_type0b_object_name_oem_key_man_proved": True,
            "bup_published_type0b_bound_to_stored_oem_key_manifest": True,
            "bup_published_expected_usage39_digest_recovered": True,
            "runtime_fit_type0b_bound_to_stored_oem_key_manifest": True,
            "runtime_expected_digest_bytes_recovered": True,
            "runtime_expected_usage39_digest": STORED_USAGE39_DIGEST,
            "source_fit_content_producer_cse_bup_proved": True,
            "bup_places_exact_ibbl_at_0xffffc000_proved": True,
            "bup_streams_resolved_ibb_through_four_slot_sram_ring_proved": True,
            "public_apl_host_protocol_matches_exact_bup_bitfields_and_ring_geometry": True,
            "exact_ibbl_host_ring_consumer_and_destination_proved": True,
            "bup_fit_base_pointer_to_ibbl_source_mapping_proved": True,
            "ibbl_static_self_relocation_descriptor_recovered": True,
            "ibbl_self_relocation_descriptor_is_not_fit_transfer_proved": True,
            "apl_public_cse_sram_to_fef80000_handoff_corroborated": True,
            "final_handoff_address_0xfef80000_mapping_proved": True,
            "rbe_and_bup_signed_module_byte_chains_proved": True,
            "rbe_runtime_ipub_key_pins_rot_key_proved": True,
            "rbe_ipub_key_consumed_from_incoming_0x08200000_handoff_proved": True,
            "same_handoff_consumed_by_signed_ftpr_kernel_proved": True,
            "ftpr_stream_and_bup_runtime_object_ingestion_geometry_match_proved": True,
            "bup_phase_zero_ingestion_before_ifp_uep_consumption_and_cleanup_proved": True,
            "bup_runtime_object_total_size_underflow_guard_absent_proved": True,
            "ftpr_total_0x10_or_0x11_survives_stream_as_synthetic_bup_header_if_reader_binding_holds": True,
            "ftpr_kernel_rejects_underflowed_bup_payload_read_on_standard_path": True,
            "bup_malformed_runtime_object_stream_attacker_control_proved": False,
            "bup_total_underflow_memory_corruption_proved": False,
            "ftpr_stream_reader_to_bup_import_binding_proved": False,
            "bup_runtime_ipub_key_proved_to_originate_in_rbe_handoff": False,
            "signed_nftp_dal_sdm_reads_exact_snowball_ipub_key_policy_object_proved": True,
            "snowball_ipub_key_producer_or_writability_proved": False,
            "pre_rbe_handoff_producer_or_authenticator_proved": False,
            "shared_rot_key_digest_for_rbep_ftpr_nftp_manifests_proved": True,
            "bup_ipub_key_runtime_object_or_snowball_resolution_proved": True,
            "bup_ipub_selector_and_pointer_field_bounds_checks_absent_proved": True,
            "bup_malformed_ipub_object_attacker_control_or_reachability_proved": False,
            "bup_snowball_ipub_key_selected_at_runtime_proved": False,
            "bup_snowball_ipub_key_writable_or_untrusted_proved": False,
            "ipub_key_external_hardware_anchor_proved": False,
            "oem_key_usage32_pins_ibbp_manifest_proved": True,
            "ibbp_manifest_binds_bpm_metadata_proved": True,
            "bpm_metadata_binds_exact_ibbl_and_ibb_proved": True,
            "uep_to_oem_key_to_ibbp_to_exact_ibb_chain_proved": True,
            "selected_uep_to_bup_fpf_to_signed_nftp_fpf_shadow_proved": True,
            "bup_ifp_uep_null_and_size_checks_absent_proved": True,
            "bup_malformed_or_duplicate_ifp_uep_reachability_proved": False,
            "nftp_fpf_hardware_state_equated_to_rbe_hardware_window": False,
            "ftpr_manifest_direct_oem_key_coverage_proved": False,
            "pre_ibbl_key_manifest_authentication_proved": True,
            "custom_signed_image_acceptance_proved": False,
            "boot_root_or_persistence_proved": False,
        },
        "limitations": [
            "Exact CSE RBE code selects FTPR CPD member oem.key, creates object oem_key_man at the exact source length, transfers that exact length without a visible transformation, and requires the destination manifest dword count to match the source length.",
            "Exact CSE BUP code initializes a 0x20000-byte FIT-bearing buffer, copies oem_key_man into payload offset 0x1000, and appends type 0x0b with address 0xfffe1000. Exact IBBL later consumes a FIT at 0xfef80000.",
            "Exact BUP resolves IBBL, bounds its size, and places it at the end of the 0x20000-byte buffer. The exact 0x4000-byte IBBL therefore begins at buffer offset 0x1c000, or SRAM alias 0xffffc000.",
            "The descriptor at runtime 0xffffe760 is statically embedded at IBBL file offset 0x2760 and contains destination 0xfeffc000, count 0x1000 dwords, source 0xffffc000. It relocates the exact 0x4000-byte IBBL itself; the FIT follows the separate proved pointer path through 0xfeffffc0.",
            "Exact BUP separately streams the resolved IBB member through four 0x8000-byte slots spanning the same 0x20000-byte SRAM buffer. Exact IBBL implements the matching PCI-config host consumer and copies the stream to 0xfefbd900 with a 0x38000-byte capacity.",
            "BUP writes 0xfffe0000 at buffer offset 0x1ffc0, which is IBBL offset 0x3fc0 after tail placement. IBBL self-relocation carries that pointer to 0xfeffffc0; exact host code reads it and copies/relocates the FIT from 0xfffe0000 to 0xfef80000 before the later low-memory copy. This closes the BUP-to-IBBL FIT mapping.",
            "Hash-bound historical Apollo Lake Slim Bootloader source independently matches the exact target's chunk-count field, four-slot interpretation, size field, low-four-bit XOR handshake, slot geometry, source expression, acknowledgement, and PCI configuration offsets.",
            "Exact stage-1 code consumes FIT type 0x0b as the key-manifest source. Public Intel structure names and ME Analyzer's usage-39 label corroborate the nomenclature but do not independently prove target provisioning policy.",
            "The RBE-to-BUP-to-IBBL path binds the runtime type-0x0b payload to exact FTPR oem.key bytes. The recovered set's runtime expected usage-39 digest is therefore 9b0a59c842ba70857b595ed8115630d3a342a10c9d4437f9ff4807517693e0af.",
            "Exact RBE looks up ipub_key in an incoming bounded runtime-object handoff at 0x08200000, copies a selected 32-byte digest to 0x6047fa8, and requires rot.key's modulus-plus-exponent digest to match it before RSA verification. RBE can append other handoff objects but its ipub_key path does not create that entry. The FTPR manifest and kernel metadata bind the exact signed FTPR kernel, which later consumes the same handoff base, first-entry address, state byte, and +0x0e entry-size geometry. Exact BUP's corresponding manifest path resolves ipub_key either from a runtime object or from /snowball/ipub_key depending on global 0xa014c. It requires the returned object size to be greater than 0x23, then uses byte 0 as an unchecked selector for the pointer at offset 4 + 4*selector and supplies 32 bytes from that pointer to its verifier. No selector upper bound or selected-pointer-within-object check is observed in this path. Reachable attacker control of either object source is not proved. The exact Intel digest occurs statically only in rot.key's Extension-14 record. These paths do not prove who populated or authenticated the pre-RBE handoff, that it is immutable, or that the snowball branch is active, writable, or unauthenticated.",
            "Exact BUP selects oem.key usage bit 32, compares the IBBP.man modulus-plus-exponent digest before RSA verification, verifies IBBP.man, checks its signed BPM.met hash, and checks BPM.met's exact IBBL and IBB SHA-256 values. This closes the selected-UEP-to-exact-IBB byte chain for the recovered set.",
            "Exact RBE materializes the selected 0x100-byte UEP payload in the 0x108-byte ifp_uep object, with a hardware-route REAL header or the validated flash-route $UEP/CRC header. Exact BUP records whether the header is REAL without rejecting the alternative in this range, initially copies the payload byte-for-byte into its FPF shadow, may update that shadow through later field assembly, and publishes the resulting 0x880-byte bup_fpf special file. The signed NFTP fpf module requires that exact-size input and uses the resulting shadow while its hardware-mode global is zero.",
            "The signed NFTP fpf module exposes fpf and fpf_hw_use special files, opens /dev/flash/uep, and switches its field-read path between the BUP-provided shadow and hardware access. Its OemLock callback sets hardware mode before processing a fixed field sequence. This later provisioning state is not yet proved byte-identical to RBE's earlier 0xf6170800 hardware window.",
            "RBEP.man, FTPR.man, NFTP.man, rot.key, and IBBP.man embedded signatures verify. The first four are externally anchored only if the runtime ipub_key object is anchored; the OEM/IBBP chain is externally anchored only if the selected UEP digest is anchored.",
            "Exact FTPR.man has no direct oem.key name or digest coverage and FTPR CPD has no oem.key.met member. This bounded absence is not proof that another CSE policy, key manifest, or hardware root leaves oem.key unauthenticated.",
            "Exact RBE creates ifp_uep, obtains a CRC-checked UEP from an exact hardware-window branch or BPDT primary/fallback route, extracts field 0x20 (256 bits) to global 0x6048038, and uses that digest to pin oem.key's modulus-plus-exponent hash before RSA and extension validation.",
            "The OEM key-manifest authentication path is therefore proved before BUP publication. What remains unproved is whether the selected UEP bytes are externally authenticated, fuse-backed, overrideable, or merely CRC-protected flash data on a given installed platform.",
            "The exact flash contains an FTPR oem.key $MN2/Extension-14 manifest with a valid embedded self-signature and usage-39 digest 9b0a59...; the embedded signature still proves self-consistency rather than an external hardware root.",
            "The recovered runtime usage-39 digest does not equal the package carried-key candidate 437008... . This is an exact artifact-set mismatch, but owner-unit boot acceptance still depends on installed ABL/RBE/BUP/UEP identity and update-component selection.",
            "The recovered IBB stages do not locally authenticate the key manifest before use. Any CSE, Boot Guard, fuse, ACM, or earlier-ROM authentication remains outside the recovered instruction boundary; the embedded manifest signature proves self-consistency only.",
            "The exact package carried-key candidate digest remains absent verbatim from the update ABL, IBBL, and decompressed stage 1; no installed-platform handoff or identity was captured.",
            "No updater, bootloader, target helper, firmware image, flash operation, partition write, selector change, or boot attempt was executed or generated.",
        ],
    }


def encode(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False, separators=(",", ": "))
        + "\n"
    ).encode("utf-8")


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
    parser.add_argument("--sbl-repo", type=Path, required=True)
    parser.add_argument("--mea-repo", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args(argv)
    try:
        data = encode(analyze(args.update_archive, args.sbl_repo, args.mea_repo))
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
