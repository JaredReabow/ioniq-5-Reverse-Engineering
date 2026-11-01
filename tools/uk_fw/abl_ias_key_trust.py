#!/usr/bin/env python3
"""Bound exact ABL IAS artifacts against public Intel embedded-key semantics."""
from __future__ import annotations
import argparse,hashlib,json,os,stat,struct,subprocess,sys,tarfile
from pathlib import Path
SCHEMA="abl-ias-key-trust/v1";VERSION="1.1.0"
UPDATE_SIZE=42101042;UPDATE_SHA="1e67344a714708733a9158a52ef5d4def95b126e5725d070669ea64e0644c4c8";ABL_MEMBER="abl/bin/104096/abl1714-Batch10-Ver.11.00-sign-8MB.bin";ABL_SHA="f6fc0373042c27f36e601fe957544582f3b1bd4be3c36659105322304b2dc7ac"
ROOT_SIZE=879109759;ROOT_SHA="423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84";APP_MEMBER="bin/ias_image_app";APP_SHA="849b6b575ab76f865684d44f49977cf6c4b5fa60ae2cfb70c49a4a66424368d8";APP_BUILD="adbd4f651cf1d63e7e5f52f7a32dc54fb507bd48"
SBL_COMMIT="5f5c14b10ae6bd3cd0cf7e274142767dc2635a06";IAS_COMMIT="a4068106f9971ed1362def1f71a8eccf90fc4422"
SBL_FILES={"BootloaderCommonPkg/Library/IasImageLib/IasImage.c":"c44a7f2a4f24a732d312edaf483a7b60f14b7597106d23ed6ccbc6d56065d497","BootloaderCommonPkg/Library/SecureBootLib/SecureBootRsa.c":"96dedbded8805d3a1de7d9745f97cfcb27ecf89ad4bae7846e612469993378ae","BootloaderCommonPkg/Library/SecureBootLib/SecureBootHash.c":"49d3fa1c8570ad87ac54c8ee548eb845b8e9da39c8355e85501f7414317e5e7b","PayloadPkg/Library/PayloadLib/PayloadLib.c":"4eecd21c2ddec495d394b869f7282908523ec46ff5e36f15f73dcbea00d2f107"}
IAS_FILES={"iasimage.py":"6a32c7df4503aa10679d3729903c583dad81bed290ee79e6f7ad1dd936252394","README.md":"e0c2c42683f8e880632da2133b080f81fc8649e97507806652c74475fd983422"}
FILES={"iasImage":(6226728,"6db0bb746722389092e60681554a3b9f1b391f8def59c65c68e764cc9d6007ce",True),"iasImage_1280":(6226728,"c2a314bc63e1dbe1440bd87b9135210b6eea356727ba03bdecb692b61d3bce4e",True),"iasImage_1280_sub":(6210308,"55e9a31be5ca734a7af111613ae6ce83cdc579b27138c5f54700f78263056eb0",False),"iasImage_1920_12":(6226728,"aaa0384e4f147ec016f019f839a06a7ed19f3a407d8b0d23070c97c8c459e0dd",True),"iasImage_1920_12_sub":(6210308,"e4d7523ba0f77a7b659260df82968d515859b01e06738bf7cfd79bef83db8e05",False),"iasImage_p5":(6226728,"57ea6691a1118020bc263c1fbdba3d7e26dd0240f4c89fac380c5578708376b0",True),"iasImage_p5_1280":(6226728,"7e8fd8c426c64eec197462aed53290c63e1a12aea43a5556f45acd2c90da3476",True),"iasImage_p5_1280_sub":(6210308,"fb442a993619b17c94c95826cc425a6e04c3e947c1f9c009191dec63607acbad",False),"iasImage_p5_1920_12":(6226728,"7d3c4c43cee76c45518f85df2ac07cb124a7984d238d7189e6ead9e4967500f3",True),"iasImage_p5_1920_12_sub":(6210308,"e4d7523ba0f77a7b659260df82968d515859b01e06738bf7cfd79bef83db8e05",False),"iasImage_p5_sub":(6210308,"47a6f19f395529814be3eeb7a5751815fab8d31b36fdc503ef025e65070a484f",False),"iasImage_sub":(6210308,"deb69570c89a37f15a92a2e07247138ab0ed83ea108141f24536db6f0f9bbc7f",False)}
MOD_HASH="227d89f5a3cabed4efb8e67d5a0f9fa29d03a6759b8a150503fb383698fedea6";TE2_META=0x4024;TE2_KEY=bytes.fromhex("60a93d70f73302a63e5ed0d0ea38be22")
class Failure(Exception):pass
def canon(n):
 if n==".":return None
 if not isinstance(n,str) or not n or n.startswith("/") or "\\" in n or "\0" in n:raise Failure("unsafe archive member spelling")
 p=n.split("/");p=p[1:] if p and p[0]=="." else p
 if not p or any(x in ("",".","..") for x in p):raise Failure("unsafe archive member component")
 return "/".join(p)
