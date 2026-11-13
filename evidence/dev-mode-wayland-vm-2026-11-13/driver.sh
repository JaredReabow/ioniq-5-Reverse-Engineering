#!/bin/sh
# VM-only Wayland control-versus-modified AppEngineerMode observation.
# No update, factory-reset, vehicle-control, or menu actions.
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/app/bin
while [ ! -r /proc/uptime ] || [ ! -e /dev/ttyS3 ]; do sleep 1; done
exec >/dev/ttyS3 2>&1
set -x
# Stock launcher semantics: Wayland, not the offscreen diagnostic platform.
export LD_LIBRARY_PATH=/app/lib:/usr/lib:/navi/navi/Lib
export QT_QPA_PLATFORM=wayland
export QT_PLUGIN_PATH=/usr/lib/qt5/plugins
export QML2_IMPORT_PATH=/usr/lib/qt5/qml:/app/share
export XDG_RUNTIME_DIR=/run/user/root
export WAYLAND_DISPLAY=wayland-0
if [ -r /tmp/session_appmgr ]; then export DBUS_SESSION_BUS_ADDRESS="$(cat /tmp/session_appmgr)"; fi
n=0
while [ ! -S "$XDG_RUNTIME_DIR/$WAYLAND_DISPLAY" ]; do
    n=$((n+1)); [ "$n" -lt 180 ] || { echo 'DEV_WAYLAND_ABORT socket_not_ready'; printf 'DEV_MODE_WAYLAND_PROBE_COMPLETE\n' >/dev/ttyS0; exit 2; }
    sleep 1
done
printf '\nDEV_WAYLAND_BEGIN\n'; cat /proc/uptime
for item in baseline modified modified_restart; do
    case "$item" in baseline) exe=/app/bin/AppEngineerMode;; *) exe=/app/bin/AppEngineerMode-dev-probe;; esac
    printf '\nDEV_WAYLAND_LAUNCH %s %s\n' "$item" "$exe"
    sha256sum "$exe"
    "$exe" >/tmp/dev-wayland-"$item".log 2>&1 & pid=$!
    sleep 60
    if kill -0 "$pid" 2>/dev/null; then
        echo "DEV_WAYLAND_ALIVE $item pid=$pid"; kill "$pid"; sleep 2
        if kill -0 "$pid" 2>/dev/null; then echo "DEV_WAYLAND_FORCE_STOP $item pid=$pid"; kill -KILL "$pid"; fi
    else echo "DEV_WAYLAND_EXITED $item pid=$pid"; fi
    wait "$pid"; echo "DEV_WAYLAND_STATUS $item rc=$?"
    echo "DEV_WAYLAND_LOG_BEGIN $item"; cat /tmp/dev-wayland-"$item".log; echo "DEV_WAYLAND_LOG_END $item"
done
printf '\nDEV_MODE_WAYLAND_PROBE_COMPLETE\n'
printf '\nDEV_MODE_WAYLAND_PROBE_COMPLETE\n' >/dev/ttyS0
