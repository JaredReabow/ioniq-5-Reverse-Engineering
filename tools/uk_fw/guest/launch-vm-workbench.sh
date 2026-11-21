#!/bin/busybox sh
# VM-only adaptation of the retained 260128 llvmpipe Home startup recipe.
# The profile/legal confirmation is displayed for the operator to interact with.
BB=/bin/busybox
# Probe returns 0 when ready, 1 to retry, and 2 for a terminal failure.
vm_wait_bounded() {
  vm_limit=$1; shift
  vm_try=0
  while [ "$vm_try" -lt "$vm_limit" ]; do
    "$@"; vm_rc=$?
    [ "$vm_rc" = 0 ] && return 0
    [ "$vm_rc" = 2 ] && return 2
    vm_try=$((vm_try + 1))
    [ "$vm_try" -ge "$vm_limit" ] || $BB sleep 1
  done
  return 1
}
vm_sim_probe() {
  kill -0 "$sim_pid" 2>/dev/null || return 2
  sim_owner=$($BB sed -n "s/^ENG_DATA_SIM_READY pid=$sim_pid owner=\\(:[0-9][0-9]*\\.[0-9][0-9]*\\) system=com.lge.car.micom .*/\\1/p" /tmp/launcher-chain/eng-data-sim.log)
  [ -n "$sim_owner" ] || return 1
  $BB timeout 1 /usr/bin/dbus-send --system --print-reply --reply-timeout=750 \
    --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner \
    string:com.lge.car.micom 2>/dev/null | $BB grep -Fqx "   string \"$sim_owner\"" || return 1
  kill -0 "$sim_pid" 2>/dev/null || return 2
}
# Read only the exact bus owner's identity and PID; never activate an app.
vm_bus_identity() {
  vm_owner_reply=$(set -o pipefail; $BB timeout 1 /usr/bin/dbus-send --session --print-reply --reply-timeout=750 \
    --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetNameOwner \
    string:com.lge.hkmc.avn.appfunc.AppStandbyClock 2>/dev/null | $BB head -c 1025); vm_bus_reply_rc=$?
  [ "${#vm_owner_reply}" -le 1024 ] || return 2
  [ "$vm_bus_reply_rc" = 0 ] || return 1
  vm_now_owner=$(printf '%s\n' "$vm_owner_reply" | $BB awk '
    NR==1 {if ($0 !~ /^method return /) exit 1; next}
    NR==2 {if ($0 !~ /^   string ":[0-9]+[.][0-9]+"$/) exit 1; gsub(/^   string "|"$/, ""); v=$0; next}
    {exit 1} END {if (NR!=2 || v=="") exit 1; print v}') || return 2
  vm_pid_reply=$(set -o pipefail; $BB timeout 1 /usr/bin/dbus-send --session --print-reply --reply-timeout=750 \
    --dest=org.freedesktop.DBus /org/freedesktop/DBus org.freedesktop.DBus.GetConnectionUnixProcessID \
    "string:$vm_now_owner" 2>/dev/null | $BB head -c 1025); vm_bus_reply_rc=$?
  [ "${#vm_pid_reply}" -le 1024 ] || return 2
  [ "$vm_bus_reply_rc" = 0 ] || return 2
  vm_now_pid=$(printf '%s\n' "$vm_pid_reply" | $BB awk '
    NR==1 {if ($0 !~ /^method return /) exit 1; next}
    NR==2 {if ($0 !~ /^   uint32 [1-9][0-9]*$/) exit 1; v=$2; next}
    {exit 1} END {if (NR!=2 || v=="" || v+0>2147483647) exit 1; print v}') || return 2
  return 0
}

# Snapshot only appended bytes, pin inode and every previously read byte, and
# consider only complete lines. This keeps startup history bounded and fresh.
vm_log_hash() {
  if [ "$1" -eq 0 ]; then printf '' | $BB sha256sum
  else $BB head -c "$1" "$vm_log" | $BB sha256sum; fi
}
vm_standby_log() {
  vm_stat=$($BB stat -c '%d:%i:%s' "$vm_log") || { vm_stage=log_stat; return 2; }
  vm_id=${vm_stat%:*}; vm_size=${vm_stat##*:}
  case "$vm_size" in ''|*[!0-9]*) vm_stage=log_stat; return 2;; esac
  [ "$vm_id" = "$vm_log_id" ] && [ "$vm_size" -ge "$vm_prev_size" ] && [ "$vm_size" -le 1048576 ] || { vm_stage=log_identity_or_size; return 2; }
  vm_prefix=$(vm_log_hash "$vm_prev_size") || { vm_stage=log_read; return 2; }
  [ "$vm_prefix" = "$vm_prev_hash" ] || { vm_stage=log_rewritten; return 2; }
  if [ "$vm_size" -eq "$vm_log_offset" ]; then : > "$vm_scan"
  else $BB tail -c +"$((vm_log_offset + 1))" "$vm_log" | $BB head -c "$((vm_size - vm_log_offset))" > "$vm_scan" || { vm_stage=log_read; return 2; }; fi
  vm_bytes=$($BB wc -c < "$vm_scan")
  [ "$vm_bytes" -eq "$((vm_size - vm_log_offset))" ] || { vm_stage=log_short_read; return 2; }
  vm_complete=0
  [ "$vm_bytes" -eq 0 ] || [ "$($BB tail -c 1 "$vm_scan" | $BB wc -l)" -eq 0 ] || vm_complete=1
  vm_result=$($BB awk -v pid="$vm_pid" -v complete="$vm_complete" '
    function check(s) {
      if (index(s,"[TIMEOUT] [1 Group] AppID : 10, PID : ")) bad="loading_timeout"
      if (index(s,"[REGISTERED] registeredFromNativeApp AppId[10][AppStandbyClock]")) {reg++; if(reg>1) bad="duplicate_registration"}
      if (index(s,"ClearTimeoutLoading : 10, PID : ")) {
        if (!reg || s !~ ("ClearTimeoutLoading : 10, PID : " pid "([^0-9]|$)")) bad="loading_pid"
        else clear++
      }
    }
    NR>1 {check(prev)} {prev=$0}
    END {if (complete && NR) check(prev); if(bad!="") print bad; else if(reg==1 && clear==1) print "ready"; else if(clear>1) print "duplicate_clear"; else print "pending"}' "$vm_scan") || { vm_stage=log_parse; return 2; }
  vm_after=$($BB stat -c '%d:%i:%s' "$vm_log") || { vm_stage=log_stat; return 2; }
  [ "${vm_after%:*}" = "$vm_log_id" ] && [ "${vm_after##*:}" -ge "$vm_size" ] || { vm_stage=log_changed; return 2; }
  vm_prefix=$(vm_log_hash "$vm_prev_size") || { vm_stage=log_read; return 2; }
  [ "$vm_prefix" = "$vm_prev_hash" ] || { vm_stage=log_rewritten; return 2; }
  vm_prev_hash=$(vm_log_hash "$vm_size") || { vm_stage=log_hash; return 2; }
  vm_prev_size=$vm_size
  case "$vm_result" in ready) return 0;; pending) return 1;; *) vm_stage=$vm_result; return 2;; esac
}

