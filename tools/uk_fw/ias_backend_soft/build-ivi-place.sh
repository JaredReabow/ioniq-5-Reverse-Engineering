#!/bin/sh
# Cross-build ivi_place, the guest-side ivi_controller placement client.
#
# Same conventions as build.sh / build-shot.sh: bundled zig, -target
# x86_64-linux-gnu, no host wayland development tree. libwayland-client is the
# guest's own shared object, so the ABI is exactly the one the image ships
# (glibc 2.25 target) and DT_NEEDED comes out as libwayland-client.so.0.
#
#   tools/uk_fw/ias_backend_soft/build-ivi-place.sh          # -> ivi_place
#
# Why not build.sh: build.sh links with -shared and produces a loadable weston
# backend plugin (.so) — it cannot produce an executable — and it also patches
# work/weston-source-1.10/full/src/compositor.h to restore the vendor struct
# layout, which this tool has no reason to touch. build-shot.sh is the existing
# precedent for a guest-side *client* binary, and this script follows it.
#
# The two generated protocol files are committed; regenerate them only if
# ivi-controller.xml changes. The generator must be wayland 1.10's own scanner,
# because later scanners emit wl_proxy_marshal_flags(), which does not exist in
# the guest's libwayland-client 1.10. The guest tree here has the scanner source
# (and the guest ships /usr/bin/wayland-scanner, but it is x86-64 Linux):
#
#   # host build of the guest's own scanner, then
#   wl-scanner client-header ivi-controller.xml ivi-controller-client-protocol.h
#   wl-scanner code          ivi-controller.xml ivi-controller-protocol.c
#
# The vendor's layer/surface "destroy" requests are not destructors (they take
# an int id), which wayland 1.10's scanner rejects as a policy check only; the
# scan above was done with those two policy checks removed. Neither check
# affects the wire format or the generated marshalling code.
set -e
cd "$(dirname "$0")/../../.."
ZIG=${ZIG:-work/toolchains/zig-macos-aarch64-0.13.0/zig}
WAY=work/vm/wayland-1.10.0-src           # wayland 1.10.0 client headers
OUT=tools/uk_fw/ias_backend_soft
LIB=${WAYLAND_CLIENT:-work/vm/softbackend/capture/libwayland-client.so}

if [ ! -f "$LIB" ]; then
	DBG=${DEBUGFS:-$(command -v debugfs 2>/dev/null || true)}
	if [ -z "$DBG" ]; then
		echo "build-ivi-place.sh: $LIB missing and debugfs not found" >&2
		exit 1
	fi
	mkdir -p "$(dirname "$LIB")"
	# Read-only extraction from the softbackend image; never the vendor image.
	"$DBG" -R "dump /usr/lib/libwayland-client.so.0.3.0 $LIB" \
		work/vm/softbackend/rootfs.img
fi

"$ZIG" cc -target x86_64-linux-gnu.2.25 -O1 \
	-I "$OUT" -I "$WAY" \
	-o "$OUT/ivi_place" "$OUT/ivi_place.c" \
	"$OUT/ivi-controller-protocol.c" "$LIB"

file "$OUT/ivi_place" | cut -c1-90
ls -l "$OUT/ivi_place" | awk '{print "size:", $5, "bytes"}'
