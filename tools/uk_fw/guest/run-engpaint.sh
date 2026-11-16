#!/bin/busybox sh
# Engineering-mode paint diagnostic. Runs the proven engdata chain (which already
# exports WAYLAND_DEBUG=1 and the software-GL environment), but preloads a stderr
# tee so each process's stderr lands in /tmp/stderr-<pid>.log. AppEngineerMode is
# launched via the launcher, then we read its own WAYLAND_DEBUG traffic to decide
# whether it ever attaches/commits a buffer (or does ivi_share surface work).
# Finally each post-launch surface is placed and captured to /dev/ttyS2.
BB=/bin/busybox
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
export LD_PRELOAD=/stderr-tee-pid.so
sh /run-engdata-chain.sh >/tmp/chainpaint.out 2>&1 &
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
echo "ENG=${P:-none} base=$BASE now=$($BB grep -ac 'Surface id(' $W 2>/dev/null) req=$n"
echo "ENG_UID=$($BB grep -E '^Uid' /proc/$P/status 2>/dev/null)"
# Let software render + data queries + PIN screen settle.
$BB sleep 70
echo "=== WESTON_SURFACE_LIST ==="
$BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -30
echo "=== STDERR_PID_FILES ==="
$BB ls -la /tmp/stderr-*.log 2>/dev/null
if [ -n "$P" ]; then
  echo "=== ENG_STDERR_SIZE $($BB wc -c < /tmp/stderr-$P.log 2>/dev/null || echo 0) ==="
  echo "--- wayland protocol traffic (attach/commit/share/create) in eng stderr ---"
  $BB grep -aE 'attach|commit|create_buffer|create_pool|share_surface|ivi_share|wl_surface|wl_shm|damage|\.frame|create_surface|wl_egl|drm' /tmp/stderr-$P.log 2>/dev/null | $BB head -100
  echo "--- total counts in eng stderr ---"
  echo "attach=$($BB grep -ac 'attach' /tmp/stderr-$P.log 2>/dev/null) commit=$($BB grep -ac 'commit' /tmp/stderr-$P.log 2>/dev/null) share=$($BB grep -ac 'share_surface' /tmp/stderr-$P.log 2>/dev/null) create_buffer=$($BB grep -ac 'create_buffer' /tmp/stderr-$P.log 2>/dev/null) surface_lines=$($BB grep -ac 'surface' /tmp/stderr-$P.log 2>/dev/null)"
  echo "--- last 60 lines of eng stderr (GL/Qt errors) ---"
  $BB tail -60 /tmp/stderr-$P.log 2>/dev/null | $BB cut -c1-180
fi
echo "=== DLT_QML_LOG ==="
$BB grep -a 'qmlLog' $D 2>/dev/null | $BB cut -c1-220 | $BB tail -60
echo "=== DLT_APPE_TAIL ==="
$BB grep -a 'APPE' $D 2>/dev/null | $BB tail -40 | $BB cut -c1-200
echo "=== DLT_GL_ERR_OR_TEXTURE ==="
$BB grep -aiE 'Fail|error|texture|not a function|undefined|Image' $D 2>/dev/null | $BB grep -avi 'Pending Err' | $BB tail -30 | $BB cut -c1-200
echo "=== LAUNCHER_ENG ==="
$BB grep -aiE '301|Engineer|AppEngineerMode' $L 2>/dev/null | $BB tail -20 | $BB cut -c1-160

# Capture each surface. Control: home 2080. Then each unique surface created
# after the launch (the engineering window's own surfaces).
cap() {
  local id="$1"
  echo "SURF_CAPTURE_BEGIN $id" > /dev/ttyS2
  /usr/bin/ivi-wm "$id" >/dev/null 2>&1
  $BB sleep 6
  $BB rm -f /tmp/wayland-screenshot.png
  $BB timeout 25 /usr/libexec/weston-screenshooter >/dev/null 2>&1
  if [ -f /tmp/wayland-screenshot.png ]; then
    echo "SURF_SIZE $id $($BB wc -c < /tmp/wayland-screenshot.png)" > /dev/ttyS2
    $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2
    echo "" > /dev/ttyS2
  else
    echo "SURF_SIZE $id 0" > /dev/ttyS2
  fi
  echo "SURF_CAPTURE_END $id" > /dev/ttyS2
}
cap 2080
for S in $($BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -n +$((BASE+1)) | $BB sed 's/.*Surface id(\([0-9]*\)).*/\1/' | $BB sort -u); do
  [ -n "$S" ] && cap "$S"
done
echo DONE
