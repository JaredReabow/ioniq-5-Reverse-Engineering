#!/bin/sh
# Cross-build the engineering-mode data-service simulator for the Gen5W guest.
# Links dynamically against the guest's own libdbus-1.so.3 (extracted from the
# EU 260128 rootfs), so the resulting binary runs unchanged inside the VM.
set -e
cd "$(dirname "$0")/../../.."
ZIG=${ZIG:-work/toolchains/zig-macos-aarch64-0.13.0/zig}
DBUS_INC=${DBUS_INC:-/opt/homebrew/include/dbus-1.0}
DBUS_ARCH_INC=${DBUS_ARCH_INC:-/opt/homebrew/lib/dbus-1.0/include}
GUEST_LIBDBUS=${GUEST_LIBDBUS:-work/decrypted-eu-260128/extracted-safe/mango-rootfs/usr/lib/libdbus-1.so.3}
SRC=tools/uk_fw/guest/eng_data_sim.c
OUT=tools/uk_fw/guest/eng-data-sim

"$ZIG" cc -target x86_64-linux-gnu -O1 \
  -I "$DBUS_INC" -I "$DBUS_ARCH_INC" \
  -o "$OUT" "$SRC" "$GUEST_LIBDBUS"

file "$OUT" | cut -c1-100
