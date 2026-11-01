#!/bin/busybox sh
BB=/bin/busybox
$BB mkdir -p /tmp/launcher-chain/core-observe
ulimit -c 32768 || exit 92
printf '0x10\n' > /proc/$$/coredump_filter || exit 93
printf '/tmp/launcher-chain/core-observe/core.%%e.%%p\n' > /proc/sys/kernel/core_pattern || exit 94
$BB cat /proc/$$/coredump_filter /proc/sys/kernel/core_pattern > /tmp/launcher-chain/core-observe/core-settings.txt
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
# Scalar supplied by AppLauncher; do not prepend a duplicate value.
unset QT_WAYLAND_DISABLE_WINDOWDECORATION
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

# Bounded early startup only, with no ptrace or debugger intervention.
CAPTURED=0
for tick in $(/bin/busybox seq 1 90); do
  for name in AppCamera AppStandbyClock; do
    for pid in $($BB pidof "$name" 2>/dev/null); do
      [ -r "/proc/$pid/maps" ] || continue
      $BB cat "/proc/$pid/maps" >"/tmp/launcher-chain/core-observe/maps-$name-$pid.txt"
      $BB tr '\000' '\n' <"/proc/$pid/environ" 2>/dev/null |
        $BB grep -E '^(QT_QPA_PLATFORM|QT_WAYLAND_DISABLE_WINDOWDECORATION|QT_WAYLAND_SHELL_INTEGRATION|LD_LIBRARY_PATH|LD_PRELOAD|GALLIUM_DRIVER|QSG_RENDER_LOOP)='         >"/tmp/launcher-chain/core-observe/env-$name-$pid.txt"
    done
  done
  for core in /tmp/launcher-chain/core-observe/core.*; do
    [ -s "$core" ] || continue
    # Wait until no process is actively core-dumping before stopping the run.
    if ! $BB grep -q '^CoreDumping:[[:space:]]*1' /proc/[0-9]*/status 2>/dev/null; then
      $BB sleep 2
      CAPTURED=1
      break
    fi
  done
  [ "$CAPTURED" -eq 1 ] && break
  $BB sleep 1
done
echo EARLY_CORE_CAPTURED=$CAPTURED
$BB kill -9 "$LPID" 2>/dev/null
$BB killall -9 AppLauncher ApplicationManager AppCamera AppStandbyClock UserProfileManager AppNavi dbus-monitor dlt-daemon micom-dbus-sim 2>/dev/null
$BB sleep 1
$BB kill -9 "$WPID" 2>/dev/null
$BB tar -czf /tmp/early-core-evidence.tar.gz -C /tmp launcher-chain
$BB sha256sum /tmp/early-core-evidence.tar.gz
echo EARLY_CORE_ARCHIVE_BEGIN
$BB base64 /tmp/early-core-evidence.tar.gz
echo EARLY_CORE_ARCHIVE_END
[ "$CAPTURED" -eq 1 ]