def archive_one(p:Path,total:int,digest:str,name:str,size:int,mode:int,uid:int,gid:int)->bytes:
 fl=os.O_RDONLY|getattr(os,"O_CLOEXEC",0)|getattr(os,"O_NOFOLLOW",0)
 try:fd=os.open(p,fl)
 except OSError as e:raise Failure(f"cannot safely open archive: {e}") from e
 try:
  a=os.fstat(fd);ident=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  if not stat.S_ISREG(a.st_mode) or a.st_size!=total:raise Failure("archive size/type mismatch")
  h=hashlib.sha256();left=total
  while left:
   c=os.read(fd,min(left,1<<20))
   if not c:raise Failure("short archive read")
   h.update(c);left-=len(c)
  if h.hexdigest()!=digest or ident(a)!=ident(os.fstat(fd)):raise Failure("archive identity mismatch")
  os.lseek(fd,0,0);found=[]
  with os.fdopen(os.dup(fd),"rb") as f:
   try:
    with tarfile.open(fileobj=f,mode="r:gz") as t:
     seen=set()
     for x in t:
      q=canon(x.name)
      if q is None:continue
      if q in seen:raise Failure("duplicate canonical archive identity")
      seen.add(q)
      if q!=name:continue
      if not x.isreg() or x.uid!=uid or x.gid!=gid or x.mode&0o7777!=mode or x.size!=size:raise Failure("selected archive member metadata drift")
      z=t.extractfile(x)
      if z is None:raise Failure("selected archive member unreadable")
      b=z.read(size+1)
      if len(b)!=size:raise Failure("selected archive member size drift")
      found.append(b)
   except (tarfile.TarError,OSError,EOFError) as e:raise Failure(f"archive parse failure: {e}") from e
  if len(found)!=1 or ident(a)!=ident(os.fstat(fd)):raise Failure("selected archive multiplicity/change")
  return found[0]
 finally:os.close(fd)
def stable(p:Path,maxn=10_000_000):
 fl=os.O_RDONLY|getattr(os,"O_CLOEXEC",0)|getattr(os,"O_NOFOLLOW",0)
 try:fd=os.open(p,fl)
 except OSError as e:raise Failure(f"cannot safely open {p.name}: {e}") from e
 try:
  a=os.fstat(fd);ident=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
  if not stat.S_ISREG(a.st_mode) or a.st_size>maxn:raise Failure("unbounded input")
  b=[];left=a.st_size
  while left:
   c=os.read(fd,min(left,1<<20))
   if not c:raise Failure("short read")
   b.append(c);left-=len(c)
  if os.read(fd,1) or ident(a)!=ident(os.fstat(fd)):raise Failure("input changed")
  return b"".join(b)
 finally:os.close(fd)
def build_id(b):
 # Parse bounded PT_NOTE bytes for the exact GNU Build ID record.
 p,end=0x254,0x298;found=[]
 while p+12<=end:
  namesz,descsz,typ=struct.unpack_from("<III",b,p);p+=12
  if namesz>64 or descsz>64 or p+((namesz+3)&~3)+((descsz+3)&~3)>end:raise Failure("GNU note bounds drift")
  name=b[p:p+namesz];p+=(namesz+3)&~3;desc=b[p:p+descsz];p+=(descsz+3)&~3
  if name==b"GNU\0" and typ==3:found.append(desc.hex())
 if len(found)!=1:raise Failure("GNU Build ID multiplicity drift")
 return found[0]
