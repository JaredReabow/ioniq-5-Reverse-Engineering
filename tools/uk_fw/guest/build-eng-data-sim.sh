#!/bin/sh
# Cross-build the engineering-mode data-service simulator for the Gen5W guest.
# Links dynamically against the guest's own libdbus-1.so.3 (extracted from the
# EU 260128 rootfs), so the resulting binary runs unchanged inside the VM.
set -e
cd "$(dirname "$0")/../../.."
ZIG=${ZIG:-work/toolchains/zig-macos-aarch64-0.13.0/zig}
# The dbus headers are a build-host dependency, not something the guest image ships,
# so they are supplied by the caller and never hardcoded here (no host paths in the repo).
#   DBUS_INC=/path/to/dbus-1.0 DBUS_ARCH_INC=/path/to/dbus-1.0/include sh build-eng-data-sim.sh
# Fall back to pkg-config (no host path is written into this file).
if [ -z "$DBUS_INC" ] && command -v pkg-config >/dev/null 2>&1; then
    DBUS_INC=$(pkg-config --cflags-only-I dbus-1 2>/dev/null | tr ' ' '\n' | sed -n 's/^-I//p' | head -1)
    DBUS_ARCH_INC=$(pkg-config --cflags-only-I dbus-1 2>/dev/null | tr ' ' '\n' | sed -n 's/^-I//p' | tail -1)
fi
if [ -z "$DBUS_INC" ] || [ -z "$DBUS_ARCH_INC" ]; then
    echo "build-eng-data-sim.sh: set DBUS_INC and DBUS_ARCH_INC to the dbus-1.0 headers" >&2
    echo "  e.g. DBUS_INC=/usr/include/dbus-1.0 DBUS_ARCH_INC=/usr/lib/dbus-1.0/include" >&2
    exit 2
fi
GUEST_LIBDBUS=${GUEST_LIBDBUS:-work/decrypted-eu-260128/extracted-safe/mango-rootfs/usr/lib/libdbus-1.so.3}
SRC=tools/uk_fw/guest/eng_data_sim.c
OUT=${OUT:-tools/uk_fw/guest/eng-data-sim}

"$ZIG" cc -target x86_64-linux-gnu -O1 -g0 \
  -ffile-prefix-map="$PWD"=. -fdebug-prefix-map="$PWD"=. \
  -I "$DBUS_INC" -I "$DBUS_ARCH_INC" \
  -o "$OUT" "$SRC" "$GUEST_LIBDBUS"

file "$OUT" | cut -c1-100

# Sanitise the artefact: the compiler still records the build root in a few diagnostic
# strings. Overwrite any occurrence of it with dots so the binary carries no host path.
# Length is preserved, and these strings are unused at run time.
python3 - "$OUT" "$PWD" <<'PYEOF'
import sys
path, root = sys.argv[1], sys.argv[2].encode()
data = open(path, 'rb').read()
if root in data:
    data = data.replace(root, b'.' * len(root))
    open(path, 'wb').write(data)
    print(f"  sanitised {path}: build root replaced with dots")
PYEOF
