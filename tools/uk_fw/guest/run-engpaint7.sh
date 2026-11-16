#!/bin/busybox sh
# v7: test the appbase handshake hypothesis. Dump the session bus names and the
# app's registration call to learn its servicename/objectpath, then deliver
# com.lge.avn.appmanager.appbase.show_window_fg to the app and re-capture.
BB=/bin/busybox
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
sh /run-engdata-chain.sh >/tmp/chainpaint7.out 2>&1 &
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
echo "=== SESSION_BUS_LISTNAMES ==="
/usr/bin/dbus-send --session --print-reply --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.ListNames 2>&1 | $BB cut -c1-400
echo "=== SESSION_BUS_REGISTRATION_LINES ==="
$BB grep -aiE 'registration|appfunc|appbase|AppEngineerMode|engineermode' $SB 2>/dev/null | $BB tail -30 | $BB cut -c1-200
echo "=== WESTON_SURFACE_LIST ==="
$BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -20
cd /tmp
# capture engineering surface BEFORE the show call
for S in $($BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -n +$((BASE+1)) | $BB sed 's/.*Surface id(\([0-9]*\)).*/\1/' | $BB sort -u | $BB tail -1); do
  /usr/bin/ivi-wm "$S" >/dev/null 2>&1; $BB sleep 6
  $BB rm -f /tmp/wayland-screenshot.png; $BB timeout 25 /usr/libexec/weston-screenshooter >/dev/null 2>&1
  echo "SURF_SHOT_BEFORE $S size=$($BB wc -c < /tmp/wayland-screenshot.png 2>/dev/null || echo 0)"
  if [ -f /tmp/wayland-screenshot.png ]; then echo "SHOT_B64_BEGIN before-$S" > /dev/ttyS2; $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2; echo "" > /dev/ttyS2; echo "SHOT_B64_END before-$S" > /dev/ttyS2; fi
done
# deliver show_window_fg on the most likely appbase names/paths
for NAME in com.lge.hkmc.avn.appfunc com.lge.avn.appbase; do
  for PATH_ in /com/lge/hkmc/avn/appfunc/engineermode /com/lge/hkmc/avn/appfunc/AppEngineerMode; do
    echo "=== SHOW_WINDOW_FG dest=$NAME path=$PATH_ ==="
    /usr/bin/dbus-send --session --print-reply --dest="$NAME" "$PATH_" com.lge.avn.appmanager.appbase.show_window_fg int32:0 int32:0 int32:0 int32:0 2>&1 | $BB cut -c1-200
    $BB sleep 3
  done
done
$BB sleep 6
# capture engineering surface AFTER the show call
for S in $($BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -n +$((BASE+1)) | $BB sed 's/.*Surface id(\([0-9]*\)).*/\1/' | $BB sort -u | $BB tail -1); do
  /usr/bin/ivi-wm "$S" >/dev/null 2>&1; $BB sleep 6
  $BB rm -f /tmp/wayland-screenshot.png; $BB timeout 25 /usr/libexec/weston-screenshooter >/dev/null 2>&1
  echo "SURF_SHOT_AFTER $S size=$($BB wc -c < /tmp/wayland-screenshot.png 2>/dev/null || echo 0)"
  if [ -f /tmp/wayland-screenshot.png ]; then echo "SHOT_B64_BEGIN after-$S" > /dev/ttyS2; $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2; echo "" > /dev/ttyS2; echo "SHOT_B64_END after-$S" > /dev/ttyS2; fi
done
echo DONE
