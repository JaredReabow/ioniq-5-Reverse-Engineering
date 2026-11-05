#!/bin/busybox sh
# v6: verify whether QT_QUICK_BACKEND=software actually reaches the app, and
# whether it changes the app's wayland traffic. Dumps /proc/<pid>/environ and
# straces write(2, ...) again.
BB=/bin/busybox
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
export QT_QUICK_BACKEND=software
sh /run-engdata-chain.sh >/tmp/chainpaint6.out 2>&1 &
W=/tmp/launcher-chain/weston.log; D=/tmp/launcher-chain/dlt.log
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
if [ -n "$P" ]; then
  /usr/bin/strace -f -e trace=write -s 400 -o /tmp/eng-strace.log -p "$P" >/dev/null 2>&1 &
  SPID=$!
  echo "=== ENG_ENVIRON (QT/QPA/QUICK vars) ==="
  $BB tr '\0' '\n' < /proc/$P/environ 2>/dev/null | $BB grep -aE 'QT_|QSG_|GALLIUM|LIBGL|WAYLAND|LD_' | $BB cut -c1-120
fi
$BB sleep 70
[ -n "$SPID" ] && $BB kill -9 $SPID 2>/dev/null
echo "=== WESTON_SURFACE_LIST ==="
$BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -30
echo "=== STRACE_RAW_SIZE $($BB wc -c < /tmp/eng-strace.log 2>/dev/null || echo 0) ==="
$BB grep -a 'write(2,' /tmp/eng-strace.log 2>/dev/null > /tmp/wl-raw.txt
echo "=== WL_RAW_SIZE $($BB wc -c < /tmp/wl-raw.txt 2>/dev/null || echo 0) LINES $($BB wc -l < /tmp/wl-raw.txt 2>/dev/null) ==="
$BB head -40 /tmp/wl-raw.txt 2>/dev/null | $BB cut -c1-160
echo "=== WL_RAW_B64_BEGIN ===" > /dev/ttyS2
$BB base64 /tmp/wl-raw.txt > /dev/ttyS2 2>/dev/null
echo "=== WL_RAW_B64_END ===" > /dev/ttyS2
echo DONE
