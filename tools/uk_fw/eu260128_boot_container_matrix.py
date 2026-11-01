#!/usr/bin/env python3
"""Verify the complete EU 260128 iasImage filename and signature matrix."""
from __future__ import annotations
import argparse,hashlib,json,os,stat,struct,subprocess,sys
from pathlib import Path
SCHEMA="eu260128-boot-container-matrix/v1";VERSION="1.0.0";META=0x4024;KEY=bytes.fromhex("60a93d70f73302a63e5ed0d0ea38be22");MAX=7_000_000
MOD_HASH="227d89f5a3cabed4efb8e67d5a0f9fa29d03a6759b8a150503fb383698fedea6"
DI_PREFIX=bytes.fromhex("3031300d060960864801650304020105000420")
FILES={
"iasImage":(6226728,"6db0bb746722389092e60681554a3b9f1b391f8def59c65c68e764cc9d6007ce","ef1820da4cf51f65abcb26e794d553661e79ad6bb095ad1cf4b0366982927d97",True,"/dev/mmcblk0p3",False),
"iasImage_1280":(6226728,"c2a314bc63e1dbe1440bd87b9135210b6eea356727ba03bdecb692b61d3bce4e","fcf18006a30b29b70ee64899177586f124b4eb1688234be83aa9baf50f89edcb",True,"/dev/mmcblk0p3",False),
"iasImage_1280_sub":(6210308,"55e9a31be5ca734a7af111613ae6ce83cdc579b27138c5f54700f78263056eb0","55e9a31be5ca734a7af111613ae6ce83cdc579b27138c5f54700f78263056eb0",False,"/dev/mmcblk0p3",True),
"iasImage_1920_12":(6226728,"aaa0384e4f147ec016f019f839a06a7ed19f3a407d8b0d23070c97c8c459e0dd","2113632569fbd8598546c664d7007e8bda07b409b86813ad6520745fc8e94e4b",True,"/dev/mmcblk0p3",False),
"iasImage_1920_12_sub":(6210308,"e4d7523ba0f77a7b659260df82968d515859b01e06738bf7cfd79bef83db8e05","e4d7523ba0f77a7b659260df82968d515859b01e06738bf7cfd79bef83db8e05",False,"/dev/mmcblk0p5",True),
"iasImage_p5":(6226728,"57ea6691a1118020bc263c1fbdba3d7e26dd0240f4c89fac380c5578708376b0","2b9fc7ce7c3c7573f3550a3afc592a2896ad15bdf02b82bcf86c0fef8d9fbd91",True,"/dev/mmcblk0p5",False),
"iasImage_p5_1280":(6226728,"7e8fd8c426c64eec197462aed53290c63e1a12aea43a5556f45acd2c90da3476","50215cb2db4255e6e2e7c2916976d36624d6dec434d8b7d978b7b4edce1e369c",True,"/dev/mmcblk0p5",False),
"iasImage_p5_1280_sub":(6210308,"fb442a993619b17c94c95826cc425a6e04c3e947c1f9c009191dec63607acbad","fb442a993619b17c94c95826cc425a6e04c3e947c1f9c009191dec63607acbad",False,"/dev/mmcblk0p5",True),
"iasImage_p5_1920_12":(6226728,"7d3c4c43cee76c45518f85df2ac07cb124a7984d238d7189e6ead9e4967500f3","cc80a5a364f2c8e24fc6ad5bdc7d7f6e732715b76658664fd3bcf90e203c3b40",True,"/dev/mmcblk0p5",False),
"iasImage_p5_1920_12_sub":(6210308,"e4d7523ba0f77a7b659260df82968d515859b01e06738bf7cfd79bef83db8e05","e4d7523ba0f77a7b659260df82968d515859b01e06738bf7cfd79bef83db8e05",False,"/dev/mmcblk0p5",True),
"iasImage_p5_sub":(6210308,"47a6f19f395529814be3eeb7a5751815fab8d31b36fdc503ef025e65070a484f","47a6f19f395529814be3eeb7a5751815fab8d31b36fdc503ef025e65070a484f",False,"/dev/mmcblk0p5",True),
"iasImage_sub":(6210308,"deb69570c89a37f15a92a2e07247138ab0ed83ea108141f24536db6f0f9bbc7f","deb69570c89a37f15a92a2e07247138ab0ed83ea108141f24536db6f0f9bbc7f",False,"/dev/mmcblk0p3",True),
}
class Failure(Exception):pass
def stable_read(p:Path)->bytes:
 flags=os.O_RDONLY|getattr(os,"O_CLOEXEC",0)|getattr(os,"O_NOFOLLOW",0)
 try:fd=os.open(p,flags)
 except OSError as e:raise Failure(f"cannot safely open {p.name}: {e}") from e
 try:
  a=os.fstat(fd)
  if not stat.S_ISREG(a.st_mode) or a.st_size>MAX:raise Failure(f"unbounded input: {p.name}")
  out=[];n=a.st_size
  while n:
   c=os.read(fd,min(n,1<<20))
   if not c:raise Failure(f"short read: {p.name}")
   out.append(c);n-=len(c)
  if os.read(fd,1):raise Failure(f"input grew: {p.name}")
  z=os.fstat(fd);ident=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
  if ident(a)!=ident(z):raise Failure(f"input changed: {p.name}")
  return b"".join(out)
 finally:os.close(fd)
