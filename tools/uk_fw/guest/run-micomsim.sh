#!/bin/busybox sh
# MICOM-simulator admission test v4 (clean): the chain's own AppLauncher already
# starts /app/bin/ApplicationManager, so do NOT start a second one. Launch
# engineering mode (appId 301) against the chain and observe whether the
# (already-running) manager stops logging "reply is not VALID" and delivers
# com.lge.avn.appmanager.appbase.show_window_fg. Captures over /dev/ttyS2.
BB=/bin/busybox
cd /tmp
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0
sh /run-engdata-chain.sh >/tmp/chainmicomsim.out 2>&1 &
W=/tmp/launcher-chain/weston.log; D=/tmp/launcher-chain/dlt.log
S=/tmp/launcher-chain/eng-data-sim.log; SB=/tmp/launcher-chain/session-bus.log
L=/tmp/launcher-chain/launcher.log
i=0; while [ $i -lt 14 ]; do $BB sleep 10; i=$((i+1)); $BB grep -aq 'Surface id(2080)' $W 2>/dev/null && break; done
echo "HOME_AT=$((i*10))s"
# Wait until AppLauncher has started the real ApplicationManager.
j=0; MP=""
while [ $j -lt 20 ]; do
  j=$((j+1))
  MP=$($BB pidof ApplicationManager)
  [ -n "$MP" ] && break
  $BB sleep 5
done
echo "APPM_PID=$MP wait=$((j*5))s"

export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/app/bin
export LD_LIBRARY_PATH=/opt/software-egl18/lib:/opt/software-egl/lib:/app/lib:/usr/lib:/lib:/navi/Lib:/navi/navi/Lib
export LIBGL_DRIVERS_PATH=/opt/software-egl18/dri
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=softpipe
export LP_NUM_THREADS=1
export QT_QPA_PLATFORM=wayland
unset QT_WAYLAND_SHELL_INTEGRATION
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
export QSG_RENDER_LOOP=basic
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr 2>/dev/null)

$BB mkdir -p /tmp/app/bin
$BB cp -f /app/bin/AppEngineerMode /tmp/app/bin/AppEngineerMode
$BB chmod 755 /tmp/app/bin/AppEngineerMode
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

k=0
while [ $k -lt 9 ]; do
  k=$((k+1))
  $BB sleep 10
  echo "T+$((k*10))s eng=$($BB pidof AppEngineerMode) appm=$($BB pidof ApplicationManager) home=$($BB pidof AppHomeScreen)"
done

echo "=== ENG_DATA_SIM_LOG ==="
$BB cat "$S" 2>/dev/null
echo "=== UNKNOWN_TALLY ==="
$BB grep -a 'ENG_DATA_SIM_UNKNOWN' "$S" 2>/dev/null | $BB sed 's/.*member=/member=/' | $BB sort | $BB uniq -c
echo "=== APPM_LOG_FROM_LAUNCHER ==="
$BB grep -aE 'APPM_LWP|reply is not VALID|reply value|reply cnt|show_window|show_engineer|deregistration|Alive|alive|hang|welcomeReady' "$L" 2>/dev/null | $BB tail -120
echo "=== SESSION_BUS_SHOW ==="
$BB grep -aiE 'show_window_fg|show_window|engineermode' "$SB" 2>/dev/null | $BB cut -c1-260 | $BB tail -40
echo "=== WESTON_SURFACE_LIST ==="
$BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -25
echo "=== PROCESS_LIST ==="
$BB ps 2>/dev/null | $BB grep -aE 'AppEngineerMode|ApplicationManager|AppHomeScreen|AppLauncher|AppCamera' | $BB cut -c1-120

cd /tmp
ENGSURF=$($BB grep -a 'Surface id(' $W 2>/dev/null | $BB tail -n +$((BASE+1)) | $BB sed 's/.*Surface id(\([0-9]*\)).*/\1/' | $BB sort -u | $BB tail -1)
echo "ENGSURF=${ENGSURF:-none}"
if [ -n "$ENGSURF" ]; then
  /usr/bin/ivi-wm "$ENGSURF" >/dev/null 2>&1
  $BB sleep 6
  $BB rm -f /tmp/wayland-screenshot.png
  $BB timeout 25 /usr/libexec/weston-screenshooter >/dev/null 2>&1
  if [ -f /tmp/wayland-screenshot.png ]; then
    echo "SHOT_SIZE=$($BB wc -c < /tmp/wayland-screenshot.png)"
    echo "SHOT_MAGIC=$($BB head -c 8 /tmp/wayland-screenshot.png 2>/dev/null | $BB od -An -tx1 2>/dev/null | $BB tr -d ' \n')"
    echo "SHOT_B64_BEGIN"
    $BB base64 /tmp/wayland-screenshot.png > /dev/ttyS2
    echo "SHOT_B64_END"
  else
    echo "SHOT_MISSING"
  fi
fi
echo DONE
