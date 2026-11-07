#!/bin/sh
# interval-run.sh - RETAINED run driver.
#
# boot58's fatal flaw was that the script driving it was never retained, so its timing, poll
# structure and relaunch logic are unrecoverable (docs/kernel/42). This file exists so that cannot
# happen again: it lives in the tracked tree, it is staged into the image by hash, and its SHA-256 is
# recorded in the run manifest before the run starts.
#
# It implements the TWO evidence channels Astra required (docs/planning/astra-c11.md):
#
#   Runtime channel - generation observations (pid AND starttime), a persistence interval FIXED
#                     BEFORE LAUNCH, and a per-sample liveness record. These are the observations that
#                     may support "registered", "persisted" and "interactive". The capture harness
#                     may NOT support those claims.
#   Export channel  - one invocation of the frozen helper (interval-capture.sh) with a
#                     launcher-supplied (pid, starttime) pair. That yields the narrow claim only.
#
# Reporting rule, fixed before launch: marker presence is an ARTIFACT result. Registration,
# persistence and interaction are SEPARATE runtime conclusions, and anything this driver cannot
# establish is reported as unresolved - not absent.
#
# FIXED BEFORE LAUNCH (do not tune these after seeing a result):
#   PERSIST_S  = 120   persistence observation interval
#   SAMPLE_S   = 5     liveness sample period
#   SETTLE_S   = 20    quiet period before the export snapshot
#
# Usage (in-guest, from the init script):
#   interval-run.sh [--out DEV] [--app NAME] [--manifest PATH] [--helper PATH]
#
# Exit status: 0 completed, 2 usage, 3 prerequisites missing, 4 no generation observed.

set -u

OUT=/dev/ttyS2
EXPORT_OUT=/dev/ttyS3
APP=AppHomeScreen
LOG=/tmp/weston-real.log
MANIFEST=/run/interval-manifest.txt
HELPER=/interval-capture.sh
PERSIST_S=120
SAMPLE_S=5
SETTLE_S=20
SOCKET=${IC_SOCKET:-/run/user/root/wayland-0}
UPTIME_FILE=${IC_UPTIME:-/proc/uptime}
PROC_ROOT=${IC_PROC:-/proc}

# SANDBOX MODE exists only so this driver can be exercised on a host before it is trusted in a boot.
# It is enabled ONLY when IC_PROC points somewhere other than the real /proc, and it is the only mode
# in which the intervals may be shortened. A real run cannot silently reduce PERSIST_S, which is the
# whole point of fixing the interval before launch.
SANDBOX=no
if [ "$PROC_ROOT" != "/proc" ]; then
  SANDBOX=yes
  PERSIST_S=${IC_PERSIST_S:-$PERSIST_S}
  SAMPLE_S=${IC_SAMPLE_S:-$SAMPLE_S}
  SETTLE_S=${IC_SETTLE_S:-$SETTLE_S}
fi

while [ $# -gt 0 ]; do
  case "$1" in
    --out)      OUT=${2:-}; shift 2 ;;
    --export-out) EXPORT_OUT=${2:-}; shift 2 ;;
    --log)      LOG=${2:-}; shift 2 ;;
    --app)      APP=${2:-}; shift 2 ;;
    --manifest) MANIFEST=${2:-}; shift 2 ;;
    --helper)   HELPER=${2:-}; shift 2 ;;
    -h|--help)  echo "usage: interval-run.sh [--out DEV] [--export-out DEV] [--log PATH] [--app NAME] [--manifest PATH] [--helper PATH]" >&2; exit 2 ;;
    *)          echo "interval-run: unknown argument $1" >&2; exit 2 ;;
  esac
done

for v in "$PERSIST_S" "$SAMPLE_S" "$SETTLE_S"; do
  case "$v" in ''|*[!0-9]*) echo "interval-run: fixed intervals must be integers" >&2; exit 2 ;; esac
done

# Receipt lines go to the same channel the helper uses. A write failure is fatal here too: a run
# whose observations were not recorded is not a run whose observations happened.
log() {
  printf '[irun] %s\n' "$*" >> "$OUT" 2>/dev/null || {
    echo "interval-run: FATAL cannot write to $OUT" >&2
    return 1
  }
}

