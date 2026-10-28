#!/bin/busybox sh
BB=/bin/busybox
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
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
export WAYLAND_DEBUG=1
$BB cp /etc/passwd.legacy /tmp/passwd
echo 'xuser:x:1000:100:xuser:/home/xuser:/bin/sh' >>/tmp/passwd
echo 'byungsu:x:1001:100:byungsu:/home/byungsu:/bin/sh' >>/tmp/passwd
$BB mkdir -p /run/dbus /run/lock /run/user/root /var/run/dbus /rw_data/var/volatile/log /rw_data/var/volatile/tmp /tmp/appnavi-wayland
$BB chmod 700 /run/user/root
/usr/bin/dbus-uuidgen --ensure
/usr/bin/dbus-daemon --system --fork 2>/tmp/appnavi-wayland/system-dbus.err
/usr/bin/dbus-daemon --session --print-address --fork >/tmp/session_appmgr 2>/tmp/appnavi-wayland/session-dbus.err
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr)
$BB ln -sf /app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png /tmp/front_lcd.png
cat >/tmp/appnavi-weston.ini <<'EOF'
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
/usr/bin/weston-headless --config=/tmp/appnavi-weston.ini --use-pixman --width=1920 --height=720 --socket=wayland-0 --idle-time=0 --debug >/tmp/appnavi-wayland/weston.log 2>&1 &
WPID=$!
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -S /run/user/root/wayland-0 ] && break
  $BB sleep 1
done
[ -S /run/user/root/wayland-0 ] || { echo NO_WAYLAND_SOCKET; exit 21; }
cd /navi/Bin || exit 22
$BB timeout 150 /navi/Bin/AppNavi >/tmp/appnavi-wayland/app.log 2>&1 &
APID=$!
echo APPNAVI_WRAPPER_PID=$APID
$BB sleep 120
$BB ps | $BB grep -E 'weston-headless|AppNavi' | $BB grep -v grep
$BB kill $APID 2>/dev/null
wait $APID 2>/dev/null
echo APPNAVI_STOPPED
echo APPNAVI_PROTOCOL_EVENTS
$BB grep -E 'ivi_|wl_surface|wl_buffer|wl_compositor|xdg_|shell_surface' /tmp/appnavi-wayland/app.log | $BB tail -n 500
echo APPNAVI_LOG_TAIL
$BB tail -n 800 /tmp/appnavi-wayland/app.log
echo WESTON_LOG_TAIL
$BB tail -n 500 /tmp/appnavi-wayland/weston.log
echo DBUS_ERRORS
$BB cat /tmp/appnavi-wayland/system-dbus.err /tmp/appnavi-wayland/session-dbus.err
$BB kill $WPID 2>/dev/null
wait $WPID 2>/dev/null
exit 0
