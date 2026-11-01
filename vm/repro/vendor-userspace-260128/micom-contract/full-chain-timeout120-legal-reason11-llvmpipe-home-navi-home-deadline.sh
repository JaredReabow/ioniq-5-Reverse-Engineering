#!/bin/busybox sh
BB=/bin/busybox
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/app/bin
export LD_LIBRARY_PATH=/opt/software-egl18/lib:/opt/software-egl/lib:/app/lib:/usr/lib:/lib:/navi/Lib:/navi/navi/Lib
export LIBGL_DRIVERS_PATH=/opt/software-egl18/dri
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export LP_NUM_THREADS=2
export XDG_RUNTIME_DIR=/run/user/root
export WAYLAND_DISPLAY=wayland-0
export QT_QPA_PLATFORM=wayland
# AppLauncher appends its own :ivi value for child processes. Pre-setting this
# produced the invalid value ivi:ivi and QPA shell-integration failures.
unset QT_WAYLAND_SHELL_INTEGRATION
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1
export QSG_RENDER_LOOP=basic
export QV4_MM_MAX_CHUNK_SIZE=16384
export QV4_NO_SSA=1
export QV4_FORCE_INTERPRETER=1
$BB cp /etc/passwd.legacy /tmp/passwd
echo 'xuser:x:1000:100:xuser:/home/xuser:/bin/sh' >>/tmp/passwd
echo 'byungsu:x:1001:100:byungsu:/home/byungsu:/bin/sh' >>/tmp/passwd
$BB mkdir -p /run/dbus /run/lock /run/user/root /var/run/dbus /rw_data/var/volatile/log /rw_data/var/volatile/tmp /tmp/launcher-chain /log_data
$BB chmod 700 /run/user/root
# Opt in before AppLauncher starts: its launcher-local execve interposer adds
# the EGL compatibility library only to the original signed AppNavi process.
$BB touch /tmp/launcher-chain/enable-appnavi-egl-compat /tmp/launcher-chain/enable-appnavi-liveness-compat /tmp/launcher-chain/enable-appnavi-startup-deadline-compat
/usr/bin/dbus-uuidgen --ensure
/usr/bin/dbus-daemon --system --fork 2>/tmp/launcher-chain/system-dbus.err
/usr/bin/dbus-daemon --session --print-address --fork >/tmp/session_appmgr 2>/tmp/launcher-chain/session-dbus.err
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr)
# VM-only, fail-closed NE/EUR idle boot profile. Every unsupported micom call
# receives UnknownObject/UnknownMethod and is logged for contract expansion.
MICOM_BOOTINFO=00000826050000051302000003c8140000000000000000000000020001000000000000
/micom-dbus-sim "$MICOM_BOOTINFO" >/tmp/launcher-chain/micom-sim.log 2>&1 &
MPID=$!
[ -e /app/share/AppHomeScreen/qml ] || $BB ln -s qml_new2.0 /app/share/AppHomeScreen/qml
# Restore the recovered production target of /app/share/images/new_gui ->
# /tmp/new_gui. Without this bind, the legal-profile QML has zero-sized theme
# images and its anchored controls are displaced off-screen.
$BB mkdir -p /tmp/new_gui
$BB mount -o bind /system/new_gui /tmp/new_gui
$BB mount -o bind /system/new_gui/new2.0/hmc/night /app/share/images/hmc
# Observational-only QML overlay: logs authentic model state and resolved
# geometry without changing button bindings, handlers, or enabled state.
$BB mount -o bind /Screen_AppStandbyClock_Confirm_Profile.observe.qml /app/share/AppStandbyClock/qml_eco3.0/Screen_AppStandbyClock_Confirm_Profile.qml
$BB mount -o bind /AppStandbyClock-main.loader-sized.qml /app/share/AppStandbyClock/qml_eco3.0/main.qml
[ -e /navi/navi ] || $BB ln -s . /navi/navi
$BB ln -sf /app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png /tmp/front_lcd.png
cat >/tmp/launcher-weston.ini <<'EOF'
[core]
backend=headless-backend.so
shell=ivi-shell.so
modules=/weston-vm-input.so
idle-time=0
[ivi-shell]
ivi-module=ivi-window-manager.so,ivi-controller.so
ivi-shell-user-interface=/bin/true
base-layer-id=1000
workspace-background-layer-id=2000
workspace-layer-id=3000
application-layer-id=4000
transition-duration=0
workspace-background-color=0xff000000
workspace-background-id=2001
[output]
name=headless
mode=1920x720
EOF
/usr/bin/weston-headless --config=/tmp/launcher-weston.ini --use-pixman --width=1920 --height=720 --socket=wayland-0 --idle-time=0 --debug >/tmp/launcher-chain/weston.log 2>&1 &
WPID=$!
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -S /run/user/root/wayland-0 ] && break
  $BB sleep 1