now_cs() {
  read -r _up _rest < "$UPTIME_FILE" 2>/dev/null || return 1
  # Strict format. Without this, "." produced an empty whole part that padded to "00" and was
  # reported as a confident 0 - the same fabricated-timestamp defect the helper had to be fixed for.
  case "$_up" in
    '') return 1 ;;
    *[!0-9.]*) return 1 ;;
    *.*.*) return 1 ;;
    .*) return 1 ;;
  esac
  _w=${_up%%.*}
  if [ "$_w" = "$_up" ]; then _f=00; else _f=${_up#*.}; fi
  while [ ${#_f} -lt 2 ]; do _f="${_f}0"; done
  _f=$(printf '%s' "$_f" | cut -c1-2) || return 1
  case "$_f" in ''|*[!0-9]*) return 1 ;; esac
  _o=$(printf '%s%s' "$_w" "$_f" | sed 's/^0*//') || return 1
  [ -z "$_o" ] && _o=0
  printf '%s\n' "$_o"
}

# starttime is /proc/<pid>/stat field 22; after stripping "pid (comm) " it is $20.
starttime_of() {
  [ -r "$PROC_ROOT/$1/stat" ] || return 1
  sed 's/.*) //' "$PROC_ROOT/$1/stat" 2>/dev/null | awk '{print $20}' 2>/dev/null
}

# pidof is used when present (the guest has busybox). A /proc scan is the fallback, which is also
# what makes this driver testable on a host: without it, pids_of returned nothing outside the guest,
# the first-generation wait spun for its full 180 s, and the sandbox tests appeared to hang.
pids_of() {
  if command -v pidof >/dev/null 2>&1; then
    pidof "$APP" 2>/dev/null
    return 0
  fi
  for _d in "$PROC_ROOT"/[0-9]*; do
    [ -r "$_d/stat" ] || continue
    _c=$(sed -n 's/^[0-9]* (\(.*\)) .*/\1/p' "$_d/stat" 2>/dev/null)
    [ "$_c" = "$APP" ] && printf '%s\n' "${_d##*/}"
  done
  return 0
}

# An init script runs BEFORE /proc is mounted, so the very first clock read fails. Observed in run
# 1794055821491663000: "/interval-run.sh: line 86: /proc/uptime: No such file or directory" and the
# driver exited 3 before doing anything. Wait for the clock source to appear.
_cw=0
while [ ! -r "$UPTIME_FILE" ] && [ "$_cw" -lt 120 ]; do
  sleep 1 2>/dev/null || break
  _cw=$((_cw + 1))
done
if [ ! -r "$UPTIME_FILE" ]; then
  echo "interval-run: FATAL $UPTIME_FILE never appeared after ${_cw}s" >&2
  exit 3
fi

T0=$(now_cs) || { echo "interval-run: clock unavailable" >&2; exit 3; }

log "DRIVER version=1 app=$APP log=$LOG out=$OUT export_out=$EXPORT_OUT persist_s=$PERSIST_S sample_s=$SAMPLE_S settle_s=$SETTLE_S sandbox=$SANDBOX proc_root=$PROC_ROOT socket=$SOCKET"
log "DRIVER fixed_before_launch=yes t0_cs=$T0"

if [ ! -r "$MANIFEST" ]; then
  log "OUTCOME PREREQ_MISSING reason=manifest_unreadable path=$MANIFEST"
  exit 3
fi
if [ ! -r "$HELPER" ]; then
  log "OUTCOME PREREQ_MISSING reason=helper_unreadable path=$HELPER"
  exit 3
fi

# --- generation observations -------------------------------------------------
# A generation is recorded the moment it is first seen, as (pid, starttime). The helper is later
# given one of these pairs EXACTLY as recorded, so the capture binding is launcher-supplied rather
# than a fresh pidof enumeration (Astra A2/A3).
GEN_N=0
LAST_PID=""
LAST_ST=""

record_generation() {
  _pid=$1
  _st=$(starttime_of "$_pid") || return 1
  case "$_st" in ''|*[!0-9]*) return 1 ;; esac
  GEN_N=$((GEN_N + 1))
  LAST_PID=$_pid
  LAST_ST=$_st
  _t=$(now_cs) || _t="?"
  log "GEN n=$GEN_N pid=$_pid starttime=$_st observed_at_cs=$_t"
  return 0
}

