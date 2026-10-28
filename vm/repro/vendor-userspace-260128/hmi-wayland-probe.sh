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
$BB timeout 180 /app/bin/AppHomeScreen >/tmp/apphome-wayland.log 2>&1 &
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

# Promote the home surface through the recovered IVI window-manager protocol,
# immediately after the authentic application reports its initial draw complete.
# Capture continuously while foreground requests race the delayed first Qt
# buffer commit. Preserve the latest frame that differs from the splash.
SPLASH_SHA=b316a82a1f8f726163c55705d6d6522603cbf9fbb3bb5b85a9d247876e0b9a83
$BB rm -f /tmp/hmi-wayland/wayland-screenshot.png
(
  for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    d=/tmp/hmi-wayland/shot$n
    $BB mkdir -p "$d"
    cd "$d"
    /usr/libexec/weston-screenshooter >>/tmp/hmi-shot.log 2>&1
    if [ -f "$d/wayland-screenshot.png" ]; then
      set -- $($BB sha256sum "$d/wayland-screenshot.png")
      echo CAPTURE_${n}_SHA=$1 >>/tmp/hmi-shot.log
      if [ "$1" != "$SPLASH_SHA" ]; then
        $BB cp "$d/wayland-screenshot.png" /tmp/hmi-wayland/wayland-screenshot.png
        echo CAPTURE_SELECTED=$n >>/tmp/hmi-shot.log
      fi
    fi
    if [ "$n" = 16 ]; then
      echo 'drag 1600 650 300 650' >/tmp/weston-vm-input
      echo INPUT_DRAG_QUEUED >>/tmp/hmi-shot.log
    fi
    $BB sleep 1
  done
  [ -f /tmp/hmi-wayland/wayland-screenshot.png ] || {
    [ -f /tmp/hmi-wayland/shot20/wayland-screenshot.png ] && $BB cp /tmp/hmi-wayland/shot20/wayland-screenshot.png /tmp/hmi-wayland/wayland-screenshot.png
  }
) &
SHOTPID=$!

: >/tmp/hmi-ivi-fg.log
for n in 1 2 3 4 5 6 7 8 9 10 11 12; do
  /ivi-fg >>/tmp/hmi-ivi-fg.log 2>&1
  echo IVI_FG_ATTEMPT_${n}_RC=$?
  $BB sleep 1
done
$BB cat /tmp/hmi-ivi-fg.log
wait $SHOTPID
echo SCREENSHOT_CAPTURE_LOG
$BB cat /tmp/hmi-shot.log
$BB ls -l /tmp/hmi-wayland/wayland-screenshot.png 2>/dev/null
if [ -f /tmp/hmi-wayland/wayland-screenshot.png ]; then
  $BB sha256sum /tmp/hmi-wayland/wayland-screenshot.png
  echo SCREENSHOT_BASE64_BEGIN
  $BB base64 /tmp/hmi-wayland/wayland-screenshot.png
  echo SCREENSHOT_BASE64_END
fi
wait $APID
echo APPHOME_RC=$?

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
