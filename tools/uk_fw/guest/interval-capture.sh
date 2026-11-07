#!/bin/sh
# interval-capture.sh - a compositor-interval capture that can prove its own boundary.
#
# Written after three defects made boot58 and boot65 incomparable (docs/kernel/42):
#   (a) the probe script that drove boot58 was never retained, so its timing is unknowable;
#   (b) the compositor log was exported by measuring a size and then streaming a still-growing
#       file, so the export exceeded its own declared length - boot58's only positive landed
#       19,494 bytes past the declared bound and 112 ms before the eventual end;
#   (c) the capture bound to `pidof <appname>`, which can select a different process generation
#       than the one under observation (boot65 saw three generations).
#
# This script exists so that a future run cannot repeat any of them. It emits a machine-readable
# receipt and refuses to claim more than it can prove. It does NOT interpret the result: the
# per-cause outcome is decided by tools/uk_fw/verify_interval_capture.py, because deciding
# "capture was too short" from inside the capture is how a truncated instrument becomes a
# confident negative.
#
# Preconditions implemented here:
#   1. SELF identity      - path, algorithm and digest, or an explicit `algo=none`.
#   2. Timed markers      - every marker carries monotonic uptime AND the driver's own offset.
#   3. Closed snapshot    - the export is bounded by `head -c` to the size just measured, then
#                           verified to decode to exactly that size.
#   4. Named generations  - pid AND /proc/<pid>/stat starttime per generation; the capture names
#                           the generation it was taken against.
#
# Usage:
#   interval-capture.sh --log /tmp/weston-real.log --app AppHomeScreen \
#                       --out /dev/ttyS2 --settle 20 --generation 2
#
# Exit status: 0 receipt emitted, 2 usage, 3 self-identity unavailable, 4 snapshot failed,
#              5 generation unresolved.

set -u

LOG=/tmp/weston-real.log
APP=AppHomeScreen
OUT=/dev/ttyS2
SETTLE=20
GENERATION=""
MARK_INTERVAL=1

usage() {
  echo "usage: interval-capture.sh [--log PATH] [--app NAME] [--out DEV] [--settle SEC] [--generation N]" >&2
  exit 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --log)        LOG=$2;        shift 2 ;;
    --app)        APP=$2;        shift 2 ;;
    --out)        OUT=$2;        shift 2 ;;
    --settle)     SETTLE=$2;     shift 2 ;;
    --generation) GENERATION=$2; shift 2 ;;
    -h|--help)    usage ;;
    *)            usage ;;
  esac
done

# ---------------------------------------------------------------- monotonic clock
# /proc/uptime's first field is monotonic seconds with centisecond resolution. It is the only
# monotonic source guaranteed on this 4.1.27 image without libc helpers.
#
# IC_UPTIME and IC_PROC exist so this script can be exercised off-device by a host test; they
# are not meant to be set on the guest. Without them the real paths are used.
UPTIME_FILE=${IC_UPTIME:-/proc/uptime}
PROC_ROOT=${IC_PROC:-/proc}

mono() {
  read -r up _rest < "$UPTIME_FILE" 2>/dev/null || up=0
  echo "$up"
}

# Convert "1234.56" to integer centiseconds so arithmetic is exact and portable.
centi() {
  case "$1" in
    *.*) echo "$(printf '%s' "$1" | tr -d '.' | sed 's/^0*\([0-9]\)/\1/')" ;;
    *)   echo "$1" ;;
  esac
}

T0_C=$(centi "$(mono)")

# Driver offset in centiseconds since this script started.
offset_c() {
  now=$(centi "$(mono)")
  echo $((now - T0_C))
}

emit() {
  printf '%s\n' "$*" >> "$OUT" 2>/dev/null || printf '%s\n' "$*"
}

# ---------------------------------------------------------------- precondition 1: self identity
SELF_PATH="$0"
SELF_ALGO=none
SELF_DIGEST=""

if command -v sha256sum >/dev/null 2>&1 && [ -r "$SELF_PATH" ]; then
  SELF_DIGEST=$(sha256sum "$SELF_PATH" 2>/dev/null | cut -d' ' -f1)
  [ -n "$SELF_DIGEST" ] && SELF_ALGO=sha256
fi
if [ "$SELF_ALGO" = none ] && command -v md5sum >/dev/null 2>&1 && [ -r "$SELF_PATH" ]; then
  SELF_DIGEST=$(md5sum "$SELF_PATH" 2>/dev/null | cut -d' ' -f1)
  [ -n "$SELF_DIGEST" ] && SELF_ALGO=md5
fi

emit "RECEIPT v1"
emit "SELF path=$SELF_PATH algo=$SELF_ALGO digest=${SELF_DIGEST:-none}"

if [ "$SELF_ALGO" = none ]; then
  # Precondition 1 cannot be met. Say so and stop: an unidentifiable harness is exactly the
  # defect that made boot58 unanalysable. Emitting measurements anyway would be the error.
  emit "OUTCOME HARNESS_UNIDENTIFIED reason=self_digest_unavailable"
  exit 3
fi

# ---------------------------------------------------------------- precondition 4: generations
# Field 22 of /proc/<pid>/stat is starttime in clock ticks since boot. Parsing must happen after
# the LAST ')' because comm can contain spaces and parentheses.
gen_starttime() {
  pid=$1
  [ -r "$PROC_ROOT/$pid/stat" ] || return 1
  sed 's/.*) //' "$PROC_ROOT/$pid/stat" 2>/dev/null | awk '{print $20}' 2>/dev/null
}