vm_standby_probe() {
  vm_stage=process
  kill -0 "$sim_pid" 2>/dev/null && kill -0 "$launcher_pid" 2>/dev/null || return 2
  [ -S /run/user/root/wayland-0 ] && [ -x /ivi-fg-standby1000 ] || return 1
  vm_bus_identity; vm_bus_rc=$?
  if [ "$vm_bus_rc" != 0 ]; then
    [ -z "$vm_owner" ] && [ "$vm_bus_rc" = 1 ] && return 1
    vm_stage=owner_query; return 2
  fi
  if [ -z "$vm_owner" ]; then vm_owner=$vm_now_owner; vm_pid=$vm_now_pid; fi
  [ "$vm_owner" = "$vm_now_owner" ] && [ "$vm_pid" = "$vm_now_pid" ] || { vm_stage=owner_changed; return 2; }
  kill -0 "$vm_pid" 2>/dev/null || { vm_stage=standby_exited; return 2; }
  vm_standby_log; vm_log_rc=$?
  [ "$vm_log_rc" = 0 ] || return "$vm_log_rc"
  vm_ping=$(set -o pipefail; $BB timeout 1 /usr/bin/dbus-send --session --print-reply --reply-timeout=750 \
    "--dest=$vm_owner" /com/lge/hkmc/avn/appfunc/valetmode org.freedesktop.DBus.Peer.Ping 2>/dev/null | $BB head -c 1025); vm_ping_rc=$?
  [ "${#vm_ping}" -le 1024 ] || { vm_stage=ping_oversize; return 2; }
  [ "$vm_ping_rc" = 0 ] || { vm_stage=ping_pending; return 1; }
  printf '%s\n' "$vm_ping" | $BB awk -v owner="$vm_owner" '
    NR==1 {if ($0 !~ /^method return sender=:[0-9]+[.][0-9]+ -> dest=:[0-9]+[.][0-9]+ reply_serial=[1-9][0-9]*$/ || index($0,"sender=" owner " ")==0) exit 1; next}
    {exit 1} END {if (NR!=1) exit 1}' || { vm_stage=ping_invalid; return 2; }
  vm_standby_log || { vm_stage=log_recheck; return 2; }
  vm_bus_identity || { vm_stage=owner_recheck; return 2; }
  [ "$vm_owner" = "$vm_now_owner" ] && [ "$vm_pid" = "$vm_now_pid" ] && kill -0 "$vm_pid" 2>/dev/null &&
    kill -0 "$sim_pid" 2>/dev/null && kill -0 "$launcher_pid" 2>/dev/null || { vm_stage=owner_changed; return 2; }
  vm_stage=ready
  return 0
}
export PATH=/bin:/sbin:/usr/bin:/usr/sbin:/app/bin
export LD_LIBRARY_PATH=/opt/software-egl18/lib:/opt/software-egl/lib:/app/lib:/usr/lib:/lib:/navi/Lib:/navi/navi/Lib
export LIBGL_DRIVERS_PATH=/opt/software-egl18/dri LIBGL_ALWAYS_SOFTWARE=1 GALLIUM_DRIVER=llvmpipe LP_NUM_THREADS=2
export XDG_RUNTIME_DIR=/run/user/root WAYLAND_DISPLAY=wayland-0 QT_QPA_PLATFORM=wayland
unset QT_WAYLAND_SHELL_INTEGRATION
export QT_WAYLAND_DISABLE_WINDOWDECORATION=1 QSG_RENDER_LOOP=basic QV4_MM_MAX_CHUNK_SIZE=16384 QV4_NO_SSA=1 QV4_FORCE_INTERPRETER=1
$BB cp /etc/passwd.legacy /tmp/passwd
echo 'xuser:x:1000:100:xuser:/home/xuser:/bin/sh' >>/tmp/passwd
echo 'byungsu:x:1001:100:byungsu:/home/byungsu:/bin/sh' >>/tmp/passwd
$BB mkdir -p /run/dbus /run/lock /run/user/root /var/run/dbus /rw_data/var/volatile/log /rw_data/var/volatile/tmp /tmp/launcher-chain /log_data
$BB chmod 700 /run/user/root
/usr/bin/dbus-uuidgen --ensure
/usr/bin/dbus-daemon --system --fork 2>/tmp/launcher-chain/system-dbus.err
/usr/bin/dbus-daemon --session --print-address --fork >/tmp/session_appmgr 2>/tmp/launcher-chain/session-dbus.err
export DBUS_SESSION_BUS_ADDRESS=$($BB cat /tmp/session_appmgr)
# This VM scenario explicitly supplies the recovered IHU parking-status bit
# before any native application requests car information.
[ ! -e /tmp/eng-data-sim-startup ] && [ ! -L /tmp/eng-data-sim-startup ] || exit 26
ENG_DATA_SIM_PARKING_STATUS=1 /eng-data-sim >/tmp/launcher-chain/eng-data-sim.log 2>&1 &
sim_pid=$!
# The ready line is emitted by this PID only after it owns the system name and
# has registered every system object handler. Verify the bus owner still agrees.
vm_wait_bounded 30 vm_sim_probe
sim_result=$?
[ "$sim_result" = 0 ] || { echo WORKBENCH_SIMULATOR_FAILED; exit 27; }
[ -e /app/share/AppHomeScreen/qml ] || $BB ln -s qml_new2.0 /app/share/AppHomeScreen/qml
$BB mkdir -p /tmp/new_gui
$BB mount -o bind /system/new_gui /tmp/new_gui
$BB mount -o bind /system/new_gui/new2.0/hmc/night /app/share/images/hmc
$BB mount -o bind /Screen_AppStandbyClock_Confirm_Profile.observe.qml /app/share/AppStandbyClock/qml_eco3.0/Screen_AppStandbyClock_Confirm_Profile.qml
$BB mount -o bind /AppStandbyClock-main.loader-sized.qml /app/share/AppStandbyClock/qml_eco3.0/main.qml
[ -e /navi/navi ] || $BB ln -s . /navi/navi
$BB ln -sf /app/share/SplashScreen/8bit_booting_2022NEWHMC_NA_NA_1920.png /tmp/front_lcd.png
vm_ivi_module=
if [ "${VM_IVI_FRAME_PROBE:-0}" = 1 ]; then
  unset LD_PRELOAD LD_AUDIT
  # Offsets used by the optional diagnostic are valid only for these bytes.
  [ "$($BB sha256sum /usr/bin/weston-headless | $BB cut -d ' ' -f1)" = 3cb8c206cd31e174835a4246202c96eba33db6f36d822299045b51ac4a42f58f ] || exit 31
  [ "$($BB sha256sum /usr/lib/weston/ivi-shell.so | $BB cut -d ' ' -f1)" = 8b57db4baa1f35a1a08cffc6de221101a92b37528123d7250c774db03a3b7697 ] || exit 31
  [ "$($BB sha256sum /usr/lib/libpixman-1.so.0.42.2 | $BB cut -d ' ' -f1)" = b02a0f8c9eac5a79f7e77375f1ba6d4e7dff3da9973496675f4403bddc507559 ] || exit 31
  [ -f /weston-ivi-frame-probe.so ] && [ ! -L /weston-ivi-frame-probe.so ] || exit 31
  vm_ivi_module=,/weston-ivi-frame-probe.so