done
[ -S /run/user/root/wayland-0 ] || { echo NO_WAYLAND_SOCKET; exit 21; }
# Keep /navi/Bin/AppNavi unmodified in this control. The prior exact-build
# zero-MSAA copy fails AppLauncher's executable/signature inspection in the
# full launcher chain (AppID 30 exits 100 before a process is created).
# Global llvmpipe's authentic 2x-MSAA behavior is deliberately tested here.
# No fabricated micom payload or semaphore reset is used.
# VM timing adaptation: AppStandbyClock registered about three seconds after
# the prior 60-second group timeout. This exact-build control changes only the
# same QTimer immediate, 10,000 -> 120,000 ms at file offset 0x18270, so the
# authentic standby registration can precede preload completion.
$BB mount --bind /AppLauncher-vm-timeout120 /app/bin/AppLauncher || exit 24
export WAYLAND_DEBUG=1
$BB mkdir -p /tmp/dltpipes /rw_data/dlt
$BB printf 'ECUId = MANGO\nPrintASCII = 1\nLoggingMode = 0\nLoggingLevel = 7\nPersistanceStoragePath = /rw_data/dlt\n' >/tmp/dlt-test.conf
/usr/bin/dlt-daemon -c /tmp/dlt-test.conf >/tmp/launcher-chain/dlt.log 2>&1 &
DPID=$!
# Full-chain control: do not claim the authentic AppStandbyClock service with
# the isolated AppNavi valet stub. AppLauncher starts the real service.
SPID=
/usr/bin/dbus-monitor --session > /tmp/launcher-chain/session-bus.log 2>&1 &
BPID=$!
echo IPC_BEFORE_LAUNCH
/ipc-observe
cd /app/bin || exit 22
# Timing control: launch directly so syscall tracing cannot trigger the
# recovered manager's application-liveness watchdog under software rendering.
LD_PRELOAD=/launcher-appnavi-liveness-preload.so /app/bin/AppLauncher 3 >/tmp/launcher-chain/launcher.log 2>&1 &
LPID=$!
echo APPLAUNCHER_DIRECT_PID=$LPID
# Let authentic AppStandbyClock register before the adapted group timer can
# expire. Do not issue an extra AppNavi launch request in this ordering control.
$BB sleep 75
echo IPC_AFTER_LAUNCH_75
/ipc-observe
$BB cat /proc/sysvipc/sem /proc/sysvipc/shm > /tmp/launcher-chain/sysvipc.txt

echo PROCESS_LIST_BEGIN
$BB ps > /tmp/launcher-chain/processes.txt
$BB cat /tmp/launcher-chain/processes.txt
echo PROCESS_LIST_END

