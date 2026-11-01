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
# Restore the recovered production target of /app/share/images/new_gui ->
# /tmp/new_gui. Without this bind, the legal-profile QML has zero-sized theme
# images and its anchored controls are displaced off-screen.
$BB mkdir -p /tmp/new_gui
$BB mount -o bind /system/new_gui /tmp/new_gui
$BB mount -o bind /system/new_gui/new2.0/hmc/night /app/share/images/hmc
# Observational-only QML overlay: logs authentic model state and resolved
# geometry without changing button bindings, handlers, or enabled state.
$BB mount -o bind /Screen_AppStandbyClock_Confirm_Profile.observe.qml /app/share/AppStandbyClock/qml_eco3.0/Screen_AppStandbyClock_Confirm_Profile.qml
$BB mount -o bind /AppStandbyClock-main.loader-sized-nostatus.qml /app/share/AppStandbyClock/qml_eco3.0/main.qml
[ -e /navi/navi ] || $BB ln -s . /navi/navi
$BB ln -sf /app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png /tmp/front_lcd.png
cat >/tmp/launcher-weston.ini <<'EOF'
[core]
backend=headless-backend.so
shell=ivi-shell.so
modules=/weston-vm-input.so
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
# VM timing adaptation: AppStandbyClock registered about three seconds after
# the prior 60-second group timeout. This exact-build control changes only the
# same QTimer immediate, 10,000 -> 120,000 ms at file offset 0x18270, so the
# authentic standby registration can precede preload completion.
$BB mount --bind /AppLauncher-vm-timeout120 /app/bin/AppLauncher || exit 24
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
# Let authentic AppStandbyClock register before the adapted group timer can
# expire. Do not issue an extra AppNavi launch request in this ordering control.
$BB sleep 75
echo IPC_AFTER_LAUNCH_75
/ipc-observe
$BB cat /proc/sysvipc/sem /proc/sysvipc/shm > /tmp/launcher-chain/sysvipc.txt

echo PROCESS_LIST_BEGIN
$BB ps > /tmp/launcher-chain/processes.txt
$BB cat /tmp/launcher-chain/processes.txt
echo PROCESS_LIST_END

echo STANDBY_STATUS_BASELINE
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_standby_status
$BB mkdir -p /tmp/launcher-chain/shot-before-confirm
cd /tmp/launcher-chain/shot-before-confirm
$BB timeout 15 /usr/libexec/weston-screenshooter >/tmp/launcher-chain/screenshot-before-confirm.log 2>&1
[ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png

# Ask authentic AppStandbyClock to enter the evidence-derived profile/legal
# screen using the exact six-argument tuple observed from ApplicationManager:
# appid=10, reason=11, plane=1, avmode=-1, command=0, temporal=false. Then
# foreground observed surface 1000. This exercises, rather than bypasses, the gate.
echo STANDBY_APPBASE_FOREGROUND_BEGIN
STANDBY_APPBASE_FOREGROUND_RC=1
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
  echo STANDBY_APPBASE_FOREGROUND_ATTEMPT=$n
  $BB timeout 5 /usr/bin/dbus-send --session --print-reply \
    --dest=com.lge.hkmc.avn.appfunc.AppStandbyClock \
    /com/lge/hkmc/avn/appfunc/standby \
    com.lge.avn.appmanager.appbase.show_window_fg \
    int32:10 int32:11 int32:1 int32:-1 int32:0 boolean:false
  STANDBY_APPBASE_FOREGROUND_RC=$?
  [ "$STANDBY_APPBASE_FOREGROUND_RC" -eq 0 ] && break
  $BB sleep 1
 done
echo STANDBY_APPBASE_FOREGROUND_RC=$STANDBY_APPBASE_FOREGROUND_RC
$BB sleep 2
$BB timeout 15 /ivi-fg-standby1000
echo STANDBY_IVI_FOREGROUND_RC=$?
$BB sleep 2
echo STANDBY_STATUS_AFTER_FOREGROUND
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_standby_status
$BB mkdir -p /tmp/launcher-chain/shot-standby-forced
cd /tmp/launcher-chain/shot-standby-forced
$BB timeout 15 /usr/libexec/weston-screenshooter >/tmp/launcher-chain/screenshot-standby-forced.log 2>&1
[ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png

# qml_eco3.0/Screen_AppStandbyClock_Confirm_Profile.qml places the
# wide-screen Confirm button in the left half of txtArea. With bg x=9 and the
# 452-pixel profile area, x=800 is bounded inside Confirm; x=1500 was Language.
# Late-starting clients can acquire pointer focus after the first foreground
# request. Re-assert surface 1000 immediately before motion/button injection.
echo STANDBY_IVI_REFOREGROUND_BEFORE_POINTER_BEGIN
$BB timeout 15 /ivi-fg-standby1000
echo STANDBY_IVI_REFOREGROUND_BEFORE_POINTER_RC=$?
$BB sleep 1
echo STANDBY_CONFIRM_LEFT_POINTER 820 630
echo pdrag 820 630 820 630 >/tmp/weston-vm-input
$BB sleep 15
echo STANDBY_STATUS_AFTER_CONFIRM_LEFT
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_standby_status
$BB mkdir -p /tmp/launcher-chain/shot-after-confirm
cd /tmp/launcher-chain/shot-after-confirm
$BB timeout 15 /usr/libexec/weston-screenshooter >/tmp/launcher-chain/screenshot-after-confirm.log 2>&1
[ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png

# If authentic confirmation only clears the standby gate without initiating a
# page change, exercise the evidence-backed Home faceplate path afterward.
echo HOME_TRANSITION_AFTER_CONFIRM_BEGIN
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /transition \
  com.lge.avn.appmanager.screentransition.request \
  int32:302 int32:0 int32:322 int32:1 int32:0
HOME_TRANSITION_RC=$?
echo HOME_TRANSITION_AFTER_CONFIRM_RC=$HOME_TRANSITION_RC
$BB sleep 12
$BB mkdir -p /tmp/launcher-chain/shot-home
cd /tmp/launcher-chain/shot-home
$BB timeout 15 /usr/libexec/weston-screenshooter >/tmp/launcher-chain/screenshot-home.log 2>&1
[ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png

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
