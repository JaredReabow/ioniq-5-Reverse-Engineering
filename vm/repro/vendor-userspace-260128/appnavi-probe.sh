#!/bin/busybox sh
BB=/bin/busybox
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
export LD_LIBRARY_PATH=/opt/software-egl18/lib:/opt/software-egl/lib:/app/lib:/usr/lib:/lib:/navi/Lib:/navi/navi/Lib
export LIBGL_DRIVERS_PATH=/opt/software-egl18/dri
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=softpipe
export LP_NUM_THREADS=1
export XDG_RUNTIME_DIR=/run/user/root
export QT_QPA_PLATFORM=offscreen
export QV4_NO_SSA=1
export QV4_FORCE_INTERPRETER=1
$BB mkdir -p /run/dbus /run/lock /run/user/root /var/run/dbus /rw_data/var/volatile/log /rw_data/var/volatile/tmp /tmp/appnavi
$BB chmod 700 /run/user/root
/usr/bin/dbus-uuidgen --ensure
/usr/bin/dbus-daemon --system --fork 2>/tmp/appnavi/dbus.err
echo APPNAVI_LDD_BEGIN
/usr/bin/ldd /navi/Bin/AppNavi 2>&1
echo APPNAVI_LDD_END
cd /navi/Bin || exit 20
$BB timeout 60 /navi/Bin/AppNavi >/tmp/appnavi/app.log 2>&1
RC=$?
echo APPNAVI_RC=$RC
echo APPNAVI_LOG_BEGIN
$BB tail -n 600 /tmp/appnavi/app.log
echo APPNAVI_LOG_END
echo DBUS_ERRORS
$BB cat /tmp/appnavi/dbus.err
exit 0
