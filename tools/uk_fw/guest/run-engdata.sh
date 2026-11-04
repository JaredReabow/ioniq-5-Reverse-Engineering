#!/bin/sh
# Launch engineering mode against the eng-data chain and capture the result.
# Streams up to two screenshots over /dev/ttyS2, each wrapped in ASCII markers,
# plus text evidence on the console.
BB=/bin/busybox
cd /tmp
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
sh /run-engdata-chain.sh >/tmp/chainengdata.out 2>&1 &
W=/tmp/launcher-chain/weston.log; L=/tmp/launcher-chain/launcher.log
S=/tmp/launcher-chain/eng-data-sim.log; D=/tmp/launcher-chain/dlt.log
i=0; while [ $i -lt 12 ]; do $BB sleep 10; i=$((i+1)); $BB grep -aq 'Surface id(2080)' $W 2>/dev/null && break; done
echo "HOME_AT=$((i*10))s"
$BB mkdir -p /tmp/app/bin
$BB cp -f /app/bin/AppEngineerMode /tmp/app/bin/AppEngineerMode
$BB chmod 755 /tmp/app/bin/AppEngineerMode
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr 2>/dev/null)
$BB sleep 10
n=0; P=""
while [ $n -lt 15 ]; do
  n=$((n+1))
  /usr/bin/dbus-send --session --print-reply --dest=com.lge.avn.applauncher /Request com.lge.avn.applauncher.request.launch int32:301 string:AppEngineerMode string:/tmp/app/bin/AppEngineerMode >/dev/null 2>&1
  $BB sleep 12
  P=$($BB pidof AppEngineerMode)
  [ -n "$P" ] && { echo "ENG=$P after_req=$n"; break; }
  echo "req=$n no_AppEngineerMode_yet"
done
[ -z "$P" ] && echo "ENG=none after $n requests"
# Give the six asks time to be answered and the QML body to re-render under
# software rendering (longer than the previous 40 s).
$BB sleep 70
echo "=== WESTON_SURFACE_LIST ==="
$BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -25
echo "=== ENG_DATA_SIM_LOG ==="
$BB cat "$S" 2>/dev/null
echo "=== DLT_APPE_TAIL ==="
$BB grep -a 'APPE' $D 2>/dev/null | $BB tail -60 | $BB cut -c1-200
echo "=== DLT_RESP ==="
$BB grep -aiE 'Pending Err|Data Null|Receive |ok$|Null' $D 2>/dev/null | $BB tail -40 | $BB cut -c1-200

# Candidate surfaces: the last AppEngineerMode window the ivi window manager
# created, and the newest surface overall. Screenshot each.
ENGSID=$($BB grep -a 'wm_window_created' $D 2>/dev/null | $BB grep -a 'AppEngineerMode' | $BB tail -1 | $BB sed 's/.*SID(\([0-9]*\)).*/\1/')
NEWSID=$($BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -1 | $BB sed 's/.*Surface id(\([0-9]*\)).*/\1/')
echo "ENGSID=$ENGSID NEWSID=$NEWSID"
if [ -n "$ENGSID" ] && [ "$ENGSID" != "$NEWSID" ]; then
  echo "PLACING_ENG=$ENGSID"; /usr/bin/ivi-wm $ENGSID >/dev/null 2>&1
  $BB sleep 6
  $BB rm -f /tmp/wayland-screenshot.png; $BB timeout 25 /usr/libexec/weston-screenshooter >/dev/null 2>&1
  $BB cp /tmp/wayland-screenshot.png /tmp/shot-eng.png 2>/dev/null
  [ -f /tmp/shot-eng.png ] && { echo "=== SHOT_ENG_BEGIN ==="; $BB base64 /tmp/shot-eng.png > /dev/ttyS2; echo "=== SHOT_ENG_END ==="; }
  echo "SHOT_ENG=$($BB wc -c < /tmp/shot-eng.png 2>/dev/null || echo none)"
fi
if [ -n "$NEWSID" ]; then
  echo "PLACING_NEW=$NEWSID"; /usr/bin/ivi-wm $NEWSID >/dev/null 2>&1
  $BB sleep 6
  $BB rm -f /tmp/wayland-screenshot.png; $BB timeout 25 /usr/libexec/weston-screenshooter >/dev/null 2>&1
  $BB cp /tmp/wayland-screenshot.png /tmp/shot-new.png 2>/dev/null
  [ -f /tmp/shot-new.png ] && { echo "=== SHOT_NEW_BEGIN ==="; $BB base64 /tmp/shot-new.png > /dev/ttyS2; echo "=== SHOT_NEW_END ==="; }
  echo "SHOT_NEW=$($BB wc -c < /tmp/shot-new.png 2>/dev/null || echo none)"
fi
echo DONE
