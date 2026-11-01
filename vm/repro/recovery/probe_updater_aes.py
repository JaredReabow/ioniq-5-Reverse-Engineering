#!/usr/bin/env python3
"""One-build, offline experiment. No app execution, API requests, or raw key output.

Reconstruct two constant key/IV pairs from the inspected updater's static
instructions. Test only CBC payload-start hypotheses at offsets 0..16384.
The updater constants are NOT established head-unit firmware keys.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

UPDATER_SHA256 = '7b63734d60ca42648e81fcf12a9518c46077859554c050e2134dc27120e0f37c'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def macho_reader(raw):
    if raw[:4] != b'\xcf\xfa\xed\xfe':
        raise ValueError('expected thin little-endian Mach-O 64')
    segments = []
    at = 32
    count = struct.unpack_from('<I', raw, 16)[0]
    for _ in range(count):
        cmd, size = struct.unpack_from('<II', raw, at)
        if size < 8 or at + size > len(raw):
            raise ValueError('invalid load command')
        if cmd == 0x19:
            vm, vm_size, off, file_size = struct.unpack_from('<4Q', raw, at + 24)
            segments.append((vm, off, file_size))
        at += size

    def read(address, length):
        matches = [(off + address - vm) for vm, off, size in segments
                   if vm <= address and address + length <= vm + size]
        if len(matches) != 1:
            raise ValueError('no unique file-backed address mapping')
        data = raw[matches[0]:matches[0] + length]
        if len(data) != length:
            raise ValueError('truncated mapped data')
        return data
    return read


def candidate_pairs(raw):
    if digest(raw) != UPDATER_SHA256:
        raise ValueError('updater build mismatch; do not reuse address/index assumptions')
    read = macho_reader(raw)
    # decryptAsUpdate's two sprintf sites: 0x10026d3d0 and 0x10026d462.
    # First four variadic bytes are edx/ecx/r8d/r9d; remaining bytes are
    # successive 8-byte stack argument slots. The output strings are copied
    # into byte vectors unchanged (not hex-decoded) before TinyAES256 CBC.
    if read(0x103f4e962, 65) != b'%c' * 32 + b'\0':
        raise ValueError('unexpected key sprintf format')
    if read(0x103f4e9a3, 33) != b'%c' * 16 + b'\0':
        raise ValueError('unexpected IV sprintf format')
    a = read(0x103f71330, 27)
    b = read(0x103f7134b, 11)
    key = bytes([b[5], b[2], a[1], a[0], b[1], a[2], b[9], a[5],
                 a[1], a[1], a[1], a[0], b[6], b[4], a[3], b[5],
                 a[2], b[0], b[6], b[9], b[4], b[3], b[6], a[2],
                 b[0], b[7], a[2], b[9], a[4], b[7], b[4], a[3]])
    iv = bytes([a[2], b[6], a[0], b[5], a[0], b[0], a[2], b[9],
                a[5], b[5], b[9], a[5], b[1], a[0], b[6], b[9]])
    # Global constructor at 0x1001a2b31..0x1001a2bd0 copies two 32-char
    # constants. toEncrypt calls TinyAES::from_hex_string on each at
    # 0x10026cc8a / 0x10026ccdc before its AES-128 CBC branch.
    auth_key = bytes.fromhex(read(0x103f409f8, 32).decode('ascii'))
    auth_iv = bytes.fromhex(read(0x103f409d7, 32).decode('ascii'))
    assert len(key) == 32 and len(iv) == len(auth_key) == len(auth_iv) == 16
    return [('updater-text-aes256', key, iv), ('updater-auth-aes128', auth_key, auth_iv)]


def decrypt(key, iv, data):
    context = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    return context.update(data) + context.finalize()


def markers(data):
    result = []
    for name, prefix in [('ipk', b'ipk.'), ('ELF', b'\x7fELF'),
                         ('gzip', b'\x1f\x8b\x08'), ('XML', b'<?xml')]:
        if data.startswith(prefix):
            result.append(name + '-prefix-only')
    if len(data) >= 512 and data[257:262] == b'ustar':
        try:
            checksum = int(data[148:156].strip(b'\x00 '), 8)
            if checksum == sum(data[:148]) + 8 * 32 + sum(data[156:512]):
                result.append('checksum-valid-ustar-header')
        except ValueError:
            pass
    return result


def probe_sample(data, pairs, last_offset=16384):
    hits = []
    attempts = 0
    for name, key, original_iv in pairs:
        for offset in range(min(last_offset, len(data) - 512) + 1):
            block = decrypt(key, b'\x00' * 16, data[offset:offset + 512])
            # CBC IV affects only the first plaintext block. The remainder
            # can be tested once; each explicit IV hypothesis changes only it.
            ivs = {'zero': b'\x00' * 16, 'updater-constant': original_iv,
                   'file-first-block': data[:16]}
            if offset >= 16:
                ivs['preceding-block'] = data[offset - 16:offset]
            attempts += len(ivs)
            for label, iv in ivs.items():
                plain = bytes(x ^ y for x, y in zip(block[:16], iv)) + block[16:]
                found = markers(plain)
                if found:
                    hits.append({'key_label': name, 'offset': offset, 'iv_hypothesis': label,
                                 'markers': found, 'sample_sha256': digest(plain)})
    return {'hypotheses': attempts, 'hits': hits}


def controls():
    # Independent NIST SP 800-38A AES-128-CBC single-block known-answer vector.
    key = bytes.fromhex('2b7e151628aed2a6abf7158809cf4f3c')
    iv = bytes.fromhex('000102030405060708090a0b0c0d0e0f')
    cipher = bytes.fromhex('7649abac8119b246cee98e9b12e9197d')
    plain = bytes.fromhex('6bc1bee22e409f96e93d7e117393172a')
    assert decrypt(key, iv, cipher) == plain
    # Exercise the actual scanning path at an unaligned offset with a
    # prepended IV and a deliberately different constant-IV hypothesis.
    sample = b'<?xml version="1.0"?>' + b' ' * (512 - 21)
    assert len(sample) == 512
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    encoded = encryptor.update(sample) + encryptor.finalize()
    report = probe_sample(b'x' * 7 + iv + encoded, [('control', key, b'\xff' * 16)], 23)
    assert any(h['offset'] == 23 and h['iv_hypothesis'] == 'preceding-block' for h in report['hits'])
    return ['NIST AES128-CBC KAT passed', 'unaligned XML/preceding-IV scan control passed']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--updater', type=Path, required=True)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output already exists')
    tested_controls = controls()
    raw = args.updater.read_bytes()
    pairs = candidate_pairs(raw)
    inventory = json.loads(args.inventory.read_text())
    files = []
    for package in inventory:
        for item in package['files']:
            if item['classification'] != 'opaque/unclassified' or not item['size'] or '/frontkey/' in item['path']:
                continue
            path = Path(package['root']) / item['path']
            if path.stat().st_size != item['size']:
                raise ValueError('inventory size mismatch')
            with path.open('rb') as stream:
                data = stream.read(16384 + 512)
            if data[:16].hex() != item['head_hex']:
                raise ValueError('inventory prefix mismatch')
            result = probe_sample(data, pairs)
            files.append({'path': str(path), 'size': item['size'], 'sample_length': len(data),
                          'sample_sha256': digest(data), **result})
    report = {
        'updater_sha256': digest(raw), 'controls': tested_controls,
        'key_candidates': [{'label': name, 'key_bytes': len(key), 'key_sha256': digest(key),
                            'iv_sha256': digest(iv)} for name, key, iv in pairs],
        'offset_range_inclusive': [0, 16384], 'plaintext_sample_bytes': 512,
        'files': files,
        'summary': {'files': len(files), 'hypotheses': sum(f['hypotheses'] for f in files),
                    'marker_hits': sum(len(f['hits']) for f in files)},
        'limitations': [
            'Static reconstruction, not execution of the vendor updater crypto code.',
            'Only two observed constant pairs; other updater modes and derivations remain untested.',
            'Only CBC starts within the first 16385 bytes and four explicit IV hypotheses.',
            'Only ipk/ELF/gzip/XML prefixes and checksum-valid ustar headers were recognized.',
            'No hit is not proof against other keys, IVs, modes, encodings, offsets, or plaintext formats.',
        ],
    }
    with args.output.open('x') as out:
        json.dump(report, out, indent=2)
        out.write('\n')
    print(json.dumps(report['summary']))


if __name__ == '__main__':
    main()
