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
cd /app/bin || exit 22
$BB timeout 130 /app/bin/AppLauncher 3 >/tmp/launcher-chain/launcher.log 2>&1 &
LPID=$!
echo APPLAUNCHER_WRAPPER_PID=$LPID
$BB sleep 25
echo DBUS_NAMES_BEFORE_NAVI
/usr/bin/dbus-send --session --print-reply --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames
echo APPNAVI_LAUNCH_REQUEST_BEGIN
/usr/bin/dbus-send --session --print-reply --dest=com.lge.avn.applauncher /Request com.lge.avn.applauncher.request.launch int32:30 string:AppNavi string:/navi/navi/Bin/AppNavi
NAVI_REQ_RC=$?
echo APPNAVI_LAUNCH_REQUEST_RC=$NAVI_REQ_RC
echo APPNAVI_LAUNCH_REQUEST_END
$BB sleep 80
for n in 1 2 3 4; do
  /ivi-fg >>/tmp/launcher-chain/ivi-fg.log 2>&1
  $BB sleep 2
done
echo PROCESS_LIST_BEGIN
$BB ps

echo PROCESS_LIST_END
$BB mkdir -p /tmp/launcher-chain/shot
cd /tmp/launcher-chain/shot
/usr/libexec/weston-screenshooter >/tmp/launcher-chain/screenshot.log 2>&1
$BB sleep 3
if [ -f /tmp/launcher-chain/shot/wayland-screenshot.png ]; then
  $BB sha256sum /tmp/launcher-chain/shot/wayland-screenshot.png
  echo SCREENSHOT_CAPTURED
fi
$BB kill $LPID 2>/dev/null
wait $LPID 2>/dev/null
echo LAUNCHER_STOPPED
echo APPLAUNCHER_APPNAVI_EVENTS_BEGIN
$BB grep -E 'AppNavi|AppID|QT_WAYLAND_SET_SURFACE_ID|REGISTERED|m_AppProcess->start' /tmp/launcher-chain/launcher.log
echo APPLAUNCHER_APPNAVI_EVENTS_END
echo LAUNCHER_LOG_BEGIN
$BB tail -n 700 /tmp/launcher-chain/launcher.log
echo LAUNCHER_LOG_END
echo LOG_DATA_LIST
$BB find /log_data -maxdepth 2 -type f -print
echo WESTON_SURFACE_EVENTS
$BB grep -E 'surface_create|ivi_hmi|ivi_application|wl_surface.*(attach|commit)|AppHome|AppNavi' /tmp/launcher-chain/weston.log | $BB tail -n 1000
echo WESTON_LOG_TAIL
$BB tail -n 800 /tmp/launcher-chain/weston.log
$BB cat /tmp/launcher-chain/ivi-fg.log /tmp/launcher-chain/screenshot.log /tmp/launcher-chain/system-dbus.err /tmp/launcher-chain/session-dbus.err
$BB kill $WPID 2>/dev/null
wait $WPID 2>/dev/null
exit 0
