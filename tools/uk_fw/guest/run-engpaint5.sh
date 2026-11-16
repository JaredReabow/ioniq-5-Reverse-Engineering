#!/bin/busybox sh
# Engineering-mode paint diagnostic v5: the single-change test. Force the Qt
# Quick SOFTWARE scene-graph renderer (the path that made the home screen draw
# geometry into a wl_shm buffer and attach/commit, per CHANGELOG 2.96.0), then
# see whether the engineering PIN screen paints. Everything else unchanged.
BB=/bin/busybox
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
export QT_QUICK_BACKEND=software
sh /run-engdata-chain.sh >/tmp/chainpaint5.out 2>&1 &
W=/tmp/launcher-chain/weston.log; L=/tmp/launcher-chain/launcher.log
D=/tmp/launcher-chain/dlt.log
i=0; while [ $i -lt 14 ]; do $BB sleep 10; i=$((i+1)); $BB grep -aq 'Surface id(2080)' $W 2>/dev/null && break; done
echo "HOME_AT=$((i*10))s"
$BB mkdir -p /tmp/app/bin
$BB cp -f /app/bin/AppEngineerMode /tmp/app/bin/AppEngineerMode
$BB chmod 755 /tmp/app/bin/AppEngineerMode
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr 2>/dev/null)
BASE=$($BB grep -ac 'Surface id(' $W 2>/dev/null)
n=0; P=""
while [ $n -lt 12 ]; do
  n=$((n+1))
  /usr/bin/dbus-send --session --print-reply --dest=com.lge.avn.applauncher /Request com.lge.avn.applauncher.request.launch int32:301 string:AppEngineerMode string:/tmp/app/bin/AppEngineerMode >/dev/null 2>&1
  $BB sleep 12
  P=$($BB pidof AppEngineerMode)
  [ -n "$P" ] && break
  echo "req=$n no_eng_yet"
done
echo "ENG=${P:-none} base=$BASE req=$n"
$BB sleep 70
echo "=== WESTON_SURFACE_LIST ==="
$BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -30
cd /tmp
# capture home (control) and each post-launch surface
/usr/bin/ivi-wm 2080 >/dev/null 2>&1; $BB sleep 6
$BB rm -f /tmp/wayland-screenshot.png; $BB timeout 25 /usr/libexec/weston-screenshooter >/dev/null 2>&1
echo "SURF_SHOT 2080 size=$($BB wc -c < /tmp/wayland-screenshot.png 2>/dev/null || echo 0)"
if [ -f /tmp/wayland-screenshot.png ]; then echo "SHOT_B64_BEGIN 2080" > /dev/ttyS2; $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2; echo "" > /dev/ttyS2; echo "SHOT_B64_END 2080" > /dev/ttyS2; fi
for S in $($BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -n +$((BASE+1)) | $BB sed 's/.*Surface id(\([0-9]*\)).*/\1/' | $BB sort -u); do
  [ -n "$S" ] || continue
  /usr/bin/ivi-wm "$S" >/dev/null 2>&1; $BB sleep 6
  $BB rm -f /tmp/wayland-screenshot.png; $BB timeout 25 /usr/libexec/weston-screenshooter >/dev/null 2>&1
  echo "SURF_SHOT $S size=$($BB wc -c < /tmp/wayland-screenshot.png 2>/dev/null || echo 0)"
  if [ -f /tmp/wayland-screenshot.png ]; then echo "SHOT_B64_BEGIN $S" > /dev/ttyS2; $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2; echo "" > /dev/ttyS2; echo "SHOT_B64_END $S" > /dev/ttyS2; fi
done
echo "=== DLT_QML_LOG ==="
$BB grep -a 'qmlLog' $D 2>/dev/null | $BB cut -c1-220 | $BB tail -40
echo "=== DLT_TEXTURE_FAIL ==="
$BB grep -aicE 'Fail|texture' $D 2>/dev/null
echo DONE
