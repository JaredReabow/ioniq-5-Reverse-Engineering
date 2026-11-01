#!/usr/bin/env python3
"""Bounded, read-only signature survey of existing local package resources.
Not decryption or proof that other encodings/recovery routes do not exist.
"""
from pathlib import Path
import gzip
import hashlib
import json
import struct
import time
import zipfile
import zlib

OUT = Path(__file__).resolve().parent / 'local-only'
CHUNK = 16 * 1024 * 1024


def classify_elf(stream, offset, size):
    stream.seek(offset)
    h = stream.read(64)
    if len(h) < 64 or h[:7] != b'\x7fELF\x02\x01\x01':
        return None
    typ, machine, version = struct.unpack_from('<HHI', h, 16)
    phoff = struct.unpack_from('<Q', h, 32)[0]
    ehsize, phsize, phnum = struct.unpack_from('<HHH', h, 52)
    if typ not in (2, 3) or machine != 62 or version != 1 or ehsize != 64:
        return None
    if phsize != 56 or not 1 <= phnum <= 256 or not 64 <= phoff <= 1024**2:
        return None
    if offset + phoff + phsize * phnum > size:
        return None
    stream.seek(offset + phoff)
    table = stream.read(phsize * phnum)
    loads = []
    for i in range(phnum):
        kind, flags, p_off, va, pa, filesz, memsz, align = struct.unpack_from('<IIQQQQQQ',table,i*56)
        if kind == 1:
            if filesz > memsz or offset + p_off + filesz > size:
                return None
            loads.append({'offset':p_off,'filesz':filesz,'memsz':memsz,'flags':flags})
    return {'type':typ,'machine':machine,'load_segments':loads} if loads else None


def survey(path):
    start = time.monotonic(); size=path.stat().st_size
    seen={key:set() for key in ('elf','gzip','ustar')}
    candidates=[]; digest=hashlib.sha256(); position=0; tail=b''
    with path.open('rb') as source, path.open('rb') as probe:
        while chunk:=source.read(CHUNK):
            digest.update(chunk)
            data=tail+chunk; base=position-len(tail)
            for name,magic in (('elf',b'\x7fELF'),('gzip',b'\x1f\x8b\x08'),('ustar',b'ustar')):
                cursor=0
                while (at:=data.find(magic,cursor))>=0:
                    cursor=at+1; offset=base+at
                    if offset in seen[name]: continue
                    seen[name].add(offset)
                    if name=='elf':
                        info=classify_elf(probe,offset,size)
                        if info: candidates.append({'kind':'validated_x86_64_ELF_headers','offset':offset,**info})
                    elif name=='ustar' and offset>=257:
                        probe.seek(offset-257); header=probe.read(512)
                        if len(header)!=512: continue
                        try: checksum=int(header[148:156].strip(b' \0'),8)
                        except ValueError: continue
                        if checksum==sum(header[:148])+8*32+sum(header[156:]):
                            candidates.append({'kind':'validated_tar_header_checksum','offset':offset-257})
                    elif name=='gzip':
                        probe.seek(offset); sample=probe.read(65536)
                        if len(sample)<10 or sample[3]&0xe0: continue
                        try:
                            decoder=zlib.decompressobj(16+zlib.MAX_WBITS)
                            decoded=decoder.decompress(sample,65536)
                        except zlib.error:
                            continue
                        if decoder.eof or decoded.startswith(b'\x7fELF') or decoded[257:262]==b'ustar':
                            candidates.append({'kind':'gzip_candidate','offset':offset,
                                               'member_completed_within_64KiB_caps':decoder.eof,
                                               'prefix_sha256':hashlib.sha256(decoded).hexdigest(),
                                               'prefix_length':len(decoded),
                                               'decoded_elf_prefix':decoded.startswith(b'\x7fELF'),
                                               'decoded_tar_prefix':decoded[257:262]==b'ustar'})
            position+=len(chunk); tail=data[-8:]
    return {'path':str(path),'size':size,'bytes_scanned':position,'sha256':digest.hexdigest(),
            'raw_magic_hits':{k:len(v) for k,v in seen.items()},'candidates':candidates,
            'elapsed_seconds':round(time.monotonic()-start,2)}


def main():
    OUT.mkdir(exist_ok=True)
    # Positive controls from an existing binary and a tiny self-created gzip.
    controls=[survey(Path(__file__).resolve().parent/'busybox')]
    fixture=OUT/'scan-positive.xml.gz'
    if not fixture.exists():
        fixture.write_bytes(gzip.compress(b'<diagnostic>local positive control</diagnostic>',mtime=0))
    controls.append(survey(fixture))
    assert any(c['kind']=='validated_x86_64_ELF_headers' for c in controls[0]['candidates'])
    assert any(c['kind']=='gzip_candidate' and c['member_completed_within_64KiB_caps'] for c in controls[1]['candidates'])
    reports=[]; zips=[]
    for root in (Path('/Users/researcher/Downloads/NaU/IONIQ5_EU'),Path('/Users/researcher/Downloads/NaU/2021_22_IONIQ_5_AU')):
        navi='navi_eu' if root.name=='IONIQ5_EU' else 'navi_au'
        for rel in ('AppUpgrade','.lge.upgrade.xml','HU/firmware/update.tar.gz',
                    'HU/images/mango-rootfs.tar.gz','HU/images/new_gui.tar.gz',
                    'HU/images/mango-rwdata.tar.gz',f'HU/images/{navi}/appnavi.tar'):
            row=survey(root/rel); reports.append(row)
            print(root.name,rel,'bytes',row['bytes_scanned'],'candidates',row['candidates'],flush=True)
        for path in (root/'HU/images'/navi).glob('*.zip'):
            headers=[]; candidates=[]
            with zipfile.ZipFile(path) as archive:
                for member in archive.infolist():
                    if member.is_dir(): continue
                    if member.flag_bits&1:
                        headers.append({'path':member.filename,'encrypted':True}); continue
                    with archive.open(member) as f: head=f.read(512)
                    kind=next((name for name,magic in (('ELF',b'\x7fELF'),('PE/DOS',b'MZ'),('gzip',b'\x1f\x8b\x08'),('ZIP',b'PK\x03\x04')) if head.startswith(magic)),None)
                    if head[257:262]==b'ustar': kind='tar'
                    if b'import Qt' in head: kind='QML-like'
                    headers.append({'path':member.filename,'size':member.file_size,'kind':kind,'prefix_sha256':hashlib.sha256(head).hexdigest()})
                    if kind: candidates.append(headers[-1])
            zips.append({'path':str(path),'regular_entries_checked':len(headers),'candidates':candidates,'entries':headers})
            print(root.name,'map entry prefixes',len(headers),'candidates',len(candidates),flush=True)
    report={'scope':'Full-byte magic scan of 14 selected opaque files; structured ELF/tar validation; gzip probes capped at 64KiB compressed and output. ZIP regular-member first 512 bytes only. No recursive extraction, no decryption, no target execution.',
            'controls':controls,'opaque_files':reports,'map_zips':zips}
    (OUT/'deep-local-ui-scan.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Saved',OUT/'deep-local-ui-scan.json')

if __name__=='__main__': main()
