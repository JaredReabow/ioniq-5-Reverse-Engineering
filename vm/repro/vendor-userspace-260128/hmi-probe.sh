#!/bin/busybox sh
BB=/bin/busybox
$BB cp /etc/passwd.legacy /tmp/passwd
echo 'xuser:x:1000:100:xuser:/home/xuser:/bin/sh' >>/tmp/passwd
echo 'byungsu:x:1001:100:byungsu:/home/byungsu:/bin/sh' >>/tmp/passwd
$BB mkdir -p /run/dbus /run/lock /var/run/dbus /rw_data/var/volatile/log /rw_data/var/volatile/tmp
/usr/bin/dbus-uuidgen --ensure
/usr/bin/dbus-daemon --system --fork 2>/tmp/dbus.err
echo DBUS_RC=$?
$BB ln -s qml_new2.0 /app/share/AppHomeScreen/qml
$BB mount -o bind /system/new_gui/new2.0/hmc/night /app/share/images/hmc
echo RESOURCE_BIND_RC=$?
$BB ls -l /app/share/images/hmc/split/split_btn_off_n.png.astc.header /navi/Bin/AppNavi
export LD_LIBRARY_PATH=/app/lib:/usr/lib:/lib:/navi/Lib:/navi/navi/Lib
export XDG_RUNTIME_DIR=/run/user/root
export QT_QPA_PLATFORM=offscreen
export QSG_RENDER_LOOP=basic
export QV4_NO_SSA=1
export QV4_FORCE_INTERPRETER=1
$BB timeout 35 /app/bin/AppHomeScreen >/tmp/apphome.log 2>&1
echo APP_RC=$?
echo UI_GATE_LINES
$BB grep -E 'main.qml|QtMsg|OpenGL|context|QQml|QML|EGL|ImageProvider|File not found|failed|Failed|ASTC' /tmp/apphome.log | $BB head -n 400
echo DBUS_ERRORS
$BB cat /tmp/dbus.err
