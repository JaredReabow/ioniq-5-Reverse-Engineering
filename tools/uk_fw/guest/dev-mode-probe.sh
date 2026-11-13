#!/bin/sh
# Disposable VM only. Does not call any update/factory-reset/vehicle-control action.
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/app/bin
while [ ! -r /proc/uptime ] || [ ! -e /dev/ttyS0 ]; do sleep 1; done
exec >/dev/ttyS0 2>&1
sleep 60
printf '\nDEV_PROBE_BEGIN\n'
cat /proc/uptime
export LD_LIBRARY_PATH=/app/lib:/usr/lib:/navi/navi/Lib
export QT_QPA_PLATFORM=offscreen
export QT_PLUGIN_PATH=/usr/lib/qt5/plugins
export QML2_IMPORT_PATH=/usr/lib/qt5/qml:/app/share
export XDG_RUNTIME_DIR=/run/user/root
if [ -r /tmp/session_appmgr ]; then
    export DBUS_SESSION_BUS_ADDRESS="$(cat /tmp/session_appmgr)"
fi
mkdir -p /tmp/dev-probe
for item in baseline modified modified_restart; do
    case "$item" in baseline) exe=/app/bin/AppEngineerMode;; *) exe=/app/bin/AppEngineerMode-dev-probe;; esac
    printf '\nDEV_PROBE_LAUNCH %s %s\n' "$item" "$exe"
    sha256sum "$exe"
    "$exe" >/tmp/dev-probe/"$item".log 2>&1 &
    pid=$!
    sleep 20
    if kill -0 "$pid" 2>/dev/null; then
        echo "DEV_PROBE_ALIVE $item pid=$pid"
        readlink /proc/"$pid"/exe
        kill "$pid"
    else
        echo "DEV_PROBE_EXITED $item pid=$pid"
    fi
    wait "$pid"; echo "DEV_PROBE_STATUS $item rc=$?"
    echo "DEV_PROBE_LOG_BEGIN $item"
    cat /tmp/dev-probe/"$item".log
    echo "DEV_PROBE_LOG_END $item"
done
printf '\nDEV_MODE_PROBE_COMPLETE\n'
