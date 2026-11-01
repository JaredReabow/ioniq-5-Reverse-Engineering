#!/bin/busybox sh
# Observation-only wrapper. Existing vendor/VM compatibility behavior is unchanged.
BB=/bin/busybox
BASE=/tmp/decoration-control-baseline.sh
OUT=/tmp/launcher-chain/backend-observe
[ -r "$BASE" ] || exit 91
$BB mkdir -p "$OUT"
observe_backend() {
  tick=0
  while [ "$tick" -lt 100 ]; do
    tick=$((tick + 1))
    # Do not start or select a substitute navigation process.
    for pid in $($BB pidof AppNavi 2>/dev/null); do
      [ -r "/proc/$pid/maps" ] || continue
      tag="$pid-$tick"
      $BB cat "/proc/$pid/maps" >"$OUT/maps-$tag.txt"
      $BB readlink "/proc/$pid/exe" >"$OUT/exe-$tag.txt" 2>/dev/null
      # Strict allowlist; never save the full environment or bus address.
      $BB tr '\000' '\n' <"/proc/$pid/environ" 2>/dev/null |
        $BB grep -E '^(QT_QPA_PLATFORM|QT_PLUGIN_PATH|QT_WAYLAND_SHELL_INTEGRATION|QT_WAYLAND_CLIENT_BUFFER_INTEGRATION|QT_WAYLAND_DISABLE_WINDOWDECORATION|LD_LIBRARY_PATH|LD_PRELOAD|GALLIUM_DRIVER|LIBGL_DRIVERS_PATH|QSG_RENDER_LOOP|WAYLAND_DEBUG)=' \
        >"$OUT/env-allowlist-$tag.txt"
      # Bound hashing to mapped Qt/client/backend files and deduplicate paths.
      $BB awk 'NF >= 6 && $6 ~ /^\// && $6 ~ /(Qt5WaylandClient|qt5\/plugins\/.*wayland|qt5\/plugins\/.*egl|libEGL|libwayland-egl|swrast_dri)/ {print $6}' \
        "$OUT/maps-$tag.txt" | $BB sort -u >"$OUT/selected-paths-$tag.txt"
      while IFS= read -r path; do
        [ -f "$path" ] && $BB sha256sum "$path"
      done <"$OUT/selected-paths-$tag.txt" >"$OUT/mapped-sha256-$tag.txt"
      $BB cat /proc/uptime >"$OUT/uptime-$tag.txt"
    done
    $BB sleep 10
  done
}
observe_backend >"$OUT/observer.log" 2>&1 &
OBSERVER_PID=$!
# Cleanup only this wrapper's observer; baseline manages its own guest processes.
trap '$BB kill "$OBSERVER_PID" 2>/dev/null' EXIT HUP INT TERM
/bin/busybox sh "$BASE"
rc=$?
$BB kill "$OBSERVER_PID" 2>/dev/null
wait "$OBSERVER_PID" 2>/dev/null
exit "$rc"
