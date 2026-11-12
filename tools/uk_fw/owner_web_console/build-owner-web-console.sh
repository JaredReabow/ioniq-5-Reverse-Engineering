#!/bin/sh
# Reproduce the reviewed linux/amd64 owner web console without installing
# target libraries. Go 1.26.11 is pinned for the reviewed artifact and size.
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/../../.." && pwd)
output_dir="$repo_root/work/owner-web-build/bin"
output="$output_dir/owner-web-console-v1.0.2"
expected=18c6ac2eb0f5e3d92661bcf979f447e6bd211ab7541bc83847f5efb26c8e807b

if [ "$#" -ne 0 ]; then
    echo "usage: $0" >&2
    exit 2
fi
mkdir -p "$output_dir"

cd "$script_dir"
GOTOOLCHAIN=go1.26.11 \
CGO_ENABLED=0 \
GOOS=linux \
GOARCH=amd64 \
GOAMD64=v1 \
go build \
    -tags=nethttpomithttp2 \
    -trimpath \
    -buildvcs=false \
    -ldflags='-s -w' \
    -o "$output" \
    .

actual=$(python3 - "$output" <<'PY'
import hashlib
import pathlib
import sys

data = pathlib.Path(sys.argv[1]).read_bytes()
print(hashlib.sha256(data).hexdigest())
PY
)
if [ "$actual" != "$expected" ]; then
    echo "owner web console digest mismatch: $actual" >&2
    exit 1
fi

printf 'IONIQ5_OWNER_WEB_BINARY=%s\n' "$output"
printf 'IONIQ5_OWNER_WEB_SHA256=%s\n' "$actual"
python3 - "$output" <<'PY'
import gzip
import lzma
import pathlib
import sys

data = pathlib.Path(sys.argv[1]).read_bytes()
print(f"raw={len(data)}")
print(f"gzip9={len(gzip.compress(data, compresslevel=9, mtime=0))}")
print(f"xz9={len(lzma.compress(data, format=lzma.FORMAT_XZ, preset=9))}")
PY
