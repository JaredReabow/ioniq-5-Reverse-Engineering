#!/bin/busybox sh
BB=/bin/busybox
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
export LD_LIBRARY_PATH=/app/lib:/usr/lib:/lib
export XDG_RUNTIME_DIR=/run/user/root
$BB mkdir -p "$XDG_RUNTIME_DIR" /tmp/weston-probe
$BB chmod 700 "$XDG_RUNTIME_DIR"
$BB ln -sf /app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png /tmp/front_lcd.png
cat >/tmp/weston-headless.ini <<'WESTON'
[core]
shell=ivi-shell.so
backend=headless-backend.so

[ivi-shell]
ivi-module=ivi-window-manager.so,ivi-controller.so
ivi-shell-user-interface=/bin/true
base-layer-id=1000
workspace-background-layer-id=2000
workspace-layer-id=3000
application-layer-id=4000
WESTON
/usr/bin/weston-headless --version
/usr/bin/weston-headless --config=/tmp/weston-headless.ini --use-pixman --width=1920 --height=720 --socket=wayland-0 --idle-time=0 --debug >/tmp/weston.log 2>&1 &
wpid=$!
$BB sleep 5
echo WESTON_PID=$wpid
$BB ps | $BB grep -E 'weston|PID'
echo WESTON_SOCKET
$BB ls -l "$XDG_RUNTIME_DIR"
WAYLAND_DISPLAY=wayland-0 /usr/bin/weston-info >/tmp/weston-info.log 2>&1
echo WESTON_INFO_RC=$?
WAYLAND_DISPLAY=wayland-0 /usr/bin/weston-simple-shm >/tmp/simple-shm.log 2>&1 &
cpid=$!
$BB sleep 5
cd /tmp/weston-probe
WAYLAND_DISPLAY=wayland-0 /usr/libexec/weston-screenshooter >/tmp/screenshooter.log 2>&1
echo SCREENSHOT_RC=$?
$BB ls -l /tmp/weston-probe /tmp/wayland-screenshot.png 2>/dev/null
if [ -f /tmp/weston-probe/wayland-screenshot.png ]; then
  $BB sha256sum /tmp/weston-probe/wayland-screenshot.png
  echo SCREENSHOT_BASE64_BEGIN
  $BB base64 /tmp/weston-probe/wayland-screenshot.png
  echo SCREENSHOT_BASE64_END
fi
echo WESTON_LOG
$BB tail -n 160 /tmp/weston.log
echo WESTON_INFO
$BB head -n 100 /tmp/weston-info.log
echo CLIENT_LOG
$BB cat /tmp/simple-shm.log /tmp/screenshooter.log
$BB kill $cpid $wpid 2>/dev/null
