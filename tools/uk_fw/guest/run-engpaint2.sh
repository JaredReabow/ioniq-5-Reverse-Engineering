#!/bin/busybox sh
# Engineering-mode paint diagnostic v2. Captures the app's own WAYLAND_DEBUG
# traffic with strace (the launcher discards child stderr, but the libwayland
# debug text still passes through write(2) before /dev/null swallows it), then
# places and captures each post-launch surface exactly as run-engdata.sh did.
BB=/bin/busybox
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
sh /run-engdata-chain.sh >/tmp/chainpaint2.out 2>&1 &
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
# Attach strace as soon as the PID exists, before the surfaces appear.
if [ -n "$P" ]; then
  /usr/bin/strace -f -e trace=write -s 400 -o /tmp/eng-strace.log -p "$P" >/dev/null 2>&1 &
  SPID=$!
  echo "STRACE_PID=$SPID"
else
  SPID=""
fi
$BB sleep 70
[ -n "$SPID" ] && $BB kill -9 $SPID 2>/dev/null
echo "=== WESTON_SURFACE_LIST ==="
$BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -30
echo "=== STRACE_SIZE $($BB wc -c < /tmp/eng-strace.log 2>/dev/null || echo 0) ==="
echo "--- wayland protocol lines in eng strace (attach/commit/share/create) ---"
$BB grep -aE 'attach|commit|create_buffer|create_pool|share_surface|ivi_share|wl_surface|wl_shm|\.damage|create_surface|wl_egl|wl_drm|dma' /tmp/eng-strace.log 2>/dev/null | $BB head -120
echo "--- counts ---"
echo "attach=$($BB grep -ac 'attach' /tmp/eng-strace.log 2>/dev/null) commit=$($BB grep -ac 'commit' /tmp/eng-strace.log 2>/dev/null) share=$($BB grep -ac 'share_surface' /tmp/eng-strace.log 2>/dev/null) create_buffer=$($BB grep -ac 'create_buffer' /tmp/eng-strace.log 2>/dev/null) surface=$($BB grep -ac 'surface' /tmp/eng-strace.log 2>/dev/null)"
echo "--- first 30 wayland-ish lines (raw) ---"
$BB grep -aE 'wl_display|get_registry|wl_compositor|wl_surface|wl_registry|wl_shm|ivi_share|wl_egl' /tmp/eng-strace.log 2>/dev/null | $BB head -30 | $BB cut -c1-220
echo "=== DLT_QML_LOG ==="
$BB grep -a 'qmlLog' $D 2>/dev/null | $BB cut -c1-220 | $BB tail -50
echo "=== DLT_GL_TEXTURE ==="
$BB grep -aiE 'Fail|texture|EGL|GL|scene graph|render' $D 2>/dev/null | $BB tail -20 | $BB cut -c1-200

# Screenshot each surface exactly as run-engdata.sh did (no function, no local).
shot() {
  $BB rm -f /tmp/wayland-screenshot.png
  $BB timeout 25 /usr/libexec/weston-screenshooter >/tmp/shot-err.txt 2>&1
  echo "SURF_SHOT $1 size=$($BB wc -c < /tmp/wayland-screenshot.png 2>/dev/null || echo 0) err=$($BB head -c 120 /tmp/shot-err.txt 2>/dev/null)"
  if [ -f /tmp/wayland-screenshot.png ]; then
    echo "SURF_B64_BEGIN $1" > /dev/ttyS2
    $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2
    echo "" > /dev/ttyS2
    echo "SURF_B64_END $1" > /dev/ttyS2
  fi
}
/usr/bin/ivi-wm 2080 >/dev/null 2>&1; $BB sleep 6; shot 2080
for S in $($BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -n +$((BASE+1)) | $BB sed 's/.*Surface id(\([0-9]*\)).*/\1/' | $BB sort -u); do
  [ -n "$S" ] && { /usr/bin/ivi-wm "$S" >/dev/null 2>&1; $BB sleep 6; shot "$S"; }
done
echo DONE