def git_blob(repo:Path,commit:str,name:str,want:str)->bytes:
 try:r=subprocess.run(["git","-C",str(repo),"show",f"{commit}:{name}"],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,check=False)
 except (OSError,subprocess.TimeoutExpired) as e:raise Failure(f"git source read failed: {e}") from e
 if r.returncode or hashlib.sha256(r.stdout).hexdigest()!=want:raise Failure(f"public source identity mismatch: {name}")
 return r.stdout
def require(src:bytes,*needles:bytes):
 for n in needles:
  if src.count(n)!=1:raise Failure(f"public source semantic anchor multiplicity: {n[:32]!r}")
def iv_for(name,n):
 x=n if n<1<<31 else n-(1<<32);return hashlib.sha256(f"{name}{x}".encode()).digest()[:16]
def plaintext(name,raw,wrapped):
 if not wrapped:return raw
 body,meta=raw[:-TE2_META],raw[-TE2_META:];iv=iv_for(name,len(body));pad=(-len(body))%16
 if meta[:3]!=b"TE2" or meta[4:36]!=hashlib.sha256(iv+meta[36:]).digest():raise Failure("TE2 metadata drift")
 try:
  from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
 except ImportError as e:raise Failure("cryptography unavailable") from e
 d=Cipher(algorithms.AES(TE2_KEY),modes.CBC(iv)).decryptor();return (d.update(body+meta[36:36+pad])+d.finalize())[:len(body)]
def all_offsets(b:bytes,s:bytes):
 out=[];p=0
 while True:
  p=b.find(s,p)
  if p<0:return out
  out.append(p);p+=1
def lz4_block(raw:bytes,expected:int)->bytes:
 i=0;out=bytearray()
 while len(out)<expected:
  if i>=len(raw):raise Failure("truncated ABL LZ4 token")
  token=raw[i];i+=1;literal=token>>4
  if literal==15:
   while True:
    if i>=len(raw):raise Failure("truncated ABL LZ4 literal length")
    n=raw[i];i+=1;literal+=n
    if n!=255:break
  if i+literal>len(raw) or len(out)+literal>expected:raise Failure("ABL LZ4 literal bounds drift")
  out+=raw[i:i+literal];i+=literal
  if len(out)==expected:break
  if i+2>len(raw):raise Failure("truncated ABL LZ4 offset")
  off=raw[i]|raw[i+1]<<8;i+=2
  if off==0 or off>len(out):raise Failure("invalid ABL LZ4 offset")
  match=(token&15)+4
  if (token&15)==15:
   while True:
    if i>=len(raw):raise Failure("truncated ABL LZ4 match length")
    n=raw[i];i+=1;match+=n
    if n!=255:break
  if len(out)+match>expected:raise Failure("ABL LZ4 match bounds drift")
  for _ in range(match):out.append(out[-off])
 if i!=len(raw):raise Failure("ABL LZ4 trailing compressed bytes")
 return bytes(out)
def direct_calls(b:bytes,target:int)->list[int]:
 out=[]
 for i in range(len(b)-4):
  if b[i]==0xe8 and (i+5+struct.unpack_from("<i",b,i+1)[0])&0xffffffff==target:out.append(i)
 return out
