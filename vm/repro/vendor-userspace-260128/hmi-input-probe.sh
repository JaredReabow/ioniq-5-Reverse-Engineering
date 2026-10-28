#!/bin/busybox sh
BB=/bin/busybox
export LD_LIBRARY_PATH=/opt/software-egl18/lib:/opt/software-egl/lib:/app/lib:/usr/lib:/lib:/navi/Lib:/navi/navi/Lib
export LIBGL_DRIVERS_PATH=/opt/software-egl18/dri
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=softpipe
export LP_NUM_THREADS=1
export XDG_RUNTIME_DIR=/run/user/root
export WAYLAND_DISPLAY=wayland-0

# Reconstruct the volatile runtime state normally established by esinit/systemd.
$BB cp /etc/passwd.legacy /tmp/passwd
echo 'xuser:x:1000:100:xuser:/home/xuser:/bin/sh' >>/tmp/passwd
echo 'byungsu:x:1001:100:byungsu:/home/byungsu:/bin/sh' >>/tmp/passwd
$BB mkdir -p /run/dbus /run/lock /run/user/root /var/run/dbus /rw_data/var/volatile/log /rw_data/var/volatile/tmp /tmp/hmi-wayland
$BB chmod 700 /run/user/root
/usr/bin/dbus-uuidgen --ensure
/usr/bin/dbus-daemon --system --fork 2>/tmp/hmi-dbus.err
echo DBUS_RC=$?

# Select the recovered IONIQ 5 QML and authentic night asset tree.
[ -e /app/share/AppHomeScreen/qml ] || $BB ln -s qml_new2.0 /app/share/AppHomeScreen/qml
$BB mount -o bind /system/new_gui/new2.0/hmc/night /app/share/images/hmc
echo RESOURCE_BIND_RC=$?
$BB mount -o bind /vm-qml/QHMI_HomeScreenMain_Advanced.qml /app/share/AppHomeScreen/qml_new2.0/HomeScreen/QHMI_HomeScreenMain_Advanced.qml
echo QML_INPUT_OVERRIDE_RC=$?

# Production IVI shell on the headless/pixman backend. The named weston-headless
# binary is a pinned VM-only copy that avoids the old composite_clipped bug.
$BB ln -sf /app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png /tmp/front_lcd.png
cat >/tmp/weston-hmi.ini <<'EOF'
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
/usr/bin/weston-headless --config=/tmp/weston-hmi.ini --use-pixman --width=1920 --height=720 --socket=wayland-0 --idle-time=0 --debug >/tmp/hmi-weston.log 2>&1 &
WPID=$!
echo WESTON_PID=$WPID
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -S /run/user/root/wayland-0 ] && break
  $BB sleep 1
done
[ -S /run/user/root/wayland-0 ] || { echo NO_WAYLAND_SOCKET; $BB tail -n 200 /tmp/hmi-weston.log; exit 21; }

# Use the vendor Qt Wayland and IVI shell plugins. 1007 is the home surface id
# declared by the recovered weston_1920.ini; it is scoped to this disposable VM.
export QT_QPA_PLATFORM=wayland
export QT_WAYLAND_SHELL_INTEGRATION=ivi
export QT_WAYLAND_SET_SURFACE_ID=1007
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
export QSG_RENDER_LOOP=basic
export QV4_NO_SSA=1
export QV4_FORCE_INTERPRETER=1
export QT_DEBUG_PLUGINS=0
$BB timeout 500 /app/bin/AppHomeScreen >/tmp/apphome-wayland.log 2>&1 &
APID=$!
echo APPHOME_WRAPPER_PID=$APID
DRAW_READY=0
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45; do
  if $BB grep -q 'SCREEN_STATE: DRAW FINISHED' /tmp/apphome-wayland.log; then
    DRAW_READY=1
    break
  fi
  $BB kill -0 $APID 2>/dev/null || break
  $BB sleep 2
done
echo DRAW_READY=$DRAW_READY
$BB ps | $BB grep -E 'weston-headless|AppHomeScreen' | $BB grep -v grep

