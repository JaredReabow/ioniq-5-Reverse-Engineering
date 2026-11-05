#!/bin/busybox sh
# Engineering-mode paint diagnostic v3. Capture the app's full stderr (which is
# /dev/null'd by the launcher) via strace write(2, ...), reassemble it, and dump
# it over ttyS2 for host parsing. Then fix the screenshot path (weston-screenshooter
# writes "wayland-screenshot.png" to cwd, so cd /tmp first).
BB=/bin/busybox
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
sh /run-engdata-chain.sh >/tmp/chainpaint3.out 2>&1 &
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
SPID=""
if [ -n "$P" ]; then
  /usr/bin/strace -f -e trace=write -s 400 -o /tmp/eng-strace.log -p "$P" >/dev/null 2>&1 &
  SPID=$!
  echo "STRACE_PID=$SPID"
fi
$BB sleep 70
[ -n "$SPID" ] && $BB kill -9 $SPID 2>/dev/null
echo "=== WESTON_SURFACE_LIST ==="
$BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -30
echo "=== STRACE_RAW_SIZE $($BB wc -c < /tmp/eng-strace.log 2>/dev/null || echo 0) ==="
# Reassemble every write(2, "...") string = the app's full stderr (WAYLAND_DEBUG
# fragments + any Qt/GL errors), then dump it losslessly over ttyS2.
$BB grep -a 'write(2, "' /tmp/eng-strace.log 2>/dev/null | $BB sed 's/^.*write(2, "//; s/", [0-9]*.*$//' | $BB tr -d '\n' > /tmp/wl-debug.txt
echo "=== WLDEBUG_SIZE $($BB wc -c < /tmp/wl-debug.txt 2>/dev/null || echo 0) ==="
echo "--- reassembled stderr: protocol keyword counts ---"
echo "attach=$($BB grep -ac 'attach' /tmp/wl-debug.txt 2>/dev/null) commit=$($BB grep -ac 'commit' /tmp/wl-debug.txt 2>/dev/null) surface=$($BB grep -ac 'surface' /tmp/wl-debug.txt 2>/dev/null) share_surface=$($BB grep -ac 'share_surface' /tmp/wl-debug.txt 2>/dev/null) create_buffer=$($BB grep -ac 'create_buffer' /tmp/wl-debug.txt 2>/dev/null) create_surface=$($BB grep -ac 'create_surface' /tmp/wl-debug.txt 2>/dev/null) delete_id=$($BB grep -ac 'delete_id' /tmp/wl-debug.txt 2>/dev/null)"
echo "--- first 1200 chars of reassembled stderr ---"
$BB head -c 1200 /tmp/wl-debug.txt 2>/dev/null
echo ""
echo "--- last 1200 chars of reassembled stderr ---"
$BB tail -c 1200 /tmp/wl-debug.txt 2>/dev/null
echo ""
echo "=== WLDEBUG_B64_BEGIN ===" > /dev/ttyS2
$BB base64 /tmp/wl-debug.txt > /dev/ttyS2 2>/dev/null
echo "=== WLDEBUG_B64_END ===" > /dev/ttyS2
echo "=== DLT_QML_LOG ==="
$BB grep -a 'qmlLog' $D 2>/dev/null | $BB cut -c1-220 | $BB tail -50
echo "=== DLT_GL_TEXTURE_ERR ==="
$BB grep -aiE 'Fail|texture|EGL|GL error|scene graph|render|QML' $D 2>/dev/null | $BB grep -avi 'Pending Err' | $BB tail -20 | $BB cut -c1-200
# Screenshots (fixed: weston-screenshooter writes to cwd).
cd /tmp
/usr/bin/ivi-wm 2080 >/dev/null 2>&1; $BB sleep 6
$BB rm -f /tmp/wayland-screenshot.png; $BB timeout 25 /usr/libexec/weston-screenshooter >/tmp/shot-err.txt 2>&1
echo "SURF_SHOT 2080 size=$($BB wc -c < /tmp/wayland-screenshot.png 2>/dev/null || echo 0) err=$($BB head -c 80 /tmp/shot-err.txt 2>/dev/null)"
if [ -f /tmp/wayland-screenshot.png ]; then echo "SHOT_B64_BEGIN 2080" > /dev/ttyS2; $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2; echo "" > /dev/ttyS2; echo "SHOT_B64_END 2080" > /dev/ttyS2; fi
for S in $($BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -n +$((BASE+1)) | $BB sed 's/.*Surface id(\([0-9]*\)).*/\1/' | $BB sort -u); do
  [ -n "$S" ] || continue
  /usr/bin/ivi-wm "$S" >/dev/null 2>&1; $BB sleep 6
  $BB rm -f /tmp/wayland-screenshot.png; $BB timeout 25 /usr/libexec/weston-screenshooter >/tmp/shot-err.txt 2>&1
  echo "SURF_SHOT $S size=$($BB wc -c < /tmp/wayland-screenshot.png 2>/dev/null || echo 0) err=$($BB head -c 80 /tmp/shot-err.txt 2>/dev/null)"
  if [ -f /tmp/wayland-screenshot.png ]; then echo "SHOT_B64_BEGIN $S" > /dev/ttyS2; $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2; echo "" > /dev/ttyS2; echo "SHOT_B64_END $S" > /dev/ttyS2; fi
done
echo DONE
