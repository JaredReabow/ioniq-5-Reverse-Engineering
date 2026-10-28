#!/usr/bin/env python3
"""Recheck retained gzip-prefix hits without executing the updater."""
import argparse
import gzip
import json
import zlib
from pathlib import Path

import probe_updater_aes as probe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--updater', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output already exists')
    pairs = {name: (key, iv) for name, key, iv in probe.candidate_pairs(args.updater.read_bytes())}
    report = json.loads(args.report.read_text())
    rows = []
    for item in report['files']:
        for hit in item['hits']:
            key, unused_iv = pairs[hit['key_label']]
            if hit['iv_hypothesis'] != 'file-first-block' or hit['markers'] != ['gzip-prefix-only']:
                raise ValueError('unexpected candidate; needs a separate validation procedure')
            with Path(item['path']).open('rb') as stream:
                first = stream.read(16)
                stream.seek(hit['offset'])
                data = stream.read(512)
            plain = probe.decrypt(key, first, data)
            if probe.digest(plain) != hit['sample_sha256']:
                raise ValueError('candidate hash mismatch')
            decoder = zlib.decompressobj(31)
            try:
                output = decoder.decompress(plain, 65536)
                validation = {'zlib_status': 'prefix-accepted', 'output_bytes': len(output), 'eof': decoder.eof}
            except zlib.error as exc:
                validation = {'zlib_status': 'rejected', 'reason': str(exc)}
            rows.append({'path': item['path'], **hit, 'gzip_flags': plain[3],
                         'gzip_reserved_flags_set': bool(plain[3] & 0xe0), **validation})
    control = b'positive gzip validation control\n' * 40
    assert zlib.decompress(gzip.compress(control, mtime=0), 31) == control
    result = {'controls': ['synthetic gzip decompression/bytes-equality passed'], 'candidates': rows,
              'validated_payloads': 0 if all(r['zlib_status'] == 'rejected' for r in rows) else None}
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    main()