echo STANDBY_STATUS_BASELINE
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_standby_status
$BB mkdir -p /tmp/launcher-chain/shot-before-confirm
cd /tmp/launcher-chain/shot-before-confirm
$BB timeout 15 /usr/libexec/weston-screenshooter >/tmp/launcher-chain/screenshot-before-confirm.log 2>&1
[ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png

# Ask authentic AppStandbyClock to enter the evidence-derived profile/legal
# screen using the exact six-argument tuple observed from ApplicationManager:
# appid=10, reason=11, plane=1, avmode=-1, command=0, temporal=false. Then
# foreground observed surface 1000. This exercises, rather than bypasses, the gate.
echo STANDBY_APPBASE_FOREGROUND_BEGIN
STANDBY_APPBASE_FOREGROUND_RC=1
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
  echo STANDBY_APPBASE_FOREGROUND_ATTEMPT=$n
  $BB timeout 5 /usr/bin/dbus-send --session --print-reply \
    --dest=com.lge.hkmc.avn.appfunc.AppStandbyClock \
    /com/lge/hkmc/avn/appfunc/standby \
    com.lge.avn.appmanager.appbase.show_window_fg \
    int32:10 int32:11 int32:1 int32:-1 int32:0 boolean:false
  STANDBY_APPBASE_FOREGROUND_RC=$?
  [ "$STANDBY_APPBASE_FOREGROUND_RC" -eq 0 ] && break
  $BB sleep 1
 done
echo STANDBY_APPBASE_FOREGROUND_RC=$STANDBY_APPBASE_FOREGROUND_RC
$BB sleep 2
$BB timeout 15 /ivi-fg-standby1000
echo STANDBY_IVI_FOREGROUND_RC=$?
$BB sleep 2
echo STANDBY_STATUS_AFTER_FOREGROUND
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_standby_status
$BB mkdir -p /tmp/launcher-chain/shot-standby-forced
cd /tmp/launcher-chain/shot-standby-forced
$BB timeout 15 /usr/libexec/weston-screenshooter >/tmp/launcher-chain/screenshot-standby-forced.log 2>&1
[ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png

# qml_eco3.0/Screen_AppStandbyClock_Confirm_Profile.qml places the
# wide-screen Confirm button in the left half of txtArea. With bg x=9 and the
# 452-pixel profile area, x=800 is bounded inside Confirm; x=1500 was Language.
# Late-starting clients can acquire pointer focus after the first foreground
# request. Re-assert surface 1000 immediately before motion/button injection.
echo STANDBY_IVI_REFOREGROUND_BEFORE_POINTER_BEGIN
$BB timeout 15 /ivi-fg-standby1000
echo STANDBY_IVI_REFOREGROUND_BEFORE_POINTER_RC=$?
$BB sleep 1
echo STANDBY_CONFIRM_LEFT_POINTER 820 630
echo pdrag 820 630 820 630 >/tmp/weston-vm-input
# Under x86 TCG the authentic release handler can be delayed beyond the old
# fixed 10-second wait. Poll read-only manager state and do not request Home
# until AppStandbyClock has authentically changed standby status to 12.
AGREED=0
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24; do
  $BB sleep 5
  echo STANDBY_STATUS_POLL_ATTEMPT=$n
  $BB timeout 15 /usr/bin/dbus-send --session --print-reply \
    --dest=com.lge.hyundai.avn.appmanager /Information \
    com.lge.avn.appmanager.info.ask_standby_status \
    >"/tmp/launcher-chain/standby-status-poll-$n.out" 2>&1
  $BB cat "/tmp/launcher-chain/standby-status-poll-$n.out"
  if $BB grep -q 'int32 12' "/tmp/launcher-chain/standby-status-poll-$n.out"; then
    AGREED=1
    echo STANDBY_AGREEMENT_OBSERVED_ATTEMPT=$n
    break
  fi
done
echo STANDBY_AGREEMENT_OBSERVED=$AGREED
echo INFORMATION_INTROSPECT_AFTER_AGREEMENT
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  org.freedesktop.DBus.Introspectable.Introspect \
  >/tmp/launcher-chain/information-introspect.txt 2>&1
$BB cat /tmp/launcher-chain/information-introspect.txt
$BB mkdir -p /tmp/launcher-chain/shot-after-confirm
cd /tmp/launcher-chain/shot-after-confirm
$BB timeout 15 /usr/libexec/weston-screenshooter >/tmp/launcher-chain/screenshot-after-confirm.log 2>&1
[ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png

# Exercise the evidence-backed Home faceplate path only after authentic
# agreement. Allow the handler's own reason-12 transition to settle first.
HOME_TRANSITION_RC=125
if [ "$AGREED" -eq 1 ]; then
  $BB sleep 8
  echo HOME_TRANSITION_AFTER_AGREEMENT_BEGIN
  $BB timeout 15 /usr/bin/dbus-send --session --print-reply \
    --dest=com.lge.hyundai.avn.appmanager /transition \
    com.lge.avn.appmanager.screentransition.request \
    int32:302 int32:0 int32:322 int32:1 int32:0
  HOME_TRANSITION_RC=$?
fi
echo HOME_TRANSITION_AFTER_AGREEMENT_RC=$HOME_TRANSITION_RC
# On two-thread llvmpipe, AppHomeScreen needs roughly a minute to finish its
# first software-rendered frame. ApplicationManager's production four-second
# liveness cadence kills it first because its Qt event loop is still rendering.
# This explicit VM-only scheduling control pauses only ApplicationManager after
# it has issued authentic requestShow(APP_HOME), giving the unmodified Home
# process a bounded 55-second initialization window. It neither fabricates a
# reply nor mutates manager or application state.
APPM_PID=$($BB pidof ApplicationManager | $BB awk '{print $1}')
if [ "$AGREED" -eq 1 ] && [ -n "$APPM_PID" ]; then
  $BB sleep 1
  echo HOME_SETTLE_MANAGER_STOP_PID=$APPM_PID
  $BB kill -STOP "$APPM_PID"
  for HOME_SETTLE in 30 55; do
    if [ "$HOME_SETTLE" -eq 30 ]; then
      $BB sleep 30
    else
      $BB sleep 25
    fi
    echo HOME_SETTLE_OBSERVATION_SECONDS=$HOME_SETTLE
    $BB mkdir -p "/tmp/launcher-chain/shot-home-settle-$HOME_SETTLE"
    cd "/tmp/launcher-chain/shot-home-settle-$HOME_SETTLE"
    $BB timeout 15 /usr/libexec/weston-screenshooter >"/tmp/launcher-chain/screenshot-home-settle-$HOME_SETTLE.log" 2>&1
    [ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png
    $BB ps >"/tmp/launcher-chain/processes-home-settle-$HOME_SETTLE.txt"
  done
  echo HOME_SETTLE_MANAGER_CONT_PID=$APPM_PID
  $BB kill -CONT "$APPM_PID"
  $BB sleep 3
  echo HOME_TRANSITION_AFTER_SETTLE_BEGIN
  $BB timeout 15 /usr/bin/dbus-send --session --print-reply \
    --dest=com.lge.hyundai.avn.appmanager /transition \
    com.lge.avn.appmanager.screentransition.request \
    int32:302 int32:0 int32:322 int32:1 int32:0
  echo HOME_TRANSITION_AFTER_SETTLE_RC=$?
else
  echo HOME_SETTLE_SKIPPED
fi
for HOME_OBSERVATION in 15; do
  $BB sleep 15
  echo HOME_POST_SETTLE_OBSERVATION_SECONDS=$HOME_OBSERVATION
  echo HOME_POST_SETTLE_STANDBY_STATUS_SECONDS=$HOME_OBSERVATION
  $BB timeout 15 /usr/bin/dbus-send --session --print-reply \
    --dest=com.lge.hyundai.avn.appmanager /Information \
    com.lge.avn.appmanager.info.ask_standby_status
  $BB mkdir -p "/tmp/launcher-chain/shot-home-post-settle-$HOME_OBSERVATION"
  cd "/tmp/launcher-chain/shot-home-post-settle-$HOME_OBSERVATION"
  $BB timeout 15 /usr/libexec/weston-screenshooter >"/tmp/launcher-chain/screenshot-home-post-settle-$HOME_OBSERVATION.log" 2>&1
  [ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png
  $BB ps >"/tmp/launcher-chain/processes-home-post-settle-$HOME_OBSERVATION.txt"
done

# AppLauncher has already created the authentic signed AppNavi process. The
# launcher-local execve interposer targets only that executable. Its guarded
# executable-scoped shim also extends the exact-build 22,999 ms startup-failure
# threshold to 180,000 ms in memory, allowing slow TCG startup to reach the
# authentic first-window event before launch-status reporting; no duplicate
# or direct AppNavi process is started.
echo TARGETED_NAVI_PREEXISTING
$BB pidof AppNavi || true

# Query the now-documented plane-1 signatures before navigation.
echo PRE_NAVI_APPMANAGER_APPLICATION
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_appmanager_application int32:1
echo PRE_NAVI_DRAWING_APPLICATION
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_drawing_application int32:1

# Evidence-backed faceplate Navigation path. Existing manager traces map
# event 302 + reason 309 to APP_NAVI_LOADING (35), which then hands off to
# authentic AppNavi (30). Keep appid=0, plane=1, command=0 as observed.
echo NAVI_TRANSITION_FROM_HOME_BEGIN
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /transition \
  com.lge.avn.appmanager.screentransition.request \
  int32:302 int32:0 int32:309 int32:1 int32:0
echo NAVI_TRANSITION_FROM_HOME_RC=$?
# Leave both manager and launcher responsive so authentic IVI and launched-
# status callbacks can advance. The launcher-local shim suppresses only its
# liveness kill of AppNavi after the explicit sentinel above.
for NAVI_OBSERVATION in 30 60 90 120; do
  $BB sleep 30
  echo NAVI_LIVE_MANAGER_OBSERVATION_SECONDS=$NAVI_OBSERVATION
  $BB mkdir -p "/tmp/launcher-chain/shot-navi-live-$NAVI_OBSERVATION"
  cd "/tmp/launcher-chain/shot-navi-live-$NAVI_OBSERVATION"
  $BB timeout 15 /usr/libexec/weston-screenshooter >"/tmp/launcher-chain/screenshot-navi-live-$NAVI_OBSERVATION.log" 2>&1
  [ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png
  $BB ps >"/tmp/launcher-chain/processes-navi-live-$NAVI_OBSERVATION.txt"
done
echo POST_NAVI_APPMANAGER_APPLICATION
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_appmanager_application int32:1
echo POST_NAVI_DRAWING_APPLICATION
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_drawing_application int32:1

# Return through the already corroborated faceplate Home path.
echo HOME_TRANSITION_FROM_NAVI_BEGIN
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /transition \
  com.lge.avn.appmanager.screentransition.request \
  int32:302 int32:0 int32:322 int32:1 int32:0
echo HOME_TRANSITION_FROM_NAVI_RC=$?
for RETURN_HOME_OBSERVATION in 30; do
  $BB sleep 30
  echo RETURN_HOME_OBSERVATION_SECONDS=$RETURN_HOME_OBSERVATION
  $BB mkdir -p "/tmp/launcher-chain/shot-return-home-$RETURN_HOME_OBSERVATION"
  cd "/tmp/launcher-chain/shot-return-home-$RETURN_HOME_OBSERVATION"
  $BB timeout 15 /usr/libexec/weston-screenshooter >"/tmp/launcher-chain/screenshot-return-home-$RETURN_HOME_OBSERVATION.log" 2>&1
  [ -f wayland-screenshot.png ] && $BB sha256sum wayland-screenshot.png
  $BB ps >"/tmp/launcher-chain/processes-return-home-$RETURN_HOME_OBSERVATION.txt"
done
echo RETURN_HOME_APPMANAGER_APPLICATION
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_appmanager_application int32:1
echo RETURN_HOME_DRAWING_APPLICATION
$BB timeout 15 /usr/bin/dbus-send --session --print-reply \
  --dest=com.lge.hyundai.avn.appmanager /Information \
  com.lge.avn.appmanager.info.ask_drawing_application int32:1

# Bounded capture; terminate direct launcher and descendants explicitly.
$BB kill -CONT $APPM_PID 2>/dev/null
$BB kill -9 $NAVI_PID $LPID $SPID $BPID $DPID $MPID 2>/dev/null
$BB killall -9 AppLauncher ApplicationManager AppHomeScreen AppNavi strace dbus-bool-stub dbus-monitor dlt-daemon micom-dbus-sim 2>/dev/null
$BB sleep 1
$BB kill -9 $WPID 2>/dev/null
wait $LPID 2>/dev/null
wait $WPID 2>/dev/null
$BB tar -czf /tmp/micom-chain-evidence.tar.gz -C /tmp launcher-chain
$BB sha256sum /tmp/micom-chain-evidence.tar.gz
echo CHAIN_ARCHIVE_BASE64_BEGIN
$BB base64 /tmp/micom-chain-evidence.tar.gz
echo CHAIN_ARCHIVE_BASE64_END
exit 0
