#!/usr/bin/env python3
"""Verify AppFUMO system-swap latch and completion-flow semantics."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, sys
from pathlib import Path

SCHEMA="appfumo-system-swap-completion/v1";VERSION="1.0.0"
BASE_HASH="c0edbbe93df218192f315437132764549453e78f7a93fec350540637312a1e82"
BASE_PATH=Path(__file__).with_name("appfumo_boot_partition_write.py")
class Failure(Exception):pass

def load_base():
    try:b=BASE_PATH.read_bytes()
    except OSError as e:raise Failure(f"cannot read bound helper: {e}") from e
    if hashlib.sha256(b).hexdigest()!=BASE_HASH:raise Failure("bound ELF helper identity mismatch")
    spec=importlib.util.spec_from_file_location("_appfumo_bound_elf",BASE_PATH)
    if not spec or not spec.loader:raise Failure("cannot load bound ELF helper")
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

RANGES={
 "update_info_handler":(0x11F1B0,0x120A9E,"8d8cbd6f13b03f5e744a9419937d37db6390cef7c6022c7e8a4d52ee6fe3b959"),
 "get_navi_extended_update":(0x8ED40,0x8ED9C,"5d6fd733ae8a3cfc9f9cddd4b36a23d27e982b6efb8a86270a56a6a72999c486"),
 "get_root_updated":(0x8EE00,0x8EE5C,"9cedfbf6530b72ae8a5f927905c6c1245015acb70ed7ed8b3a9a82136cb300af"),
 "get_navi_updated":(0x8EEC0,0x8EF1C,"88cde4481812191548ed102af59d273880e3e72d65cd040c51d0b4d1efb7d790"),
 "get_resource_updated":(0x8F100,0x8F15C,"87a0a479102e8e411cc2835be31d2f4029a27d7fa563fd000178c947b5afa828"),
 "ext_folder_predicate":(0xEDEF0,0xEE2E3,"ef44910f6ca468e807b7d72f96068d8ee3970ddcf8362b3e8d3926974038bec0"),
 "marker_remove_helper":(0x13FEB0,0x140025,"fb184af8a802f616510da2f5fc50a62509fd25902b46c8c5ae4fb12904d71ba4"),
}
LITERALS={
 "root_updated_log":(0x215051,"\t [%s] m_rootUpdated : %d "),
 "system_swap_complete_log":(0x225398,"###[newota][%s:%d] %s() \t ***************************  Upgrade complate ******************************* :: m_systemSwapComplte [%d] "),
 "ext_units":(0x223B10,"/update/extInfoUpdate/ext_units"),"touch_template":(0x22073D,"touch %1"),
 "state_report":(0x225470,"/update/extInfoUpdate/StateReport2DM"),"state_ready":(0x22DCFC,"ready"),
 "firmware_complete_signal":(0x222478,"/update/exfirmware_update_complete"),
 "system_completed_marker":(0x20A658,"/update/system_update_completed"),
 "system_complete_marker":(0x20A678,"/update/system_update_complete"),
 "firmware_complete_marker":(0x20A698,"/update/firmware_update_complete"),
 "kernel_finish_command":(0x225568,"echo [USB-UPDATE] UPDATE FINISH >/dev/kmsg"),
 "finish_log":(0x220761,"[%s] UPDATE FINISH !!!  \n"),
}
CALLS={
 "read_root_updated":(0x11F624,0x8EE00),"ext_folder_predicate":(0x11F667,0xEDEF0),
 "ext_units_execute":(0x11F6F9,0x23900),"read_navi_updated":(0x11F840,0x8EEC0),
 "read_navi_extended":(0x11F85A,0x8ED40),"navi_completion_normal":(0x11F86E,0x148010),
 "read_resource_updated":(0x11F884,0x8F100),"remove_system_completed_marker":(0x11F8B3,0x13FEB0),
 "swap_system":(0x12003F,0x148E70),"finish_system_call":(0x1200D7,0x24790),
}
ANCHORS={
 "root_getter_and_current_latch":(0x11F620,"488b7b40e8d7f7f6ff84c00f85bf0700000fb6ab40020000e82366f3ff4889c74189e9b90c0d00004c8d05b1ac100031c0488d15cef40f00488d35395d1000e8cc7d0100"),
 "ext_folder_and_latch_gate":(0x11F664,"4889dfe884e8fcff84c00f84c801000080bb40020000000f84bb010000e8da65f3ff4c8d0573ac10004889c7b90e0d0000488d158af40f0031c0488d357b5d1000e8867d0100488dac2430010000488d35574410004889efe8cf64f3ff4c8dac2420010000488d356d1010004c89efe8b864f3ff4c8dbc244001000041b82000000031c94889ea4c89ee4c89ffe83a35f0ff4c89ffe80242f0ff4c"),
 "navi_resource_then_marker":(0x11F83C,"488b7b40e87bf6f6ff84c00f843300000080bb4102000000752a488b7b40e8e1f4f6ff84c00f84590c0000488bbb38020000e89d87020084c07409c68341020000016690488b7b40e877f8f6ff84c00f857f050000488dac24b0010000488d35b8ad0e004889efe8e862f3ffe8b36bf4ff4889ee4889c7e8f80502004889efe8a0c0f2ff"),
 "swap_false_rejoins_and_true_latches":(0x120038,"488bbb38020000e82c8e020084c00f84e5f5ffffc6834002000001bd01000000e9dbf5ffff"),
 "downstream_finish_log":(0x1200C8,"4889dfe880a3fcff488d3d91541000e8b446f0ffe87f5bf3ff488d1538a210004889c731c0488d356d061000e837730100"),
}

def analyze(path:Path)->dict:
    base=load_base()
    try:data=base.stable_read(path);digest=hashlib.sha256(data).hexdigest();bid,loads=base.parse_elf(data)
    except Exception as e:raise Failure(str(e)) from e
    if len(data)!=base.EXPECTED_SIZE or digest!=base.EXPECTED_SHA256 or bid!=base.EXPECTED_BUILD_ID:raise Failure("ELF identity mismatch")
    rs={}
    for role,(a,z,want) in RANGES.items():
        got=hashlib.sha256(base.at(data,a,z-a,loads)).hexdigest()
        if got!=want:raise Failure(f"range drift: {role}")
        rs[role]={"start":a,"end_exclusive":z,"sha256":got}
    ls={}
    for role,(a,want) in LITERALS.items():
        got=base.cstring(data,a,loads)
        if got!=want:raise Failure(f"literal drift: {role}")
        ls[role]={"va":a,"value":got}
    cs={}
    for role,(a,want) in CALLS.items():
        got=base.call_target(data,a,loads)
        if got!=want:raise Failure(f"call drift: {role}")
        cs[role]={"site":a,"target":got}
    an={}
    for role,(a,h) in ANCHORS.items():
        want=bytes.fromhex(h);got=base.at(data,a,len(want),loads)
        if got!=want:raise Failure(f"anchor drift: {role}")
        an[role]={"va":a,"size":len(got),"sha256":hashlib.sha256(got).hexdigest()}
    return {"schema":SCHEMA,"tool":{"name":"appfumo-system-swap-completion","version":VERSION,"bound_elf_helper_sha256":BASE_HASH},
      "artifact":{"size":len(data),"sha256":digest,"build_id":bid},"exact_static":{
       "controller_fields":{"root_updated_getter_object_offset":0x45,"system_swap_complete_handler_offset":0x240,"navi_complete_handler_offset":0x241,"resource_complete_handler_offset":0x242},
       "swap_result_flow":{"root_updated_true_requests_swap":True,"swap_true_stores_one_at_0x240":True,"swap_false_returns_to_current_latch_log":True,"swap_false_aborts_handler":False},
       "ext_units_flow":{"requires_ext_folder_predicate":True,"requires_system_swap_latch":True,"qprocess_execute_result_used":False},
       "downstream_flow":{"navi_and_resource_blocks_follow_swap_block":True,"system_completed_marker_helper_follows_resource_block":True,"system_completed_marker_helper_requires_0x240":False,"finish_log_is_downstream_in_same_handler":True,"all_paths_reach_finish_log":False},
       "ranges":rs,"literals":ls,"direct_calls":cs,"instruction_anchors":an},
      "conclusions":{"system_swap_latch_is_not_a_mandatory_gate_for_downstream_marker_handling":True,"weak_swap_true_can_set_system_swap_latch":True,"swap_false_can_continue_in_handler":True,"completion_log_proves_successful_boot_partition_bytes":False,"persistent_boot_selection_proved":False,"boot_acceptance_or_mark_good_proved":False,"root_or_persistence_proved":False},
      "limitations":["This is exact-static control flow, not runtime invocation or successful effects.","The handler has additional state and file predicates; the package does not claim every path reaches the final log.","Marker removal, QProcess::execute, system(), and log call sites do not establish successful or durable effects.","Neither a latch nor downstream completion handling proves selected boot bytes, persistent activation, ABL/MICOM acceptance, health, mark-good, rollback, root, or persistence."]}

def encode(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False,separators=(",",": "))+"\n").encode()
def write_exclusive(p:Path,b:bytes):
    try:fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_CLOEXEC",0),0o600)
    except OSError as e:raise Failure(f"cannot create output exclusively: {e}") from e
    try:
        n=0
        while n<len(b):
            w=os.write(fd,b[n:]);
            if w<=0:raise Failure("short output write")
            n+=w
    finally:os.close(fd)
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("elf",type=Path);p.add_argument("-o","--output",type=Path);a=p.parse_args(argv)
    try:
        b=encode(analyze(a.elf));write_exclusive(a.output,b) if a.output else sys.stdout.buffer.write(b)
    except Failure as e:print(f"error: {e}",file=sys.stderr);return 2
    return 0
if __name__=="__main__":raise SystemExit(main())