def iv_for(name:str,n:int)->bytes:
 signed=n if n<1<<31 else n-(1<<32)
 return hashlib.sha256(f"{name}{signed}".encode()).digest()[:16]
def decrypt_te2(name:str,raw:bytes)->tuple[bytes,dict]:
 if len(raw)<=META:raise Failure(f"short TE2 envelope: {name}")
 body,meta=raw[:-META],raw[-META:];iv=iv_for(name,len(body))
 if meta[:3]!=b"TE2":raise Failure(f"TE2 magic drift: {name}")
 if meta[4:36]!=hashlib.sha256(iv+meta[36:]).digest():raise Failure(f"TE2 metadata integrity failure: {name}")
 padlen=(-len(body))%16;ciphertext=body+meta[36:36+padlen]
 try:
  from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
 except ImportError as e:raise Failure("cryptography package unavailable") from e
 dec=Cipher(algorithms.AES(KEY),modes.CBC(iv)).decryptor();plain=(dec.update(ciphertext)+dec.finalize())[:len(body)]
 return plain,{"metadata_discriminator":meta[3],"iv":iv.hex(),"metadata_integrity":True,"body_size":len(body)}
def u32(b,o):return struct.unpack_from("<I",b,o)[0]
def parse_ipk(name:str,b:bytes,root:str,console:bool)->dict:
 if len(b)!=6210308 or b[:4]!=b"ipk.":raise Failure(f"ipk identity drift: {name}")
 version,reserved,total,hdr,dup,bid,clen=struct.unpack_from("<7I",b,4)
 if (version,reserved,total,hdr,dup,bid)!=(0x30300,0,0x5ebfcc,0x34,0x5ebfcc,0x42f08d94):raise Failure(f"ipk header drift: {name}")
 if not 1<=clen<=4096 or hdr+clen>len(b):raise Failure(f"command line bounds: {name}")
 field=b[hdr:hdr+clen];nul=field.find(b"\0")
 if nul<0:raise Failure(f"unterminated command line: {name}")
 try:cmd=field[:nul].decode("ascii","strict")
 except UnicodeDecodeError as e:raise Failure(f"non-ASCII command line: {name}") from e
 token=f"root={root}"
 if token not in cmd or ("console=ttyS2,115200n8" in cmd)!=console:raise Failure(f"command line contract drift: {name}")
 base=hdr+total
 if base+0x304!=len(b):raise Failure(f"trailer bounds drift: {name}")
 if b[base+4:base+0x100]!=b"\xff"*252:raise Failure(f"signature padding drift: {name}")
 sig=b[base+0x100:base+0x200];mod=b[base+0x200:base+0x300];exp=u32(b,base+0x300)
 if exp!=65537 or hashlib.sha256(mod).hexdigest()!=MOD_HASH:raise Failure(f"embedded key drift: {name}")
 digest=hashlib.sha256(b[:base+4]).digest();em=pow(int.from_bytes(sig,"big"),exp,int.from_bytes(mod,"big")).to_bytes(256,"big")
 sep=em.find(b"\0",2)
 if not em.startswith(b"\0\1") or sep<10 or em[2:sep]!=b"\xff"*(sep-2) or em[sep+1:]!=DI_PREFIX+digest:raise Failure(f"RSA signature failure: {name}")
 lz4off=b.find(b"\x02\x21\x4c\x18")
 if lz4off<0:raise Failure(f"legacy LZ4 stream absent: {name}")
 try:proc=subprocess.run(["lz4","-d","-c"],input=b[lz4off:],stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,check=False)
 except (OSError,subprocess.TimeoutExpired) as e:raise Failure(f"host lz4 unavailable or timed out: {e}") from e
 # The stream is followed by signed-container trailer bytes, so stock lz4 may
 # return nonzero after emitting the complete frame. Bind the emitted bytes.
 if len(proc.stdout)!=16398376 or hashlib.sha256(proc.stdout).hexdigest()!="f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b":raise Failure(f"decompressed kernel identity mismatch: {name}")
 return {"ipk_size":len(b),"version":version,"total_field":total,"header_size":hdr,"build_id":bid,"command_line_length":clen,"root_target":root,"serial_console":console,"signed_end":base+4,"signed_sha256":digest.hex(),"signature":"RSA-2048 PKCS#1 v1.5 SHA-256","modulus_sha256":MOD_HASH,"legacy_lz4_offset":lz4off,"decompressed_kernel_size":len(proc.stdout),"decompressed_kernel_sha256":"f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b"}