# Keep the authentic home surface foreground while the scalar renderer finishes
# constructing the interactive QListViewHomePage. DRAW FINISHED is too early;
# the QML onCompleted marker is the bounded interaction gate.
: >/tmp/hmi-ivi-fg.log
QML_PAGE_READY=0
n=1
while [ "$n" -le 140 ]; do
  /ivi-fg >>/tmp/hmi-ivi-fg.log 2>&1
  if $BB grep -q 'onCompleted: currentIndex = 0' /tmp/apphome-wayland.log; then
    QML_PAGE_READY=1
    break
  fi
  $BB kill -0 $APID 2>/dev/null || break
  n=$((n + 1))
  $BB sleep 2
done
echo QML_PAGE_READY=$QML_PAGE_READY
$BB cat /tmp/hmi-ivi-fg.log
# Reproduce the absent system-popup service's hidden-state notification.
/usr/bin/dbus-send --system --type=signal /com/lge/hkmc/avn/appfunc/appInterface com.lge.hkmc.avn.appfunc.appInterface.NotifySystemPopupState int32:0 int32:0
/usr/bin/dbus-send --system --type=signal /com/lge/hkmc/avn/appfunc/appInterface com.lge.hkmc.avn.appfunc.appInterface.NotifySystemPopupState int32:1 int32:0
echo SYSTEM_POPUP_HIDE_SIGNALS_SENT
$BB sleep 2

capture_frame() {
  name=$1
  d=/tmp/hmi-wayland/$name
  $BB mkdir -p "$d"
  cd "$d"
  /usr/libexec/weston-screenshooter >>/tmp/hmi-input-shot.log 2>&1
  if [ -f "$d/wayland-screenshot.png" ]; then
    set -- $($BB sha256sum "$d/wayland-screenshot.png")
    echo ${name}_SHA=$1
  fi
}

capture_frame BASELINE
BASELINE_SHA=$($BB sha256sum /tmp/hmi-wayland/BASELINE/wayland-screenshot.png 2>/dev/null | $BB cut -d' ' -f1)
echo 'pdrag 1600 650 300 650' >/tmp/weston-vm-input
echo INPUT_POINTER_DRAG_QUEUED
INPUT_DONE=0
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  if $BB grep -q 'VM_INPUT_PDRAG_DONE' /tmp/hmi-weston.log; then
    INPUT_DONE=1
    break
  fi
  $BB sleep 1
done
echo INPUT_DONE=$INPUT_DONE
MOTION_SETTLED=0
n=1
while [ "$n" -le 90 ]; do
  if $BB grep -q 'onMovingChanged: false' /tmp/apphome-wayland.log; then
    MOTION_SETTLED=1
    break
  fi
  $BB kill -0 $APID 2>/dev/null || break
  n=$((n + 1))
  $BB sleep 2
done
echo MOTION_SETTLED=$MOTION_SETTLED
$BB sleep 8
capture_frame POST_INPUT_1
$BB sleep 8
capture_frame POST_INPUT_2
POST_SHA=$($BB sha256sum /tmp/hmi-wayland/POST_INPUT_2/wayland-screenshot.png 2>/dev/null | $BB cut -d' ' -f1)
echo BASELINE_SHA_FINAL=$BASELINE_SHA
echo POST_INPUT_SHA_FINAL=$POST_SHA
if [ -f /tmp/hmi-wayland/POST_INPUT_2/wayland-screenshot.png ]; then
  $BB cp /tmp/hmi-wayland/POST_INPUT_2/wayland-screenshot.png /tmp/hmi-wayland/wayland-screenshot.png
  echo SCREENSHOT_BASE64_BEGIN
  $BB base64 /tmp/hmi-wayland/wayland-screenshot.png
  echo SCREENSHOT_BASE64_END
fi
$BB grep -E 'VM_INPUT|Loading module|Failed to load module' /tmp/hmi-weston.log
$BB kill $APID 2>/dev/null
wait $APID 2>/dev/null
echo APPHOME_STOPPED

echo APPHOME_LOG_BEGIN
$BB cat /tmp/apphome-wayland.log
echo APPHOME_LOG_END
echo WESTON_LOG_BEGIN
$BB tail -n 500 /tmp/hmi-weston.log
echo WESTON_LOG_END
echo DBUS_ERRORS
$BB cat /tmp/hmi-dbus.err
$BB kill $WPID 2>/dev/null
wait $WPID 2>/dev/null
exit 0
