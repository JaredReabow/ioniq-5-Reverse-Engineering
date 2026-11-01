#!/usr/bin/env python3
"""Verify stock DecryptToPIPE output and fallback integrity boundaries."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,stat,struct,sys,tarfile
from pathlib import Path
SCHEMA="decrypttopipe-output-integrity/v1";VERSION="1.0.0"
ROOTFS_SIZE=879109759;ROOTFS_SHA="423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84"
MEMBER="app/share/AppUpgrade/DecryptToPIPE";HELPER_SIZE=559192;HELPER_SHA="e3110811e83701368e638947e6d8887f59321707e70f6288adf0790090d929c0";HELPER_BUILD="4303e27a93f0acfb308146a5d034dafbffa064d0"
ELF_HELPER_HASH="c0edbbe93df218192f315437132764549453e78f7a93fec350540637312a1e82";MATRIX_HELPER_HASH="af2b37b8d5dca602edff12bb801ed3cba02c361c243d300e173ebd5b0d4c1e20"
BASE=Path(__file__).parent
RANGES={"main":(0x8110,0x8197,"ef61feff42227530a048d72745fff99f0c8b1daff0613a31edb8ed471cfb0aee"),"stream":(0x82d0,0x8461,"c0809b306973e00197084b5ee5b9a5bba9547ab198d247a10c9feed5ae15c62b"),"offset_parser":(0x8470,0x84ef,"bad26422eb28d5a4c77b84843e397baf2702b4520b68b11d8464060b1837ef53"),"envelope_parser":(0x9080,0x954e,"d7236fde765b031f0753e4937417a0dabc3d85fb04277d493224ea1345d2bd49"),"decrypt_reader":(0x9550,0x98ce,"478b4d9d1b05488240c1273ab8d87d21fd0d547a457f9abf82c9a5e9db16003a"),"stream_close":(0x9d50,0x9dec,"062a0d3dcef9b90129000bfa27511e53ad9e04e1908c113625e983ed0953120b"),"key_loader":(0x9e50,0x9ef4,"9f4932d4d87704a33c5b03bbdb531a73ad30a8c9d94aa9301371eb6d2dab000c")}
CALLS={"main_load_key":(0x8168,0x9e50),"main_parse_offset":(0x8171,0x8470),"main_stream":(0x8184,0x82d0),"stream_parse_envelope":(0x8328,0x9080),"decrypt_stdout_write":(0x837b,0x7fd0),"fallback_fopen":(0x83fa,0x7fa0),"fallback_fseek":(0x840f,0x7d80),"fallback_stdout_write":(0x842b,0x7fd0),"fallback_fread":(0x8445,0x7ec0),"fallback_fclose":(0x8452,0x7f40)}
ANCHORS={"main_dispatch_and_zero_return":(0x8125,"83ff047e0c488b46084889f380382d741831c0488b4c24086448330c2528000000754a4883c4105bc30fb6500180fa6475348078020075d9488b7b10488d3518ff2700e8e31c0000488b7b20e8fa020000488d15f3fe2700488b7b18488902e847010000ebab80fa4475a6ebc5"),"stream_result_classification":(0x8328,"e8530d00004989c58b44240c3d6cfeffff0f84b100000085c0757d"),"decrypt_write_negative_only":(0x8367,"660f1f8400000000004889c24889debf01000000e850fcffff4885c07833"),"plaintext_fallback_negative_only":(0x83f0,"488d35cd3605004c89e7e8a1fbffff4989c44885c074b931d24889ee4889c7e86cf9ffffeb1f662e0f1f8400000000004889c24889debf01000000e8a0fbffff4885c0781a4c89e1ba00020000be010000004889dfe876faffff4885c07fd14c89e7e8e9faffff"),"te2_or_minus404_parser":(0x90f7,"e8e4eeffff4885c00f8edb030000483d244000007e71488db0dcbfffff4889df31d2e802ecffff4889df85c00f85a2000000e8b2eeffff4989c54885c00f8ea6030000be01000000bf24400000e8e7edffff4889c54885c00f84ae0300004889d9ba01000000be244000004889c7e856edffff4883f8017550807d0054746a4889efe862ecffff4889dfe8baedffff41c7066cfeffff31c0488b8c24c80200006448330c25280000000f85a30300004881c4d80200005b5d415c415d415e415fc30f1f8400000000004889efe818ecffff4889dfe870edffff41c7066efeffff31c0ebb40f1f440000807d014575900fb645023c520f8404030000c7442414030000003c320f8574ffffff"),"minus404_store":(0x9176,"4889efe862ecffff4889dfe8baedffff41c7066cfeffff31c048"),"numeric_offset_parser":(0x8470,"534889fb4883ec1064488b042528000000488944240831c0e863f9ffff83e80178544863f889c0b901000000488d343b4883ef014829c731c04801df0f1f40000fbe164883ee0183ea304863d2480fafd1488d0c894801c94801d04839fe75e0488b5c24086448331c2528000000750a4883c4105bc3")}
class Failure(Exception):pass
def load_bound(name:str,want:str):
 p=BASE/name
 try:b=p.read_bytes()
 except OSError as e:raise Failure(f"cannot read bound helper {name}: {e}") from e
 if hashlib.sha256(b).hexdigest()!=want:raise Failure(f"bound helper identity mismatch: {name}")
 s=importlib.util.spec_from_file_location("_bound_"+name.replace(".","_"),p)
 if not s or not s.loader:raise Failure("cannot import bound helper")
 m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def canon(name:str)->str:
 if not isinstance(name,str) or not name or name.startswith("/") or "\\" in name or "\0" in name:raise Failure("unsafe archive member spelling")
 parts=name.split("/")
 if parts and parts[0]==".":parts=parts[1:]
 if not parts or any(x in ("",".","..") for x in parts):raise Failure("unsafe archive member component")
 return "/".join(parts)
def archive_member(path:Path)->tuple[bytes,dict]:
 flags=os.O_RDONLY|getattr(os,"O_CLOEXEC",0)|getattr(os,"O_NOFOLLOW",0)
 try:fd=os.open(path,flags)
 except OSError as e:raise Failure(f"cannot safely open rootfs: {e}") from e
 try:
  before=os.fstat(fd);ident=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  if not stat.S_ISREG(before.st_mode) or before.st_size!=ROOTFS_SIZE:raise Failure("rootfs identity size mismatch")
  h=hashlib.sha256();left=before.st_size
  while left:
   c=os.read(fd,min(left,1<<20))
   if not c:raise Failure("short rootfs read")
   h.update(c);left-=len(c)
  if h.hexdigest()!=ROOTFS_SHA:raise Failure("rootfs SHA-256 mismatch")
  if ident(before)!=ident(os.fstat(fd)):raise Failure("rootfs changed while hashing")
  os.lseek(fd,0,os.SEEK_SET);found=[]
  with os.fdopen(os.dup(fd),"rb",closefd=True) as f:
   try:
    with tarfile.open(fileobj=f,mode="r:gz") as tf:
     for ti in tf:
      if ti.name==".":continue
      c=canon(ti.name)
      if c!=MEMBER:continue
      if not ti.isreg() or ti.issym() or ti.islnk():raise Failure("selected archive member is not a regular file")
      if ti.uid!=0 or ti.gid!=0 or ti.mode&0o7777!=0o755 or ti.size!=HELPER_SIZE:raise Failure("selected archive metadata drift")
      x=tf.extractfile(ti)
      if x is None:raise Failure("cannot read selected archive member")
      data=x.read(HELPER_SIZE+1)
      if len(data)!=HELPER_SIZE:raise Failure("selected archive member length drift")
      found.append(data)
   except (tarfile.TarError,OSError,EOFError) as e:raise Failure(f"rootfs archive parse failure: {e}") from e
  if len(found)!=1:raise Failure(f"selected archive member multiplicity: {len(found)}")
  if ident(before)!=ident(os.fstat(fd)):raise Failure("rootfs changed while parsing")
  data=found[0]
  if hashlib.sha256(data).hexdigest()!=HELPER_SHA:raise Failure("DecryptToPIPE member hash mismatch")
  return data,{"canonical_name":MEMBER,"size":HELPER_SIZE,"sha256":HELPER_SHA,"uid":0,"gid":0,"mode":"0755"}
 finally:os.close(fd)
def analyze(rootfs:Path,appfumo:Path,bootdir:Path)->dict:
 elf=load_bound("appfumo_boot_partition_write.py",ELF_HELPER_HASH);matrix=load_bound("eu260128_boot_container_matrix.py",MATRIX_HELPER_HASH)
 helper,meta=archive_member(rootfs);bid,loads=elf.parse_elf(helper)
 if bid!=HELPER_BUILD:raise Failure("DecryptToPIPE Build ID mismatch")
 rs={}
 for role,(a,z,w) in RANGES.items():
  got=hashlib.sha256(elf.at(helper,a,z-a,loads)).hexdigest()
  if got!=w:raise Failure(f"range drift: {role}")
  rs[role]={"start":a,"end_exclusive":z,"sha256":got}
 cs={}
 for role,(site,w) in CALLS.items():
  got=elf.call_target(helper,site,loads)
  if got!=w:raise Failure(f"call drift: {role}")
  cs[role]={"site":site,"target":got}
 ans={}
 for role,(a,h) in ANCHORS.items():
  want=bytes.fromhex(h);got=elf.at(helper,a,len(want),loads)
  if got!=want:raise Failure(f"anchor drift: {role}")
  ans[role]={"va":a,"size":len(got),"sha256":hashlib.sha256(got).hexdigest()}
 app=elf.stable_read(appfumo)
 if len(app)!=elf.EXPECTED_SIZE or hashlib.sha256(app).hexdigest()!=elf.EXPECTED_SHA256:raise Failure("AppFUMO identity mismatch")
 abid,aloads=elf.parse_elf(app)
 if abid!=elf.EXPECTED_BUILD_ID or elf.cstring(app,0x22DB4A,aloads)!="%1 -d %2 %3 0 | ":raise Failure("AppFUMO pipeline contract drift")
 try:names={x.name for x in os.scandir(bootdir)}
 except OSError as e:raise Failure(f"cannot scan boot sources: {e}") from e
 if names!=set(matrix.FILES):raise Failure("boot source filename set mismatch")
 rows=[]
 for name in sorted(matrix.FILES):
  size,want,_,wrapped,_,_=matrix.FILES[name];raw=matrix.stable_read(bootdir/name)
  if len(raw)!=size or hashlib.sha256(raw).hexdigest()!=want:raise Failure(f"boot source identity mismatch: {name}")
  if len(raw)<=matrix.META:classification="minus404_size"
  else:
   trailer=raw[-matrix.META:]
   classification="te2_decrypt" if trailer[:2]==b"TE" and trailer[2] in (ord("R"),ord("2")) else "minus404_magic"
  expected="te2_decrypt" if wrapped else "minus404_magic"
  if classification!=expected:raise Failure(f"parser classification drift: {name}")
  rows.append({"name":name,"source_sha256":want,"te2_wrapped":wrapped,"trailer_prefix_hex":raw[-matrix.META:-matrix.META+4].hex(),"parser_classification":classification,"fallback_offset":None if wrapped else 0})
 return {"schema":SCHEMA,"tool":{"name":"decrypttopipe-output-integrity","version":VERSION,"bound_helpers":{"elf":ELF_HELPER_HASH,"matrix":MATRIX_HELPER_HASH}},"rootfs":{"size":ROOTFS_SIZE,"sha256":ROOTFS_SHA,"member":meta},"decrypttopipe":{"size":len(helper),"sha256":HELPER_SHA,"build_id":bid,"ranges":rs,"direct_calls":cs,"instruction_anchors":ans},"appfumo":{"sha256":elf.EXPECTED_SHA256,"build_id":abid,"pipeline_template":"%1 -d %2 %3 0 | ","numeric_offset":0},"boot_sources":rows,"exact_static":{"normal_images_select_te2_path":True,"all_sub_images_select_minus404_fallback":True,"minus404_fallback_copies_from_offset_zero":True,"other_parser_errors_can_emit_no_output":True,"main_exit_status_after_stream_call":0,"decrypt_write_rejects_only_negative":True,"fallback_write_rejects_only_negative":True,"short_nonnegative_write_is_fully_accounted":False},"conclusions":{"plaintext_sub_pass_through_route_present":True,"decrypt_or_write_failure_propagates_to_process_exit":False,"process_zero_exit_proves_complete_output":False,"appfumo_pipeline_proves_complete_dd_input":False,"final_boot_partition_bytes_or_durability_proved":False,"boot_acceptance_or_persistence_proved":False},"limitations":["Static classification proves branch selection for the exact package bytes; no target helper or pipeline was executed.","A pass-through route and zero offset do not prove complete stdout delivery because short nonnegative writes are not retried.","The surrounding AppFUMO helper discards pclose status, and this process itself returns zero after stream failures.","No conclusion establishes final partition bytes, boot selection, external key acceptance, health, mark-good, rollback, root, or persistence."]}
def encode(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False,separators=(",",": "))+"\n").encode()
def write_exclusive(p:Path,b:bytes):
 try:fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_CLOEXEC",0),0o600)
 except OSError as e:raise Failure(f"cannot create output exclusively: {e}") from e
 try:
  n=0
  while n<len(b):
   w=os.write(fd,b[n:])
   if w<=0:raise Failure("short output write")
   n+=w
 finally:os.close(fd)
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--rootfs",type=Path,required=True);p.add_argument("--appfumo",type=Path,required=True);p.add_argument("--boot-dir",type=Path,required=True);p.add_argument("-o","--output",type=Path);a=p.parse_args(argv)
 try:
  b=encode(analyze(a.rootfs,a.appfumo,a.boot_dir));write_exclusive(a.output,b) if a.output else sys.stdout.buffer.write(b)
 except Failure as e:print(f"error: {e}",file=sys.stderr);return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