def analyze(update:Path,rootfs:Path,boot:Path,sbl:Path,ias:Path):
 abl=archive_one(update,UPDATE_SIZE,UPDATE_SHA,ABL_MEMBER,8388608,0o755,8100,8100)
 if hashlib.sha256(abl).hexdigest()!=ABL_SHA:raise Failure("ABL firmware hash mismatch")
 app=archive_one(rootfs,ROOT_SIZE,ROOT_SHA,APP_MEMBER,39664,0o755,0,0)
 if hashlib.sha256(app).hexdigest()!=APP_SHA or build_id(app)!=APP_BUILD:raise Failure("ias_image_app identity mismatch")
 if hashlib.sha256(app[0x39e5:0x3a33]).hexdigest()!="107ae64f061d64a6be0fed002ec80a329407ea8988dbaa88d7407bc39a1029e7" or hashlib.sha256(app[0x4150:0x4243]).hexdigest()!="abbf7e26a8570942e3d9f2d011de2239eaf7c3210fd1586d0463f27d89f3e43a":raise Failure("ias_image_app instruction drift")
 # Exact primary BPDT and IBB CPD topology.
 if struct.unpack_from("<IHH",abl,0x100000)!=(0x55AA,13,1):raise Failure("primary BPDT drift")
 entries=[struct.unpack_from("<HHII",abl,0x100018+i*12) for i in range(13)]
 ibb=[x for x in entries if x[0]==4]
 if ibb!=[(4,0,0x87000,0x39000)]:raise Failure("IBB BPDT entry drift")
 if struct.unpack_from("<IIBBBBI",abl,0x187000)[:6]!=(0x44504324,4,1,1,16,50):raise Failure("IBB CPD drift")
 cpd=[]
 for i in range(4):
  nm,raw,sz,_=struct.unpack_from("<12sIII",abl,0x187010+i*24);cpd.append((nm.rstrip(b"\0").decode(),raw&0x1ffffff,sz))
 if cpd!=[("IBBP.man",0x70,0x2ec),("BPM.met",0x380,0xb4),("IBBL",0x440,0x4000),("IBB",0x4440,0x34000)]:raise Failure("IBB CPD entries drift")
 h=struct.unpack_from("<7I",abl,0x18b440)
 if h!=(0x2e6b7069,0,0,0x33cd4,0x2c,0x33cd4,0xf753acfa):raise Failure("IBB IAS header drift")
 sizes=struct.unpack_from("<4I",abl,0x18b45c)
 if sizes!=(0xc0,0x172d2,0x44a9,0x18493):raise Failure("IBB subimage table drift")
 pos=0x18b46c;subs=[]
 for index,n in enumerate(sizes):
  subs.append(abl[pos:pos+n]);pos+=n
  if index+1<len(sizes):pos=(pos+3)&~3
 if pos!=0x1bf13f:raise Failure("IBB subimage extent drift")
 build=subs[0]
 if b"rel.1714-HF3\0release/GP1.0.1_LGE\0" not in build:raise Failure("ABL build identity drift")
 dec=[]
 for i,s in enumerate(subs[1:],1):
  expected=struct.unpack_from("<I",s)[0]
  if expected not in (0x1fe00,0x8b00,0x2a140):raise Failure("ABL LZ4 output-size drift")
  dec.append(lz4_block(s[4:-4],expected))
 stage=dec[0]
 dh=[hashlib.sha256(x).hexdigest() for x in dec]
 if dh!=["3491be59ef865cb376131b02fa1ff6941e37d1c87ae3c4cf7969b5364785b3c2","d1e6d5da3a95a1634ec6a98703775f464044e335e0000f5f1477062f5d91d564","3a8a2ddef16dfefb17b4a28878df601f4e9f5a85fb53e2eecf11c3b4dcf4aa9e"]:raise Failure("ABL decompressed-stage identity drift")
 if stage.find(b"ABL.oemkm")!=0x1c861 or stage.find((0xfc861).to_bytes(4,"little"))!=0xbf04:raise Failure("ABL stage load-base anchor drift")
 ranges={"key_and_payload_auth":(0x157a3,0x159fe,"4b71d5c95ff2bcf4210ba23a96883f3ce3524fb31b40f037a00991a6c14a7f30"),"sha256_wrapper":(0x16bd0,0x16c0c,"bbabc9ec261135c0bd9eb93152e7ba73f99d3c3701b14ebe6cae8074cec2c0b9"),"compare":(0x160d8,0x16100,"7b1c913d8e4f3152d64723470cb26de125cd8f4740690cd1389f3dec67c85796"),"rsa_verify":(0x16c0c,0x16da0,"b83eabfa8f01da0d1523e5ba76d6c92a6081dff4b43d17df3cdf1ec56b5ab94b")}
 for a,z,w in ranges.values():
  if hashlib.sha256(stage[a:z]).hexdigest()!=w:raise Failure("ABL authentication range drift")
 calls=direct_calls(stage,0x157a3)
 if calls!=[0xa1f8,0xa560,0xc1ea,0xc9e0,0xd4fe]:raise Failure("ABL authentication direct-call inventory drift")
 selectors={0xa1f3:0x25,0xa55b:0x28,0xc1e4:0x27,0xc9dc:0x27,0xd4f9:0x28}
 for site,value in selectors.items():
  if stage[site:site+2]!=bytes((0x6a,value)):raise Failure("ABL authentication selector drift")
 # Type 3 OS handling follows a selector-0x27 authentication result.
 if hashlib.sha256(stage[0xc1e4:0xc20c]).hexdigest()!="6e9002a872ebe1bbbb99b2671c0099ae01e782f679260716d7e51e0476e82414":raise Failure("ABL type-3 authentication branch drift")
 # Exact package key and candidate public SBL hash input.
 try:names={x.name for x in os.scandir(boot)}
 except OSError as e:raise Failure(f"cannot scan boot sources: {e}") from e
 if names!=set(FILES):raise Failure("boot source filename set mismatch")
 mod=exp=None
 for name,(n,w,wrapped) in FILES.items():
  raw=stable(boot/name)
  if len(raw)!=n or hashlib.sha256(raw).hexdigest()!=w:raise Failure("boot source identity drift")
  plain=plaintext(name,raw,wrapped)
  if plain[:4]!=b"ipk.":raise Failure("IAS plaintext magic drift")
  _,_,_,dl,do,_,_=struct.unpack_from("<7I",plain);base=do+dl;mm=plain[base+0x200:base+0x300];ee=plain[base+0x300:base+0x304]
  if len(mm)!=256 or ee!=b"\x01\x00\x01\x00" or hashlib.sha256(mm).hexdigest()!=MOD_HASH:raise Failure("embedded key drift")
  if mod is None:mod,exp=mm,ee
  elif (mod,exp)!=(mm,ee):raise Failure("embedded key disagreement")
 candidate=hashlib.sha256(mod[::-1]+exp).digest()
 # Public source semantics, preserved as public-source evidence only.
 src={n:git_blob(sbl,SBL_COMMIT,n,w) for n,w in SBL_FILES.items()};it={n:git_blob(ias,IAS_COMMIT,n,w) for n,w in IAS_FILES.items()}
 require(src[next(n for n in src if n.endswith("IasImage.c"))],b"CopyMem (&Key.PubKeyMod, ((UINT8 *) IAS_PUBLIC_KEY (Hdr)), sizeof (Key.PubKeyMod));",b"COMP_TYPE_PUBKEY_OS")
 require(src[next(n for n in src if n.endswith("SecureBootRsa.c"))],b"Status = DoHashVerify ((CONST UINT8 *)PubKeyBuf, RSA_MOD_SIZE + RSA_E_SIZE, ComponentType);",b"Status = RsaVerify ((RSA_PUB_KEY *)PubKey, Signature")
 require(src[next(n for n in src if n.endswith("SecureBootHash.c"))],b"Status = GetComponentHash (ComponentType, &PubKeyHash);",b"if (CompareMem (PubKeyHash, (VOID *)Digest, SHA256_DIGEST_SIZE))")
 require(src[next(n for n in src if n.endswith("PayloadLib.c"))],b"GetNextGuidHob (&gPayloadKeyHashGuid, GetHobList())",b"PayloadKeyHash->KeyHash[Index].ComponentType == ComponentType")
 require(it["README.md"],b"binary file format understood by bootloaders",b"iasimage create -o iasImage -i 0x30300 -d priv_key.pem")
 auth_ranges={n:{"file_start":a,"file_end":z,"runtime_start":0xe0000+a,"runtime_end":0xe0000+z,"sha256":w} for n,(a,z,w) in ranges.items()}
 return {"schema":SCHEMA,"tool":{"name":"abl-ias-key-trust","version":VERSION},"exact_update":{"archive":{"size":UPDATE_SIZE,"sha256":UPDATE_SHA},"abl":{"member":ABL_MEMBER,"size":len(abl),"sha256":ABL_SHA,"build":"rel.1714-HF3 / release/GP1.0.1_LGE","primary_bpdt_descriptor_count":13,"ibb_cpd_entries":[{"name":n,"offset":o,"size":z} for n,o,z in cpd],"ibb_subimages":{"stored_sizes":list(sizes),"decompressed_sizes":[len(x) for x in dec],"decompressed_sha256":dh},"decompressed_stage":{"load_base":0xe0000,"size":len(stage),"sha256":dh[0],"auth_ranges":auth_ranges,"auth_direct_call_file_offsets":calls,"hash_selector_immediates":[{"file_offset":o,"value":v} for o,v in selectors.items()],"type3_os_auth":{"selector":0x27,"branch_file_start":0xc1e4,"branch_file_end":0xc20c,"branch_sha256":"6e9002a872ebe1bbbb99b2671c0099ae01e782f679260716d7e51e0476e82414"},"key_check":{"signed_flag_required":True,"runtime_descriptor_type":0x0b,"record_size":0x44,"expected_digest_offset":0x24,"digest_size":32,"carried_key_hash_input":"reverse(stored 256-byte modulus) || stored 4-byte exponent","digest_compared_before_rsa":True,"mismatch_returns_failure":True}},"literal_offsets":{"ipk.":all_offsets(abl,b"ipk."),"iasImage":all_offsets(abl,b"iasImage"),"oemkm":all_offsets(abl,b"oemkm")},"candidate_os_key_hash_present_verbatim":abl.find(candidate)>=0,"candidate_os_key_hash_present_in_decompressed_stages":any(candidate in x for x in dec)}},"stock_constructor":{"member":APP_MEMBER,"size":len(app),"sha256":APP_SHA,"build_id":APP_BUILD,"supplied_key_signature_check_before_embedding":True,"external_boot_key_pin_proved":False},"package_key":{"containers":12,"modulus_sha256":MOD_HASH,"exponent":65537,"exact_abl_hash_input":"reverse(stored_modulus) || stored_little_endian_exponent","public_sbl_hash_input":"reverse(stored_modulus) || stored_little_endian_exponent","candidate_digest":candidate.hex()},"public_intel":{"iasimage":{"commit":IAS_COMMIT,"files":IAS_FILES,"format_match":{"magic":"ipk.","signed_type":"0x30300","signature_size":256,"public_key_size":260}},"slim_bootloader":{"commit":SBL_COMMIT,"files":SBL_FILES,"platform":"Apollo Lake IAS public source","embedded_key_extracted":True,"embedded_key_digest_checked_first":True,"component_type":"COMP_TYPE_PUBKEY_OS (6)","digest_source":"gPayloadKeyHashGuid HOB component entry","payload_signature_checked_after_key_digest":True}},"conclusions":{"package_signature_is_not_merely_unkeyed_hash":True,"public_sbl_pins_embedded_os_key_digest":True,"exact_target_abl_key_pin_proved":True,"exact_target_abl_type3_path_uses_pinned_key_check":True,"exact_target_expected_digest_storage_identity_proved":False,"exact_target_abl_accepts_arbitrary_embedded_key_proved":False,"custom_signed_image_acceptance_proved":False,"boot_acceptance_root_or_persistence_proved":False},"limitations":["Exact decompressed rel.1714 code proves a 32-byte carried-key digest comparison before RSA verification, including the type-3 OS path; it does not yet identify the persistent source object that populates the runtime descriptor/hash table.","The candidate digest is not present verbatim in stored flash or the three decompressed IBB stages; manifest, CSE/HOB delivery, transformed storage, or another authenticated source remains possible.","Normal-versus-_sub selection, attempts, health, mark-good, rollback, and recovery remain unresolved.","No firmware, bootloader, constructor, updater, image, flash operation, or boot attempt was executed."]}
def encode(x):return (json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False,separators=(",",": "))+"\n").encode()
def exclusive(p,b):
 try:fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,"O_CLOEXEC",0),0o600)
 except OSError as e:raise Failure(f"cannot create output exclusively: {e}") from e
 try:
  n=0
  while n<len(b):
   z=os.write(fd,b[n:])
   if z<=0:raise Failure("short output write")
   n+=z
 finally:os.close(fd)
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--update-archive",type=Path,required=True);p.add_argument("--rootfs",type=Path,required=True);p.add_argument("--boot-dir",type=Path,required=True);p.add_argument("--sbl-repo",type=Path,required=True);p.add_argument("--iasimage-repo",type=Path,required=True);p.add_argument("-o","--output",type=Path);a=p.parse_args(argv)
 try:b=encode(analyze(a.update_archive,a.rootfs,a.boot_dir,a.sbl_repo,a.iasimage_repo));exclusive(a.output,b) if a.output else sys.stdout.buffer.write(b)
 except Failure as e:print(f"error: {e}",file=sys.stderr);return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
