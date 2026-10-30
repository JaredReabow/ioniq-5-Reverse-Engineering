#!/bin/busybox sh
# Reproduce the known-working valet-stub recipe, with the gpio adaptor, and print
# protocol marker counts instead of the large screenshot payload.
BB=/bin/busybox
$BB mkdir -p /tmp/dltpipes /rw_data/dlt
$BB printf 'ECUId = MANGO\nPrintASCII = 1\nLoggingMode = 0\nLoggingLevel = 7\nPersistanceStoragePath = /rw_data/dlt\n' >/tmp/dlt-test.conf
/usr/bin/dlt-daemon -c /tmp/dlt-test.conf >/tmp/dlt-daemon.log 2>&1 &
DPID=$!
$BB rm -f /tmp/session_appmgr
$BB sh /appnavi-valet2-probe.sh &
PROBE_PID=$!
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -s /tmp/session_appmgr ] && break
  $BB sleep 1
done
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr)
/dbus-bool-stub \
  com.lge.hkmc.avn.appfunc.AppStandbyClock \
  /com/lge/hkmc/avn/appfunc/appInterface \
  com.lge.hkmc.avn.appfunc.appInterface \
  NotifyValetStatus false >/tmp/valet-stub.log 2>&1 &
STUB_PID=$!
wait "$PROBE_PID"
echo VALET2_PROBE_RC=$?
L=/tmp/appnavi-render/appnavi.log
for t in wl_compositor ivi_application wl_surface create_surface surface_create attach commit; do
  echo "MARK $t=$($BB grep -ac $t $L 2>/dev/null)"
done
echo "MARK gpio440=$($BB grep -ac gpio440 $L 2>/dev/null)"
echo "MARK weston_ids=$($BB grep -ac 'Surface id' /tmp/appnavi-render/weston.log 2>/dev/null)"
for t in surface_create ivi_surface attach commit; do
  echo "WESTON $t=$($BB grep -ac $t /tmp/appnavi-render/weston.log 2>/dev/null)"
done
$BB grep -a 'surface_create\|Surface id' /tmp/appnavi-render/weston.log 2>/dev/null | $BB head -4
$BB grep -a 'Surface id' /tmp/appnavi-render/weston.log 2>/dev/null | $BB head -4
$BB kill -9 "$STUB_PID" "$DPID" 2>/dev/null
$BB killall -9 dbus-bool-stub dlt-daemon 2>/dev/null
exit 0
