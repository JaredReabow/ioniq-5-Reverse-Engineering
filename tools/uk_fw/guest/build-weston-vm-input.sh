#!/bin/sh
# Cross-build the projection's input injector for the Gen5W guest.
#
# The module is deliberately self-contained: it declares the weston and wayland
# externs it needs and pins two struct offsets recovered from the vendor binary's
# DWARF, so it needs no weston headers and no vendor sources.
#
# No host paths are recorded: -g0 plus prefix maps, and any surviving build root in
# the artefact is overwritten with dots (the same treatment as the other builders).
set -e
cd "$(dirname "$0")/../../.."
ZIG=${ZIG:-work/toolchains/zig-macos-aarch64-0.13.0/zig}
OUT=${OUT:-tools/uk_fw/guest/weston-vm-input.so}

"$ZIG" cc -target x86_64-linux-gnu -O1 -g0 -shared -fPIC \
  -ffile-prefix-map="$PWD"=. -fdebug-prefix-map="$PWD"=. \
  -o "$OUT" tools/uk_fw/guest/weston_vm_input.c

python3 - "$OUT" "$PWD" <<'PYEOF'
import sys
path, root = sys.argv[1], sys.argv[2].encode()
d = open(path, 'rb').read()
if root in d:
    open(path, 'wb').write(d.replace(root, b'.' * len(root)))
    print(f"  sanitised {path}")
PYEOF
file "$OUT" | cut -c1-100