# Wait for the compositor socket, then for the first generation of the app.
log "PHASE wait_socket socket=$SOCKET"
_n=0
while [ ! -S "$SOCKET" ] && [ "$_n" -lt 300 ]; do
  sleep 1 || { log "OUTCOME CLOCK_UNAVAILABLE reason=sleep_failed"; exit 3; }
  _n=$((_n + 1))
done
if [ ! -S "$SOCKET" ]; then
  log "OUTCOME PREREQ_MISSING reason=no_wayland_socket waited_s=$_n"
  exit 3
fi
log "PHASE socket_up waited_s=$_n"

log "PHASE wait_first_generation"
_n=0
while [ -z "$(pids_of)" ] && [ "$_n" -lt 180 ]; do
  sleep 1 || { log "OUTCOME CLOCK_UNAVAILABLE reason=sleep_failed"; exit 3; }
  _n=$((_n + 1))
done
for _p in $(pids_of); do
  record_generation "$_p" && break
done
if [ "$GEN_N" -eq 0 ]; then
  log "OUTCOME NO_GENERATION reason=app_never_observed waited_s=$_n app=$APP"
  exit 4
fi

# --- persistence interval, fixed before launch ------------------------------
# This is the runtime channel. It answers "did the generation stay alive for PERSIST_S", which the
# capture harness cannot answer at all.
log "PHASE persistence persist_s=$PERSIST_S"
_samples=0
_alive=0
_elapsed=0
while [ "$_elapsed" -lt "$PERSIST_S" ]; do
  sleep "$SAMPLE_S" || { log "OUTCOME CLOCK_UNAVAILABLE reason=sleep_failed"; exit 3; }
  _elapsed=$((_elapsed + SAMPLE_S))
  _samples=$((_samples + 1))
  _t=$(now_cs) || _t="?"
  if [ -n "$LAST_PID" ] && [ -r "$PROC_ROOT/$LAST_PID/stat" ]; then
    _now_st=$(starttime_of "$LAST_PID" 2>/dev/null || echo "")
    if [ "$_now_st" = "$LAST_ST" ]; then
      _alive=$((_alive + 1))
      log "SAMPLE n=$_samples at_cs=$_t pid=$LAST_PID starttime=$_now_st alive=yes same_generation=yes"
    else
      log "SAMPLE n=$_samples at_cs=$_t pid=$LAST_PID starttime=${_now_st:-none} alive=yes same_generation=no"
    fi
  else
    log "SAMPLE n=$_samples at_cs=$_t pid=$LAST_PID starttime=none alive=no same_generation=no"
  fi
done
log "PERSISTENCE_RESULT samples=$_samples alive=$_alive of=$_samples interval_s=$PERSIST_S"

# --- export channel ---------------------------------------------------------
# One snapshot, bound to the generation recorded above. If the generation changed during the
# persistence interval this still proceeds, because the helper's own checks will refuse a pair that
# no longer matches and we need that refusal recorded rather than hidden.
log "PHASE settle settle_s=$SETTLE_S"
_n=0
while [ "$_n" -lt "$SETTLE_S" ]; do
  sleep 1 || { log "OUTCOME CLOCK_UNAVAILABLE reason=sleep_failed"; exit 3; }
  _n=$((_n + 1))
done

log "PHASE export helper=$HELPER expect_pid=$LAST_PID expect_starttime=$LAST_ST"
# Capture the helper's own exit status. `if ! cmd; then _rc=$?; fi` would report the status of the
# NEGATION (always 0) instead of the helper's code, which is the kind of silently-wrong observation
# this project keeps having to unlearn.
"$HELPER" --manifest "$MANIFEST" --log "$LOG" --out "$EXPORT_OUT" \
      --settle 0 --app "$APP" \
      --expect-pid "$LAST_PID" --expect-starttime "$LAST_ST"
_hrc=$?
if [ "$_hrc" -ne 0 ]; then
  log "EXPORT_CALL_FAILED rc=$_hrc"
else
  log "EXPORT_CALL_OK rc=0"
fi

_final=$(now_cs) || _final="?"
log "DRIVER_DONE generations=$GEN_N final_generation_pid=$LAST_PID starttime=$LAST_ST final_cs=$_final"
log "OUTCOME COMPLETED generations=$GEN_N persistence_samples=$_samples persistence_alive=$_alive"
exit 0