def analyze(d:Path)->dict:
 try:entries=list(os.scandir(d))
 except OSError as e:raise Failure(f"cannot scan input directory: {e}") from e
 names={x.name for x in entries}
 if names!=set(FILES):raise Failure(f"input filename set mismatch: missing={sorted(set(FILES)-names)}, extra={sorted(names-set(FILES))}")
 rows=[]
 for name in sorted(FILES):
  size,enc_hash,plain_hash,wrapped,root,console=FILES[name];raw=stable_read(d/name)
  if len(raw)!=size or hashlib.sha256(raw).hexdigest()!=enc_hash:raise Failure(f"source identity mismatch: {name}")
  if wrapped:plain,te2=decrypt_te2(name,raw)
  else:plain,te2=raw,None
  if hashlib.sha256(plain).hexdigest()!=plain_hash:raise Failure(f"plaintext identity mismatch: {name}")
  ipk=parse_ipk(name,plain,root,console)
  rows.append({"name":name,"source_size":size,"source_sha256":enc_hash,"te2_wrapped":wrapped,"te2":te2,"plaintext_sha256":plain_hash,"ipk":ipk})
 return {"schema":SCHEMA,"tool":{"name":"eu260128-boot-container-matrix","version":VERSION},"package":{"filenames":12,"te2_wrapped":6,"already_plaintext":6,"common_plaintext_size":6210308,"common_modulus_sha256":MOD_HASH,"common_decompressed_kernel_sha256":"f5ee9c2f97eed44f9827153c273125bf131a9ca9a96c63bb6e93cfc5af6b102b"},"rows":rows,"conclusions":{"all_appfumo_selected_filenames_present":True,"all_embedded_signatures_verify":True,"all_share_one_embedded_modulus":True,"normal_variants_te2_wrapped":True,"sub_variants_already_plaintext":True,"all_twelve_decompress_to_recovered_vmlinux":True,"bootloader_pins_embedded_modulus":None,"persistent_activation_or_boot_acceptance_proved":False,"custom_image_acceptance_proved":False,"root_or_persistence_proved":False},"limitations":["The report verifies package bytes and embedded signatures, not that MICOM or ABL accepts the embedded modulus.","Presence and signature validity do not prove updater invocation, final written bytes, durability, boot selection, health, mark-good, rollback, root, or persistence.","No modified or re-signed container is created by this analyzer."]}
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
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("directory",type=Path);p.add_argument("-o","--output",type=Path);a=p.parse_args(argv)
 try:
  b=encode(analyze(a.directory));write_exclusive(a.output,b) if a.output else sys.stdout.buffer.write(b)
 except Failure as e:print(f"error: {e}",file=sys.stderr);return 2
 return 0
if __name__=="__main__":raise SystemExit(main())
