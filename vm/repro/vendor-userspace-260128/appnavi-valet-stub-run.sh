#!/bin/busybox sh
# VM-only exact AppNavi experiment: provide the one boolean D-Bus reply whose
# absent argument causes getValetModeOnOffState() to dereference an empty list.
BB=/bin/busybox
$BB mkdir -p /tmp/dltpipes /rw_data/dlt
$BB printf 'ECUId = MANGO\nPrintASCII = 1\nLoggingMode = 0\nLoggingLevel = 7\nPersistanceStoragePath = /rw_data/dlt\n' >/tmp/dlt-test.conf
/usr/bin/dlt-daemon -c /tmp/dlt-test.conf >/tmp/dlt-daemon.log 2>&1 &
DPID=$!
$BB rm -f /tmp/session_appmgr
$BB sed \
  -e 's/timeout 45/timeout 100/' \
  -e 's/for n in 1 2 3; do/for n in 1 2 3 4 5 6 7 8; do/' \
  -e 's#/ivi-fg-navi >>#/ivi-link-navi-widget-v2 >>#' \
  /appnavi-strace-no-appmgr-probe.sh >/tmp/appnavi-valet-stub-probe.sh
$BB chmod +x /tmp/appnavi-valet-stub-probe.sh
$BB sh /tmp/appnavi-valet-stub-probe.sh &
PROBE_PID=$!
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -s /tmp/session_appmgr ] && break
  $BB sleep 1
done
if [ ! -s /tmp/session_appmgr ]; then
  echo VALET_STUB_NO_SESSION_BUS
  $BB kill -9 "$PROBE_PID" "$DPID" 2>/dev/null
  exit 31
fi
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr)
/dbus-bool-stub \
  com.lge.hkmc.avn.appfunc.AppStandbyClock \
  /com/lge/hkmc/avn/appfunc/appInterface \
  com.lge.hkmc.avn.appfunc.appInterface \
  NotifyValetStatus false >/tmp/valet-stub.log 2>&1 &
STUB_PID=$!
wait "$PROBE_PID"
PROBE_RC=$?
echo NAVI_WIDGET_FG_LOG_BEGIN
$BB cat /tmp/appnavi-render/ivi-fg.log
echo NAVI_WIDGET_FG_LOG_END
if [ -f /tmp/appnavi-render/shot/wayland-screenshot.png ]; then
  echo NAVI_SCREENSHOT_SHA256_BEGIN
  $BB sha256sum /tmp/appnavi-render/shot/wayland-screenshot.png
  echo NAVI_SCREENSHOT_SHA256_END
  echo NAVI_SCREENSHOT_BASE64_BEGIN
  $BB base64 /tmp/appnavi-render/shot/wayland-screenshot.png
  echo NAVI_SCREENSHOT_BASE64_END
fi
echo VALET_STUB_LOG_BEGIN
$BB cat /tmp/valet-stub.log
echo VALET_STUB_LOG_END
echo DLT_DAEMON_LOG_BEGIN
$BB tail -n 30000 /tmp/dlt-daemon.log
echo DLT_DAEMON_LOG_END
$BB kill -9 "$STUB_PID" "$DPID" 2>/dev/null
$BB killall -9 dbus-bool-stub dlt-daemon 2>/dev/null
wait "$STUB_PID" 2>/dev/null
wait "$DPID" 2>/dev/null
exit "$PROBE_RC"
