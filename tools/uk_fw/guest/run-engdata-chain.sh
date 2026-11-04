#!/bin/busybox sh
# Engineering-mode data-service chain: same proven launcher/weston stack as
# run-chain23.sh, but the single com.lge.car.micom owner is /eng-data-sim (which
# also serves com.lge.hkmc.avn.AppVR on the session bus). The wrapper
# /run-engdata.sh launches AppEngineerMode against this chain and captures.
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
/usr/bin/persistence-admin-stub >/tmp/launcher-chain/persist-stub.log 2>&1 &
$BB sleep 1
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr)
# Single fail-closed simulator for the whole data landscape: micom boot info on
# the system bus (com.lge.car.micom) plus the six engineering-mode asks, and the
# AppVH VR-version interface on the session bus.
/eng-data-sim >/tmp/launcher-chain/eng-data-sim.log 2>&1 &
EPID=$!
/usr/bin/dbus-monitor --system > /tmp/launcher-chain/system-bus.log 2>&1 &
SBPID=$!
/usr/bin/dbus-monitor --session > /tmp/launcher-chain/session-bus.log 2>&1 &
BPID=$!
[ -e /app/share/AppHomeScreen/qml ] || $BB ln -s qml_new2.0 /app/share/AppHomeScreen/qml
$BB mount -o bind /system/new_gui/new2.0/hmc/night /app/share/images/hmc
[ -e /navi/navi ] || $BB ln -s . /navi/navi
$BB ln -sf /app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png /tmp/front_lcd.png
cat >/tmp/launcher-weston.ini <<'EOF'
[core]
backend=headless-backend.so
shell=ivi-shell.so
modules=/weston-vm-input.so
idle-time=0
[ivi-shell]
ivi-module=ivi-window-manager.so,ivi-controller.so,hmi-controller.so
ivi-shell-user-interface=/usr/bin/keeper
base-layer-id=1000
workspace-background-layer-id=2000
workspace-layer-id=3000
application-layer-id=4000
transition-duration=0
workspace-background-color=0xff000000
workspace-background-id=2001
background-id=2001
panel-id=2002
tiling-id=2003
sidebyside-id=2004
fullscreen-id=2005
random-id=2006
home-id=2007
surface-id-offset=1000
[output]
name=headless
mode=1920x720
EOF
{ /usr/bin/weston-headless --config=/tmp/launcher-weston.ini --use-pixman --width=1920 --height=720 --socket=wayland-0 --idle-time=0 --debug >/tmp/launcher-chain/weston.log 2>&1; echo "WESTON_EXIT=$?" > /tmp/weston-exit.txt; } &
WPID=$!
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -S /run/user/root/wayland-0 ] && break
  $BB sleep 1
done
[ -S /run/user/root/wayland-0 ] || { echo NO_WAYLAND_SOCKET; exit 21; }
$BB mount --bind /AppNavi-egl-no-msaa-v2 /navi/Bin/AppNavi || exit 23
export WAYLAND_DEBUG=1
$BB mkdir -p /tmp/dltpipes /rw_data/dlt
$BB printf 'ECUId = MANGO\nPrintASCII = 1\nLoggingMode = 0\nLoggingLevel = 7\nPersistanceStoragePath = /rw_data/dlt\n' >/tmp/dlt-test.conf
/usr/bin/dlt-daemon -c /tmp/dlt-test.conf >/tmp/launcher-chain/dlt.log 2>&1 &
DPID=$!
cd /app/bin || exit 22
/app/bin/AppLauncher 3 >/tmp/launcher-chain/launcher.log 2>&1 &
LPID=$!
echo APPLAUNCHER_DIRECT_PID=$LPID
$BB sleep 25
/usr/bin/dbus-send --session --print-reply --dest=com.lge.avn.applauncher /Request com.lge.avn.applauncher.request.launch int32:30 string:AppNavi string:/navi/navi/Bin/AppNavi >/dev/null 2>&1
echo APPNAVI_REQ_RC=$?
# Dwell: the wrapper owns all eng-mode timing. Keep the stack alive until the
# wrapper has captured; then tear down.
$BB sleep 600
echo PROCESS_LIST_BEGIN
$BB ps > /tmp/launcher-chain/processes.txt
$BB cat /tmp/launcher-chain/processes.txt
echo PROCESS_LIST_END
$BB kill -9 $LPID $EPID $BPID $SBPID $DPID 2>/dev/null
$BB killall -9 AppLauncher ApplicationManager AppHomeScreen AppNavi dlt-daemon dbus-monitor eng-data-sim 2>/dev/null
$BB sleep 1
$BB kill -9 $WPID 2>/dev/null
wait $LPID 2>/dev/null
wait $WPID 2>/dev/null
exit 0
