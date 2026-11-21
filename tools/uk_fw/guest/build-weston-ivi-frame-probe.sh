#!/bin/sh
# Cross-build only the opt-in VM diagnostic, never a vehicle artifact.
set -eu
cd "$(dirname "$0")/../../.."
ZIG=${ZIG:-zig}
OUT=${OUT:-tools/uk_fw/guest/weston-ivi-frame-probe.so}
"$ZIG" cc -target x86_64-linux-gnu.2.25 -std=c11 -O1 -g0 -Wall -Wextra -Werror -shared -fPIC \
  -ffile-prefix-map="$PWD"=. -fdebug-prefix-map="$PWD"=. \
  -o "$OUT" tools/uk_fw/guest/weston_ivi_frame_probe.c