fi
$BB cat >/tmp/launcher-weston.ini <<EOF
[core]
backend=headless-backend.so
shell=ivi-shell.so
modules=/weston-vm-input.so
idle-time=0
[ivi-shell]
ivi-module=ivi-window-manager.so,ivi-controller.so$vm_ivi_module
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
for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
  [ -S /run/user/root/wayland-0 ] && break
  $BB sleep 1
done
[ -S /run/user/root/wayland-0 ] || { echo WORKBENCH_NO_WAYLAND; exit 21; }
$BB mount --bind /AppNavi-egl-no-msaa-v2 /navi/Bin/AppNavi || exit 23
$BB mount --bind /AppLauncher-vm-timeout120 /app/bin/AppLauncher || exit 24
export WAYLAND_DEBUG=1
$BB mkdir -p /tmp/dltpipes /rw_data/dlt
$BB printf 'ECUId = MANGO\nPrintASCII = 1\nLoggingMode = 0\nLoggingLevel = 7\nPersistanceStoragePath = /rw_data/dlt\n' >/tmp/dlt-test.conf
/usr/bin/dlt-daemon -c /tmp/dlt-test.conf >/tmp/launcher-chain/dlt.log 2>&1 &
cd /app/bin || exit 22
vm_log=/tmp/launcher-chain/launcher.log
vm_scan=/tmp/launcher-chain/standby-admission.log
[ ! -e "$vm_log" ] && [ ! -L "$vm_log" ] && [ ! -e "$vm_scan" ] && [ ! -L "$vm_scan" ] || { echo WORKBENCH_STANDBY_FAIL_log_preexisting; exit 29; }
: > "$vm_log" || exit 29
vm_stat=$($BB stat -c '%d:%i:%s' "$vm_log") || exit 29
vm_log_id=${vm_stat%:*}; vm_log_offset=${vm_stat##*:}; vm_prev_size=$vm_log_offset
vm_prev_hash=$(vm_log_hash "$vm_prev_size") || exit 29
vm_owner=; vm_pid=; vm_stage=startup
/app/bin/AppLauncher 3 >>"$vm_log" 2>&1 &
launcher_pid=$!
echo WORKBENCH_LAUNCHER_STARTED
# One monotonic guest deadline covers every registration, log and Ping probe.
read -r vm_start _ </proc/uptime
vm_start=${vm_start%%.*}; case "$vm_start" in ''|*[!0-9]*) exit 29;; esac
vm_deadline=$((vm_start + 120))
while :; do
  read -r vm_now _ </proc/uptime
  vm_now=${vm_now%%.*}; case "$vm_now" in ''|*[!0-9]*) vm_stage=clock; break;; esac
  [ "$vm_now" -lt "$vm_deadline" ] || { vm_stage=deadline; break; }
  vm_standby_probe; vm_result=$?
  if [ "$vm_result" = 0 ]; then
    read -r vm_now _ </proc/uptime; vm_now=${vm_now%%.*}
    case "$vm_now" in ''|*[!0-9]*) vm_stage=clock; break;; esac
    [ "$vm_now" -lt "$vm_deadline" ] || { vm_stage=deadline; break; }
    echo WORKBENCH_STANDBY_PREREQUISITES_READY
    exit 0
  fi
  [ "$vm_result" = 2 ] && break
  $BB sleep 1
done
echo "WORKBENCH_STANDBY_FAIL_$vm_stage"
# Stage labels come only from the bounded probe above. Publish privately
# before the host wrapper publishes status 25. A write failure stays generic.
vm_failure=/tmp/workbench-launch.failure
if [ ! -e "$vm_failure" ] && [ ! -L "$vm_failure" ]; then
  (umask 077; set -C; printf '%s\n' "$vm_stage" > "$vm_failure") 2>/dev/null
fi
exit 25
