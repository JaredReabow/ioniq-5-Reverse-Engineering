#!/bin/sh
# Cross-build the SocketCAN shim for the Gen5W guest. No host paths are recorded: -g0 plus
# prefix maps, and any remaining build root in the artefact is overwritten with dots.
set -e
cd "$(dirname "$0")/../../.."
ZIG=${ZIG:-work/toolchains/zig-macos-aarch64-0.13.0/zig}
OUT=${OUT:-tools/uk_fw/can_shim/can_shim.so}
"$ZIG" cc -target x86_64-linux-gnu -O1 -g0 -shared -fPIC \
  -ffile-prefix-map="$PWD"=. -fdebug-prefix-map="$PWD"=. \
  -o "$OUT" tools/uk_fw/can_shim/can_shim.c -lpthread
python3 - "$OUT" "$PWD" <<'PYEOF'
import sys
path, root = sys.argv[1], sys.argv[2].encode()
d = open(path, 'rb').read()
if root in d:
    open(path, 'wb').write(d.replace(root, b'.' * len(root)))
    print(f"  sanitised {path}")
PYEOF
file "$OUT" | cut -c1-100
