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
export QT_WAYLAND_SHELL_INTEGRATION=ivi
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
export QSG_RENDER_LOOP=basic
export QV4_NO_SSA=1
export QV4_FORCE_INTERPRETER=1
$BB cp /etc/passwd.legacy /tmp/passwd
echo 'xuser:x:1000:100:xuser:/home/xuser:/bin/sh' >>/tmp/passwd
echo 'byungsu:x:1001:100:byungsu:/home/byungsu:/bin/sh' >>/tmp/passwd
$BB mkdir -p /run/dbus /run/lock /run/user/root /var/run/dbus /rw_data/var/volatile/log /rw_data/var/volatile/tmp /tmp/appnavi-render /log_data
$BB chmod 700 /run/user/root
/usr/bin/dbus-uuidgen --ensure
/usr/bin/dbus-daemon --system --fork 2>/tmp/appnavi-render/system-dbus.err
/usr/bin/dbus-daemon --session --print-address --fork >/tmp/session_appmgr 2>/tmp/appnavi-render/session-dbus.err
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr)
[ -e /navi/navi ] || $BB ln -s . /navi/navi
$BB ln -sf /app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png /tmp/front_lcd.png
cat >/tmp/appnavi-render-weston.ini <<'EOF'
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
/usr/bin/weston-headless --config=/tmp/appnavi-render-weston.ini --use-pixman --width=1920 --height=720 --socket=wayland-0 --idle-time=0 --debug >/tmp/appnavi-render/weston.log 2>&1 &
WPID=$!
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -S /run/user/root/wayland-0 ] && break
  $BB sleep 1
done
[ -S /run/user/root/wayland-0 ] || { echo NO_WAYLAND_SOCKET; exit 21; }
cd /app/bin
/usr/bin/env -u QT_WAYLAND_SET_SURFACE_ID /app/bin/ApplicationManager -cv:0 -vv:0 -sv:0 -dt:0 -l:0 -ck:0 >/tmp/appnavi-render/appmgr.log 2>&1 &
MPID=$!
$BB sleep 8
cd /navi/navi/Bin || exit 22
export QT_WAYLAND_SET_SURFACE_ID=3000
export WAYLAND_DEBUG=1
$BB timeout 180 /navi/navi/Bin/AppNavi -cv:0 -vv:0 -sv:0 -dt:0 -l:0 -ck:0 >/tmp/appnavi-render/appnavi.log 2>&1 &
APID=$!
echo APPNAVI_WRAPPER_PID=$APID
for n in 1 2 3 4 5 6 7 8 9 10 11 12; do
  $BB sleep 10
  /ivi-fg-navi >>/tmp/appnavi-render/ivi-fg.log 2>&1
done
echo PROCESS_LIST_BEGIN
$BB ps
echo PROCESS_LIST_END
$BB mkdir -p /tmp/appnavi-render/shot
cd /tmp/appnavi-render/shot
/usr/libexec/weston-screenshooter >/tmp/appnavi-render/screenshot.log 2>&1
$BB sleep 3
if [ -f /tmp/appnavi-render/shot/wayland-screenshot.png ]; then
  $BB sha256sum /tmp/appnavi-render/shot/wayland-screenshot.png
  echo SCREENSHOT_BASE64_BEGIN
  $BB base64 /tmp/appnavi-render/shot/wayland-screenshot.png
  echo SCREENSHOT_BASE64_END
fi
$BB kill $APID 2>/dev/null
wait $APID 2>/dev/null
echo APPNAVI_STOPPED
echo APPNAVI_PROTOCOL_EVENTS
$BB grep -E 'ivi_application.*surface_create|wl_surface.*(attach|damage|commit)|egl|EGL' /tmp/appnavi-render/appnavi.log | $BB tail -n 1000
echo APPNAVI_LOG_BEGIN
$BB tail -n 2000 /tmp/appnavi-render/appnavi.log
echo APPNAVI_LOG_END
echo APPMANAGER_LOG_TAIL
$BB tail -n 1000 /tmp/appnavi-render/appmgr.log
echo WESTON_NAVI_EVENTS
$BB grep -E '3000|wl_surface.*(attach|damage|commit)|ivi_application.*surface_create' /tmp/appnavi-render/weston.log | $BB tail -n 1000
echo WESTON_LOG_TAIL
$BB tail -n 300 /tmp/appnavi-render/weston.log
$BB cat /tmp/appnavi-render/ivi-fg.log /tmp/appnavi-render/screenshot.log /tmp/appnavi-render/system-dbus.err /tmp/appnavi-render/session-dbus.err
$BB kill $APID $MPID $WPID 2>/dev/null
wait $APID 2>/dev/null
wait $MPID 2>/dev/null
wait $WPID 2>/dev/null
exit 0
