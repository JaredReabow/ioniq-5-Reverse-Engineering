#!/bin/busybox sh
BB=/bin/busybox
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
export XDG_RUNTIME_DIR=/run/user/root
export WAYLAND_DISPLAY=wayland-0
export LD_LIBRARY_PATH=/opt/software-egl18/lib:/opt/software-egl/lib:/app/lib:/usr/lib:/lib
export LIBGL_DRIVERS_PATH=/opt/software-egl18/dri
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export LIBGL_DEBUG=verbose
$BB mkdir -p /run/user/root /tmp/software-egl-shot
$BB chmod 700 /run/user/root
$BB ln -sf /app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png /tmp/front_lcd.png
cat >/tmp/software-egl-weston.ini <<'EOF'
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
EOF

echo LDD_SWRAST_BEGIN
/usr/bin/ldd /opt/software-egl18/dri/swrast_dri.so 2>&1
echo LDD_SWRAST_END
/usr/bin/weston-headless --config=/tmp/software-egl-weston.ini --use-pixman --width=1920 --height=720 --socket=wayland-0 --idle-time=0 --debug >/tmp/software-egl-weston.log 2>&1 &
WPID=$!
$BB sleep 8
[ -S /run/user/root/wayland-0 ] || { echo NO_WAYLAND_SOCKET; $BB cat /tmp/software-egl-weston.log; exit 21; }
export SIMPLE_EGL_SURFACE_ID=1007
$BB timeout 30 /usr/bin/weston-simple-egl -f >/tmp/software-egl-client.log 2>&1 &
CPID=$!
$BB sleep 10
echo 'click 960 360' >/tmp/weston-vm-input
$BB sleep 1
$BB ps | $BB grep -E 'weston-headless|weston-simple-egl' | $BB grep -v grep
/ivi-fg >/tmp/ivi-fg.log 2>&1
echo IVI_FG_RC=$?
echo IVI_FG_LOG
$BB cat /tmp/ivi-fg.log
$BB sleep 3
cd /tmp/software-egl-shot
/usr/libexec/weston-screenshooter >/tmp/software-egl-shot.log 2>&1
echo SCREENSHOT_RC=$?
$BB sleep 2
$BB ls -l /tmp/software-egl-shot/wayland-screenshot.png 2>/dev/null
if [ -f /tmp/software-egl-shot/wayland-screenshot.png ]; then
  $BB sha256sum /tmp/software-egl-shot/wayland-screenshot.png
  echo SCREENSHOT_BASE64_BEGIN
  $BB base64 /tmp/software-egl-shot/wayland-screenshot.png
  echo SCREENSHOT_BASE64_END
fi
$BB kill $CPID $WPID 2>/dev/null
$BB wait $CPID 2>/dev/null
echo CLIENT_LOG_BEGIN
$BB cat /tmp/software-egl-client.log
echo CLIENT_LOG_END
echo WESTON_INPUT_LOG
$BB grep -E 'VM_INPUT|Loading module|Failed to load module' /tmp/software-egl-weston.log
echo WESTON_LOG_TAIL
$BB tail -n 250 /tmp/software-egl-weston.log
$BB cat /tmp/software-egl-shot.log
exit 0
