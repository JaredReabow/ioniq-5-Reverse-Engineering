#!/usr/bin/env python3
"""Verify AppFUMO boot-partition write and result-propagation boundaries."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import struct
import sys
from pathlib import Path

TOOL = "appfumo-boot-partition-write"
VERSION = "1.0.0"
SCHEMA = "appfumo-boot-partition-write/v1"
MAX_SIZE = 16 * 1024 * 1024
EXPECTED_SIZE = 5_066_264
EXPECTED_SHA256 = "464a87646153213ce1f405743a10cff78eb90c203b619f983002358ca74ef0e7"
EXPECTED_BUILD_ID = "863a8730e66a1c5245a1bf458fe2554adee0351a"

RANGES = {
    "swap_system": (0x148E70, 0x14BBA6, "741fbf2e3fe1321cdc8a2274c4f194ea26c0a90801ca2a6994e4292ef40f8a60"),
    "mount_command_dispatch": (0x13C1A0, 0x13C400, "a3042e9295c7ef5a2f8a0d43789f5f9a52333115b22db05484155b97e7789a7f"),
    "process_list_dispatch": (0x13BFD0, 0x13C195, "9d3153c135fe546cf739316ff904c7c9f6153d366f02548d6c6bc7b5ec7611c5"),
    "process_wait": (0x13BBA0, 0x13BFC6, "e704df8654359cd570e2f231da68da8aa66414199125b1234342588566b8e9e0"),
    "pipeline_runner": (0x1397C0, 0x1398FB, "2ecd2e51775da1ff3f6ea1f9082a1e1b44aeba526bbd4713aaff798e38a3bd26"),
    "progress_caller": (0x11F1B0, 0x120A9E, "8d8cbd6f13b03f5e744a9419937d37db6390cef7c6022c7e8a4d52ee6fe3b959"),
    "secondary_caller": (0x122550, 0x12340F, "79b656d58a6f3ea734b8965e228dfc55f87bc0d8b75ac4d81b3f6a70df9048be"),
    "diagnostic_wrapper": (0x14BBB0, 0x14BD83, "230fb4615eeeb7eda4ba1f90d89af7467c0e3e9d983a8f7b587e18a44523368d"),
}

LITERALS = {
    "mountpoint": (0x22DAD5, "/mnt/bootcopy"),
    "mount_p1_prefix": (0x22DAE3, "mount -t ext2 /dev/mmcblk0p1 "),
    "mount_p2_prefix": (0x22DB01, "mount -t ext2 /dev/mmcblk0p2 "),
    "normal_destination_suffix": (0x22DB32, "/iasImage"),
    "sub_destination_suffix": (0x22DB3C, "/iasImage_sub"),
    "decrypt_pipeline_template": (0x22DB4A, "%1 -d %2 %3 0 | "),
    "dd_sink_template": (0x2122A8, "dd of=%1 bs=512"),
    "decrypt_program": (0x20B4D8, "/app/share/AppUpgrade/DecryptToPIPE"),
    "stderr_redirect": (0x20B81C, " 2>&1"),
    "popen_read_mode": (0x211C8B, "r"),
    "staging_root": (0x2130F6, "/tmp/update/usb"),
    "staging_suffix": (0x216E92, "/bootImage"),
    "iaspreload_suffix": (0x22DB96, "/iasPreload"),
    "umount_error_log": (0x22DBA2, "[%s] : umount error %d "),
    "domain": (0x22DC38, "swapSystem"),
}

DIRECT_CALLS = {
    "select_boot_filename": (0x148FA2, 0xA2480),
    "create_temporary_key_path": (0x149450, 0x44010),
    "retrieve_key_file": (0x1494C4, 0x47AE0),
    "sync_tail": (0x149580, 0x23420),
    "dispatch_mount_command": (0x149C3C, 0x13C1A0),
    "run_normal_pipeline": (0x149CD9, 0x1397C0),
    "remove_temporary_key": (0x149EEA, 0x237C0),
    "unmount_mountpoint": (0x14A00F, 0x245E0),
    "copy_normal_direct": (0x14A1BE, 0x1413F0),
    "copy_sub_direct": (0x14A404, 0x1413F0),
    "run_sub_pipeline": (0x14B59C, 0x1397C0),
    "dispatch_to_process_list": (0x13C2CD, 0x13BFD0),
    "wait_process_list": (0x13C0D8, 0x13BBA0),
    "wait_for_finished": (0x13BE15, 0x22E90),
    "pipeline_popen": (0x139867, 0x23800),
    "pipeline_fgets": (0x1398A3, 0x23130),
    "pipeline_pclose": (0x1398B0, 0x21FE0),
    "progress_call_swap": (0x12003F, 0x148E70),
    "secondary_call_swap": (0x1225C8, 0x148E70),
    "diagnostic_call_swap": (0x14BBFA, 0x148E70),
}

ANCHORS = {
    "mode_branch": (0x149476, "803d378c5800000f84bd060000"),
    "key_failure_counter_and_two_iteration_loop": (0x14954C, "488bbc24b001000083442444018b0785c00f85650b0000ba08000000be02000000e86ea9edff4983c5014983fd020f859ffeffffe89b9eedff"),
    "common_return_formula": (0x149585, "837c244401488bbc24a0010000400f9fc540222d178b58008b0783f501"),
    "normal_direct_copy_result_branch": (0x14A1A2, "488b3d57bd58004885ff0f84260e0000488b54243831c9488b742458e82d72ffff488bbc240003000089c38b1785d20f843105000083faff740ff0832f010f95c084c00f8411050000488b8424c000000084db0f842c050000"),
    "p2_sub_gate_and_direct_copy": (0x14A3AE, "4983fd010f853ffbffff488b742418488d8424400300004c8da424300100004889c74889442448488dac24900100004c89e2488d9c2480010000e8e3bef1ffe86ec0f1ff488b6c244831c94889c7488b7424704889eae8e76fffff89c34889efe84d15f0ff84db"),
    "mount_dispatch_then_mode_test": (0x149C29, "488b3dd0c258004885ff0f84771200004c89f6e85f25ffff488bbc24500400008b0785c00f85ad080000ba08000000be02000000e87ea2edff488d8424e0000000bf1027000048890424488dac2490010000488d9c24800100004c8da42430010000e840a5edff"),
    "pipeline_runner_call": (0x149C90, "803d1d845800000f84cb040000488b3d5cc258004885ff0f84bb130000488d8424e0000000488db424a001000048890424488dac2490010000488d9c24800100004c8da42430010000e8e2fafeff"),
    "unmount_result_log_only": (0x149FE2, "488b7c24504801c6e88184edff488b8424e00300008b5004488b781085d2740a4883ff170f86241100004801c7e8cca5edff488bbc24e003000089c38b0785c00f8578090000ba08000000be01000000e8a99eedff488bbc24400400008b0785c00f852f090000ba08000000be02000000e8889eedff85db7427488b3d85bd58004885ff0f84440f0000488d15c53b0e0089d931c0488d35243b0e00e8add3feffbf10270000e843a1edff"),
    "pipeline_drain_and_ignored_pclose_status": (0x139853, "488b7c2420e863c2f1ff488d3527840d004889c7e8949feeff4c89e74889c3e86920f1ff4889efe8e120f1ff4889e7e8d920f1ff4885db0f845affffff488d6c24300f1f004889dabe000200004889efe88898eeff4885c075eb4889dfe82b87eeff"),
    "wait_for_finished_log_path": (0x13BE15, "e87670eeff84c00f85bd000000488d6c247089de4c89efe85fa7f2ff4889ef48"),
    "progress_latch": (0x120020, "4c89f7e838b9f2ff4c89efe830b9f2ffe916f5ffff0f1f00488bbb38020000e82c8e020084c00f84e5f5ffffc6834002000001bd010000"),
    "secondary_latch": (0x1225A9, "0000488b7b40e84cc8f6ff84c0742880bb4002000000751f488bbb38020000e8a368020084c0740fc68340020000010f1f840000000000"),
}

class Failure(Exception):
    pass

def u16(b: bytes, o: int) -> int: return struct.unpack_from("<H", b, o)[0]
def u32(b: bytes, o: int) -> int: return struct.unpack_from("<I", b, o)[0]
def u64(b: bytes, o: int) -> int: return struct.unpack_from("<Q", b, o)[0]

def stable_read(path: Path) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try: fd = os.open(path, flags)
    except OSError as exc: raise Failure(f"cannot open input safely: {exc}") from exc
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_SIZE:
            raise Failure("input is not a bounded regular file")
        chunks, remaining = [], before.st_size
        while remaining:
            chunk = os.read(fd, min(remaining, 1 << 20))
            if not chunk: raise Failure("short input read")
            chunks.append(chunk); remaining -= len(chunk)
        if os.read(fd, 1): raise Failure("input grew while being read")
        after = os.fstat(fd)
        identity = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if identity(before) != identity(after): raise Failure("input changed while being read")
        return b"".join(chunks)
    finally: os.close(fd)

def parse_elf(data: bytes) -> tuple[str, list[tuple[int, int, int]]]:
    if len(data) < 64 or data[:16] != b"\x7fELF\x02\x01\x01\x00" + b"\0" * 8:
        raise Failure("unsupported ELF identity")
    if u16(data, 0x12) != 62 or u32(data, 0x14) != 1: raise Failure("unsupported ELF ABI")
    phoff, ents, count = u64(data, 0x20), u16(data, 0x36), u16(data, 0x38)
    if ents != 56 or not 0 < count <= 256 or phoff + ents * count > len(data):
        raise Failure("malformed program-header table")
    loads, build_id = [], None
    for i in range(count):
        o = phoff + i * ents; kind = u32(data, o)
        off, va, filesz, memsz = u64(data,o+8),u64(data,o+16),u64(data,o+32),u64(data,o+40)
        if filesz > memsz or off + filesz > len(data): raise Failure("program segment exceeds file")
        if kind == 1: loads.append((va, va + filesz, off))
        elif kind == 4:
            p, end = off, off + filesz
            while p < end:
                if p + 12 > end: raise Failure("truncated PT_NOTE")
                ns, ds, nt = struct.unpack_from("<III", data, p); p += 12
                np, dp = (ns+3)&~3, (ds+3)&~3
                if p + np + dp > end: raise Failure("malformed PT_NOTE")
                name=data[p:p+ns]; p+=np; desc=data[p:p+ds]; p+=dp
                if name.rstrip(b"\0")==b"GNU" and nt==3:
                    if build_id is not None: raise Failure("duplicate Build ID")
                    build_id=desc.hex()
    loads.sort()
    if build_id is None or not loads: raise Failure("required ELF records absent")
    for a,b in zip(loads,loads[1:]):
        if a[1] > b[0]: raise Failure("overlapping PT_LOAD ranges")
    return build_id, loads

def map_va(va: int, size: int, loads: list[tuple[int,int,int]]) -> int:
    hits=[off+va-start for start,end,off in loads if start<=va and va+size<=end]
    if len(hits)!=1: raise Failure(f"VA does not map uniquely: 0x{va:x}")
    return hits[0]

def at(data: bytes, va: int, size: int, loads: list[tuple[int,int,int]]) -> bytes:
    o=map_va(va,size,loads); return data[o:o+size]

def cstring(data: bytes, va: int, loads: list[tuple[int,int,int]]) -> str:
    o=map_va(va,1,loads); e=data.find(b"\0",o,min(len(data),o+4096))
    if e<0: raise Failure(f"unterminated string at 0x{va:x}")
    try: return data[o:e].decode("utf-8","strict")
    except UnicodeDecodeError as exc: raise Failure("literal is not UTF-8") from exc

def call_target(data: bytes, va: int, loads: list[tuple[int,int,int]]) -> int:
    raw=at(data,va,5,loads)
    if raw[0]!=0xE8: raise Failure(f"expected direct call at 0x{va:x}")
    return va+5+struct.unpack_from("<i",raw,1)[0]

def direct_targets(data: bytes, start: int, end: int, loads: list[tuple[int,int,int]]) -> list[int]:
    raw=at(data,start,end-start,loads); out=[]
    for i in range(len(raw)-4):
        if raw[i]==0xE8: out.append(start+i+5+struct.unpack_from("<i",raw,i+1)[0])
    return out

def analyze(path: Path) -> dict[str,object]:
    data=stable_read(path); digest=hashlib.sha256(data).hexdigest()
    if len(data)!=EXPECTED_SIZE or digest!=EXPECTED_SHA256: raise Failure("ELF identity mismatch")
    build_id,loads=parse_elf(data)
    if build_id!=EXPECTED_BUILD_ID: raise Failure("Build ID mismatch")
    ranges={}
    for role,(start,end,want) in RANGES.items():
        got=hashlib.sha256(at(data,start,end-start,loads)).hexdigest()
        if got!=want: raise Failure(f"range drift: {role}")
        ranges[role]={"start":start,"end_exclusive":end,"sha256":got}
    literals={}
    for role,(va,want) in LITERALS.items():
        got=cstring(data,va,loads)
        if got!=want: raise Failure(f"literal drift: {role}")
        literals[role]={"va":va,"value":got}
    calls={}
    for role,(site,want) in DIRECT_CALLS.items():
        got=call_target(data,site,loads)
        if got!=want: raise Failure(f"call drift: {role}")
        calls[role]={"site":site,"target":got}
    anchors={}
    for role,(va,hexed) in ANCHORS.items():
        want=bytes.fromhex(hexed); got=at(data,va,len(want),loads)
        if got!=want: raise Failure(f"anchor drift: {role}")
        anchors[role]={"va":va,"size":len(got),"sha256":hashlib.sha256(got).hexdigest()}
    wait_targets=direct_targets(data,*RANGES["process_wait"][:2],loads)
    if 0x237E0 in wait_targets: raise Failure("process wait helper now checks QProcess exitCode")
    pipeline_targets=direct_targets(data,*RANGES["pipeline_runner"][:2],loads)
    if pipeline_targets.count(0x21FE0)!=1: raise Failure("pipeline pclose inventory drift")
    return {
      "schema":SCHEMA,"tool":{"name":TOOL,"version":VERSION},
      "artifact":{"size":len(data),"sha256":digest,"build_id":build_id},
      "exact_static":{
        "boot_destination_matrix":[
          {"iteration":0,"partition":"p1","source":"selected normal staging file","destination":"iasImage"},
          {"iteration":1,"partition":"p2","source":"selected normal staging file","destination":"iasImage"},
          {"iteration":1,"partition":"p2","source":"selected _sub staging file","destination":"iasImage_sub"},
        ],
        "mode_dispatch":{"mode_byte_va":0x6D20B4,"zero":"direct size-checking copy helper","nonzero":"DecryptToPIPE-to-dd pipeline"},
        "mount_contract":{"wait_for_finished_infinite":True,"wait_failure_logged":True,"exit_code_checked":False,"exit_code_contributes_to_swap_result":False},
        "pipeline_contract":{"stderr_redirected_to_stdout":True,"stdout_drained_with_fgets":True,"pclose_called":True,"pclose_status_checked":False,"exit_status_contributes_to_swap_result":False},
        "direct_copy_contract":{"normal_result_tested":True,"sub_result_tested":True,"copy_failures_logged":True,"copy_failures_increment_key_failure_counter":False,"copy_results_contribute_to_common_tail_return":False},
        "unmount_contract":{"return_tested_for_logging":True,"return_contributes_to_swap_result":False},
        "common_tail":{"key_failure_counter_increment":"nonzero key-retrieval result","iterations":2,"return_formula":"1 XOR ((key_failures > 1) AND (mode_byte & 1))","mode_zero_tail_result":True,"mode_one_false_only_if_both_key_retrievals_fail":True},
        "caller_latches":[
          {"call_site":0x12003F,"latch_offset":0x240,"stores_one_only_on_true_return":True},
          {"call_site":0x1225C8,"latch_offset":0x240,"stores_one_only_on_true_return":True},
        ],
        "ranges":ranges,"literals":literals,"direct_calls":calls,"instruction_anchors":anchors,
        "bounded_absence":{"qprocess_exit_code_calls_in_wait_helper":0},
      },
      "conclusions":{
        "staging_to_boot_partition_write_paths_present":True,
        "normal_image_targets_both_boot_partitions":True,
        "sub_image_targets_second_boot_partition":True,
        "true_return_proves_mount_success":False,
        "true_return_proves_direct_copy_success":False,
        "true_return_proves_pipeline_exit_success":False,
        "true_return_proves_durable_boot_partition_bytes":False,
        "caller_success_latch_can_follow_bounded_weak_true_return":True,
        "persistent_boot_selector_changed":None,
        "abl_or_micom_acceptance":None,"mark_good_or_health":None,"rollback":None,
        "root_or_persistence":False,
      },
      "limitations":[
        "The analyzer proves construction and exact-static result propagation, not runtime invocation or effects.",
        "Process completion without an exit-code check does not establish a successful mount.",
        "Draining a pipeline and calling pclose without using its status does not establish successful decryption or dd output.",
        "A true swapSystem return and caller latch do not establish durable boot-partition bytes.",
        "The routine updates files on both boot partitions but does not by itself establish a persistent boot selector, boot acceptance, health, mark-good, rollback, root, or persistence.",
      ],
    }

def encode(value: dict[str,object]) -> bytes:
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False,separators=(",",": "))+"\n").encode("utf-8")
def write_exclusive(path: Path,payload: bytes)->None:
    flags=os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_CLOEXEC",0)
    try: fd=os.open(path,flags,0o600)
    except OSError as exc: raise Failure(f"cannot create output exclusively: {exc}") from exc
    try:
        n=0
        while n<len(payload):
            w=os.write(fd,payload[n:])
            if w<=0: raise Failure("short output write")
            n+=w
    finally: os.close(fd)
def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("elf",type=Path);p.add_argument("-o","--output",type=Path)
    a=p.parse_args(argv)
    try:
        payload=encode(analyze(a.elf))
        if a.output is None: sys.stdout.buffer.write(payload)
        else: write_exclusive(a.output,payload)
    except Failure as exc:
        print(f"error: {exc}",file=sys.stderr);return 2
    return 0
if __name__=="__main__": raise SystemExit(main())
