#!/bin/busybox sh
# v8: discover the app's real session-bus name, then deliver appbase.show_window_fg
# to it (the handshake the real ApplicationManager performs to show a launched app).
BB=/bin/busybox
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
sh /run-engdata-chain.sh >/tmp/chainpaint8.out 2>&1 &
W=/tmp/launcher-chain/weston.log; D=/tmp/launcher-chain/dlt.log
SB=/tmp/launcher-chain/session-bus.log
i=0; while [ $i -lt 14 ]; do $BB sleep 10; i=$((i+1)); $BB grep -aq 'Surface id(2080)' $W 2>/dev/null && break; done
echo "HOME_AT=$((i*10))s"
$BB mkdir -p /tmp/app/bin; $BB cp -f /app/bin/AppEngineerMode /tmp/app/bin/AppEngineerMode; $BB chmod 755 /tmp/app/bin/AppEngineerMode
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr 2>/dev/null)
BASE=$($BB grep -ac 'Surface id(' $W 2>/dev/null)
n=0; P=""
while [ $n -lt 12 ]; do
  n=$((n+1))
  /usr/bin/dbus-send --session --print-reply --dest=com.lge.avn.applauncher /Request com.lge.avn.applauncher.request.launch int32:301 string:AppEngineerMode string:/tmp/app/bin/AppEngineerMode >/dev/null 2>&1
  $BB sleep 12; P=$($BB pidof AppEngineerMode); [ -n "$P" ] && break
  echo "req=$n no_eng_yet"
done
echo "ENG=${P:-none} base=$BASE req=$n"
$BB sleep 70
echo "=== WESTON_SURFACE_LIST ==="
$BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -20
echo "=== BUS_NAME_DISCOVERY ==="
/usr/bin/dbus-send --session --print-reply --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>&1 | $BB grep -a 'string' | $BB cut -c1-200
echo "=== REGISTRATION_CALL_FROM_APP ==="
$BB grep -aiE 'member=registration' $SB 2>/dev/null | $BB tail -5 | $BB cut -c1-300
ENG_NAME=$($BB grep -ao 'com\.lge\.hkmc\.avn\.appfunc\.[A-Za-z]*[Ee]ngineer[A-Za-z]*' $SB 2>/dev/null | $BB sort -u | $BB head -1)
echo "ENG_NAME_DISCOVERED=${ENG_NAME:-none}"
cd /tmp
ENGSURF=$($BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -n +$((BASE+1)) | $BB sed 's/.*Surface id(\([0-9]*\)).*/\1/' | $BB sort -u | $BB tail -1)
echo "ENGSURF=${ENGSURF:-none}"
if [ -n "$ENGSURF" ]; then
  /usr/bin/ivi-wm "$ENGSURF" >/dev/null 2>&1; $BB sleep 6
  $BB rm -f /tmp/wayland-screenshot.png; $BB timeout 25 /usr/libexec/weston-screenshooter >/dev/null 2>&1
  echo "SURF_SHOT_BEFORE $ENGSURF size=$($BB wc -c < /tmp/wayland-screenshot.png 2>/dev/null || echo 0)"
  if [ -f /tmp/wayland-screenshot.png ]; then echo "SHOT_B64_BEGIN before" > /dev/ttyS2; $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2; echo "" > /dev/ttyS2; echo "SHOT_B64_END before" > /dev/ttyS2; fi
fi
# Deliver show_window_fg to the discovered name across path candidates.
for N in "${ENG_NAME:-none}" com.lge.hkmc.avn.appfunc.AppEngineerMode; do
  for PT in /com/lge/hkmc/avn/appfunc/AppEngineerMode /com/lge/hkmc/avn/appfunc/engineermode /com/lge/hkmc/avn/appfunc/appInterface; do
    echo "=== SHOW_WINDOW_FG dest=$N path=$PT ==="
    /usr/bin/dbus-send --session --print-reply --dest="$N" "$PT" com.lge.avn.appmanager.appbase.show_window_fg int32:0 int32:0 int32:0 int32:0 2>&1 | $BB cut -c1-220
    $BB sleep 3
  done
done
$BB sleep 8
if [ -n "$ENGSURF" ]; then
  /usr/bin/ivi-wm "$ENGSURF" >/dev/null 2>&1; $BB sleep 6
  $BB rm -f /tmp/wayland-screenshot.png; $BB timeout 25 /usr/libexec/weston-screenshooter >/dev/null 2>&1
  echo "SURF_SHOT_AFTER $ENGSURF size=$($BB wc -c < /tmp/wayland-screenshot.png 2>/dev/null || echo 0)"
  if [ -f /tmp/wayland-screenshot.png ]; then echo "SHOT_B64_BEGIN after" > /dev/ttyS2; $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2; echo "" > /dev/ttyS2; echo "SHOT_B64_END after" > /dev/ttyS2; fi
fi
echo "=== DLT_QML_TAIL ==="
$BB grep -a 'qmlLog' $D 2>/dev/null | $BB cut -c1-200 | $BB tail -25
echo DONE
