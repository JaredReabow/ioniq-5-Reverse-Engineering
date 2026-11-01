#!/bin/busybox sh
BB=/bin/busybox
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/app/bin
export LD_LIBRARY_PATH=/opt/software-egl18/lib:/opt/software-egl/lib:/app/lib:/usr/lib:/lib:/navi/Lib:/navi/navi/Lib
export LIBGL_DRIVERS_PATH=/opt/software-egl18/dri
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=softpipe
export LP_NUM_THREADS=1
export XDG_RUNTIME_DIR=/run/user/root
export WAYLAND_DISPLAY=wayland-0
export QT_QPA_PLATFORM=wayland
# AppLauncher appends its own :ivi value for child processes. Pre-setting this
# produced the invalid value ivi:ivi and QPA shell-integration failures.
unset QT_WAYLAND_SHELL_INTEGRATION
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
export QSG_RENDER_LOOP=basic
export QV4_MM_MAX_CHUNK_SIZE=16384
export QV4_NO_SSA=1
export QV4_FORCE_INTERPRETER=1
$BB cp /etc/passwd.legacy /tmp/passwd
echo 'xuser:x:1000:100:xuser:/home/xuser:/bin/sh' >>/tmp/passwd
echo 'byungsu:x:1001:100:byungsu:/home/byungsu:/bin/sh' >>/tmp/passwd
$BB mkdir -p /run/dbus /run/lock /run/user/root /var/run/dbus /rw_data/var/volatile/log /rw_data/var/volatile/tmp /tmp/launcher-chain /log_data
$BB chmod 700 /run/user/root
/usr/bin/dbus-uuidgen --ensure
/usr/bin/dbus-daemon --system --fork 2>/tmp/launcher-chain/system-dbus.err
/usr/bin/dbus-daemon --session --print-address --fork >/tmp/session_appmgr 2>/tmp/launcher-chain/session-dbus.err
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr)
# VM-only, fail-closed NE/EUR idle boot profile. Every unsupported micom call
# receives UnknownObject/UnknownMethod and is logged for contract expansion.
MICOM_BOOTINFO=00000826050000051302000003c8140000000000000000000000020001000000000000
/micom-dbus-sim "$MICOM_BOOTINFO" >/tmp/launcher-chain/micom-sim.log 2>&1 &
MPID=$!
[ -e /app/share/AppHomeScreen/qml ] || $BB ln -s qml_new2.0 /app/share/AppHomeScreen/qml
$BB mount -o bind /system/new_gui/new2.0/hmc/night /app/share/images/hmc
[ -e /navi/navi ] || $BB ln -s . /navi/navi
$BB ln -sf /app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png /tmp/front_lcd.png
cat >/tmp/launcher-weston.ini <<'EOF'
[core]
backend=headless-backend.so
shell=ivi-shell.so
idle-time=0
[ivi-shell]
ivi-module=ivi-window-manager.so,ivi-controller.so
ivi-shell-user-interface=/bin/true
base-layer-id=1000
workspace-background-layer-id=2000
workspace-layer-id=3000
application-layer-id=4000
transition-duration=0
workspace-background-color=0xff000000
workspace-background-id=2001
[output]
name=headless
mode=1920x720
EOF
/usr/bin/weston-headless --config=/tmp/launcher-weston.ini --use-pixman --width=1920 --height=720 --socket=wayland-0 --idle-time=0 --debug >/tmp/launcher-chain/weston.log 2>&1 &
WPID=$!
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -S /run/user/root/wayland-0 ] && break
  $BB sleep 1
done
[ -S /run/user/root/wayland-0 ] || { echo NO_WAYLAND_SOCKET; exit 21; }
# Use existing proven adaptations, no fabricated micom payload or semaphore reset.
$BB mount --bind /AppNavi-egl-no-msaa-v2 /navi/Bin/AppNavi || exit 23
export WAYLAND_DEBUG=1
$BB mkdir -p /tmp/dltpipes /rw_data/dlt
$BB printf 'ECUId = MANGO\nPrintASCII = 1\nLoggingMode = 0\nLoggingLevel = 7\nPersistanceStoragePath = /rw_data/dlt\n' >/tmp/dlt-test.conf
/usr/bin/dlt-daemon -c /tmp/dlt-test.conf >/tmp/launcher-chain/dlt.log 2>&1 &
DPID=$!
# Full-chain control: do not claim the authentic AppStandbyClock service with
# the isolated AppNavi valet stub. AppLauncher starts the real service.
SPID=
/usr/bin/dbus-monitor --session > /tmp/launcher-chain/session-bus.log 2>&1 &
BPID=$!
echo IPC_BEFORE_LAUNCH
/ipc-observe
cd /app/bin || exit 22
# Timing control: launch directly so syscall tracing cannot trigger the
# recovered manager's application-liveness watchdog under software rendering.
/app/bin/AppLauncher 3 >/tmp/launcher-chain/launcher.log 2>&1 &
LPID=$!
echo APPLAUNCHER_DIRECT_PID=$LPID
$BB sleep 25
echo IPC_AFTER_LAUNCH
/ipc-observe
echo DBUS_NAMES_BEFORE_NAVI
/usr/bin/dbus-send --session --print-reply --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames
echo APPNAVI_LAUNCH_REQUEST_BEGIN
/usr/bin/dbus-send --session --print-reply --dest=com.lge.avn.applauncher /Request com.lge.avn.applauncher.request.launch int32:30 string:AppNavi string:/navi/navi/Bin/AppNavi
NAVI_REQ_RC=$?
echo APPNAVI_LAUNCH_REQUEST_RC=$NAVI_REQ_RC
echo APPNAVI_LAUNCH_REQUEST_END
$BB sleep 50
echo IPC_AFTER_NAVI_50
/ipc-observe
$BB sleep 80
echo IPC_AFTER_NAVI_130
/ipc-observe
$BB cat /proc/sysvipc/sem /proc/sysvipc/shm > /tmp/launcher-chain/sysvipc.txt
# Capture without an IVI hierarchy repair first: observe authentic chain behavior.
echo PROCESS_LIST_BEGIN
$BB ps > /tmp/launcher-chain/processes.txt
$BB cat /tmp/launcher-chain/processes.txt
echo PROCESS_LIST_END
$BB mkdir -p /tmp/launcher-chain/shot
cd /tmp/launcher-chain/shot
$BB timeout 15 /usr/libexec/weston-screenshooter >/tmp/launcher-chain/screenshot.log 2>&1
if [ -f wayland-screenshot.png ]; then
 echo CHAIN_SCREENSHOT_SHA256
 $BB sha256sum wayland-screenshot.png
fi
# Bounded capture; terminate direct launcher and descendants explicitly.
$BB kill -9 $LPID $SPID $BPID $DPID $MPID 2>/dev/null
$BB killall -9 AppLauncher ApplicationManager AppHomeScreen AppNavi strace dbus-bool-stub dbus-monitor dlt-daemon micom-dbus-sim 2>/dev/null
$BB sleep 1
$BB kill -9 $WPID 2>/dev/null
wait $LPID 2>/dev/null
wait $WPID 2>/dev/null
$BB tar -czf /tmp/micom-chain-evidence.tar.gz -C /tmp launcher-chain
$BB sha256sum /tmp/micom-chain-evidence.tar.gz
echo CHAIN_ARCHIVE_BASE64_BEGIN
$BB base64 /tmp/micom-chain-evidence.tar.gz
echo CHAIN_ARCHIVE_BASE64_END
exit 0