# Snapshot every live instance of the app name, with starttime, so a generation is pinned by
# (pid, starttime) rather than by name alone.
GEN_N=0
SNAP_PIDS=""
for p in $(pidof "$APP" 2>/dev/null || true); do
  st=$(gen_starttime "$p" 2>/dev/null || echo "")
  [ -z "$st" ] && continue
  GEN_N=$((GEN_N + 1))
  emit "GEN n=$GEN_N pid=$p starttime=$st phase=observed"
  SNAP_PIDS="$SNAP_PIDS $p:$st"
done

emit "GEN_COUNT count=$GEN_N app=$APP"

if [ -n "$GENERATION" ]; then
  # Pin the capture to a named generation. Resolve it to exactly one (pid, starttime) pair.
  SEL_PID=""
  i=0
  for pair in $SNAP_PIDS; do
    i=$((i + 1))
    if [ "$i" -eq "$GENERATION" ] 2>/dev/null; then
      SEL_PID=${pair%%:*}
      SEL_ST=${pair##*:}
    fi
  done
  if [ -z "$SEL_PID" ]; then
    emit "OUTCOME HARNESS_MISMATCH reason=requested_generation_absent requested=$GENERATION observed=$GEN_N"
    exit 5
  fi
  emit "TARGET generation=$GENERATION pid=$SEL_PID starttime=$SEL_ST binding=pinned_pid_and_starttime"
else
  emit "TARGET generation=unbound binding=name_only"
fi

# ---------------------------------------------------------------- precondition 2: timed markers
mark() {
  name=$1
  shift
  emit "MARK t_mono=$(mono) off_c=$(offset_c) name=$name $*"
}

mark driver_start log="$LOG" settle_s="$SETTLE"

# ---------------------------------------------------------------- settle: let the stream quiesce
# The settle delay exists so the snapshot is taken after the last interesting event rather than
# during it. This is the direct fix for boot58's 112 ms margin.
i=0
SETTLE_N=$((SETTLE / MARK_INTERVAL))
while [ "$i" -lt "$SETTLE_N" ]; do
  i=$((i + 1))
  sleep "$MARK_INTERVAL" 2>/dev/null || break
  mark settle_step step=$i of="$SETTLE_N"
done

# ---------------------------------------------------------------- precondition 3: closed snapshot
# Measure, then read EXACTLY that many bytes. The export can therefore never exceed its declared
# length, which is the defect that let boot58's bound be meaningless.
mark snapshot_measuring
SZ=$(wc -c < "$LOG" 2>/dev/null | tr -d ' ')
if [ -z "$SZ" ] || [ "$SZ" -le 0 ] 2>/dev/null; then
  emit "OUTCOME HARNESS_MISMATCH reason=log_unmeasurable log=$LOG"
  exit 4
fi

DIGEST=$(command -v sha256sum >/dev/null 2>&1 && head -c "$SZ" "$LOG" 2>/dev/null | sha256sum | cut -d' ' -f1)
[ -z "$DIGEST" ] && DIGEST=none

# First and last protocol timestamps inside the bounded region, so the verifier can compare the
# window against the milestone without trusting byte counts.
FIRST_TS=$(head -c "$SZ" "$LOG" 2>/dev/null | grep -ao '^\[[0-9]*\.[0-9]*\]' | head -1 | tr -d '[]')
LAST_TS=$(head -c "$SZ" "$LOG" 2>/dev/null | grep -ao '^\[[0-9]*\.[0-9]*\]' | tail -1 | tr -d '[]')

B64=$(head -c "$SZ" "$LOG" 2>/dev/null | base64 2>/dev/null | tr -d '\n')
B64_LEN=${#B64}

emit "CAPTURE file=$LOG bytes=$SZ digest=$DIGEST first_ts=${FIRST_TS:-none} last_ts=${LAST_TS:-none} b64_len=$B64_LEN seq=$((GEN_N))"
printf 'BEGIN interval %s\n%s\nENDinterval\n' "$SZ" "$B64" >> "$OUT" 2>/dev/null || true

# Verify the export round-trips to exactly the measured size. If it does not, the snapshot is not
# closed and nothing downstream may treat it as authoritative.
DECODED_LEN=$(printf '%s' "$B64" | base64 -d 2>/dev/null | wc -c | tr -d ' ')
if [ "$DECODED_LEN" != "$SZ" ]; then
  emit "OUTCOME SNAPSHOT_NOT_CLOSED measured=$SZ decoded=$DECODED_LEN"
  exit 4
fi

mark snapshot_closed bytes="$SZ"
emit "SNAPSHOT_CLOSED bytes=$SZ decoded=$DECODED_LEN match=yes"

# ---------------------------------------------------------------- hand off, do not judge
# No pass/fail here on purpose. "The milestone is absent" and "the window was too short to reach
# the milestone" are different claims and only the verifier, which can also see the harness
# identity and generation bindings, is allowed to distinguish them.
emit "OUTCOME CAPTURED bytes=$SZ first_ts=${FIRST_TS:-none} last_ts=${LAST_TS:-none} generation=${GENERATION:-unbound}"
exit 0
