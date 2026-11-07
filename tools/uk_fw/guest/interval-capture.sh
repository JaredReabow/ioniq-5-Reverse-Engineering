#!/bin/sh
# interval-capture.sh - a compositor-interval capture that can prove its own boundary.
#
# REVISION 2. Revision 1 was REJECTED by Astra (docs/planning/astra-c9.md) with six blocking
# defects. Each is addressed here, and the mapping is stated so a later reader can check it:
#
#   A1  "closed snapshot" was five independent reads of a mutable pathname. Now the source is read
#       ONCE into a private snapshot file, and size, digest, timestamps and export are all derived
#       from that single immutable copy.
#   A2  `--generation N` was a `pidof` enumeration slot that shifted when a process exited. The
#       enumeration is GONE. A generation is now supplied by the launcher as an exact
#       (pid, starttime) pair and is mandatory.
#   A3  The binding was optional and never re-checked. It is now required, verified at start, and
#       re-verified immediately before the snapshot. Any change aborts the capture.
#   A4  Hashing this helper did not retain the harness that drove the run. The script now requires a
#       frozen run manifest naming the DRIVER and this HELPER with their SHA-256 digests, verifies
#       its own digest against the manifest, and records the manifest's identity in the receipt.
#       An unretained driver can no longer produce a valid receipt.
#   A5  A failed export could still emit SNAPSHOT_CLOSED and exit 0, because verification ran on the
#       in-memory copy. The export is now staged to a file, verified, then appended to the output
#       channel with its status checked. No suppressed failures anywhere.
#   A6  A failed `sleep` shortened the window silently, and the clock substituted 0 when uptime was
#       unreadable. Both now abort.
#
# What this script still does NOT do, and deliberately: it does not judge the result. "The milestone
# is absent" and "the window was too short to reach it" are different claims; only the host verifier
# (tools/uk_fw/verify_interval_capture.py) may distinguish them.
#
# Usage:
#   interval-capture.sh --manifest RUN_MANIFEST --log /tmp/weston-real.log \
#                       --expect-pid 2667 --expect-starttime 123456 \
#                       [--app AppHomeScreen] [--out /dev/ttyS2] [--settle 20]
#
# Exit status:
#   0 receipt emitted     2 usage        3 manifest missing/unverifiable or self-digest mismatch
#   4 source/snapshot failure          5 generation binding failed
#   6 export failed       7 clock unavailable

set -u

MANIFEST=""
LOG=/tmp/weston-real.log
APP=AppHomeScreen
OUT=/dev/ttyS2
SETTLE=20
EXPECT_PID=""
EXPECT_STARTTIME=""

usage() {
  echo "usage: interval-capture.sh --manifest FILE --expect-pid N --expect-starttime N [--log PATH] [--app NAME] [--out DEV] [--settle SEC]" >&2
  exit 2
}

while [ $# -gt 0 ]; do
  case "$1" in
    --manifest)         MANIFEST=${2:-}; shift 2 ;;
    --log)              LOG=${2:-}; shift 2 ;;
    --app)              APP=${2:-}; shift 2 ;;
    --out)              OUT=${2:-}; shift 2 ;;
    --settle)           SETTLE=${2:-}; shift 2 ;;
    --expect-pid)       EXPECT_PID=${2:-}; shift 2 ;;
    --expect-starttime) EXPECT_STARTTIME=${2:-}; shift 2 ;;
    -h|--help)          usage ;;
    *)                  usage ;;
  esac
done

if [ -z "$MANIFEST" ] || [ -z "$EXPECT_PID" ] || [ -z "$EXPECT_STARTTIME" ]; then
  echo "interval-capture: --manifest, --expect-pid and --expect-starttime are all required" >&2
  usage
fi

case "$SETTLE" in
  ''|*[!0-9]*) echo "interval-capture: --settle must be a non-negative integer" >&2; exit 2 ;;
esac
case "$EXPECT_PID" in
  ''|*[!0-9]*) echo "interval-capture: --expect-pid must be a positive integer" >&2; exit 2 ;;
esac
case "$EXPECT_STARTTIME" in
  ''|*[!0-9]*) echo "interval-capture: --expect-starttime must be a non-negative integer" >&2; exit 2 ;;
esac

# --- output channel ---------------------------------------------------------
# Every receipt line goes through emit, which FAILS the script on a write error. Revision 1's emit()
# silently fell back to stdout, which could split receipt and payload across channels (A5).
emit() {
  if printf '%s\n' "$*" >> "$OUT" 2>/dev/null; then
    return 0
  fi
  echo "interval-capture: FATAL receipt write failed on $OUT" >&2
  exit 6
}

# --- clock ----------------------------------------------------------------
# /proc/uptime's first field is monotonic seconds with centisecond resolution.
# Revision 1 substituted 0 when this failed, which silently produced meaningless offsets (A6).
UPTIME_FILE=${IC_UPTIME:-/proc/uptime}
PROC_ROOT=${IC_PROC:-/proc}

# Prints centiseconds on success. Prints nothing and returns non-zero on failure: the CALLER decides
# what to do. Putting emit/exit in here was a real bug in an earlier draft of this revision, because
# this function is evaluated inside $( ) and `exit` there only terminates the subshell, so the caller
# would have carried on with an empty timestamp.
read_uptime_cs() {
  if ! read -r _up _rest < "$UPTIME_FILE" 2>/dev/null; then
    return 1
  fi
  case "$_up" in
    ''|*[!0-9.]*) return 1 ;;
  esac
  _whole=${_up%%.*}
  if [ "$_whole" = "$_up" ]; then
    _frac=00
  else
    _frac=${_up#*.}
  fi
  while [ ${#_frac} -lt 2 ]; do _frac="${_frac}0"; done
  _frac=$(printf '%s' "$_frac" | cut -c1-2)
  _raw="$_whole$_frac"
  _out=$(printf '%s' "$_raw" | sed 's/^0*//')
  [ -z "$_out" ] && _out=0
  printf '%s\n' "$_out"
}

if ! T0_CS=$(read_uptime_cs); then
  emit "OUTCOME CLOCK_UNAVAILABLE reason=cannot_read_uptime file=$UPTIME_FILE"
  echo "interval-capture: cannot read or parse $UPTIME_FILE" >&2
  exit 7
fi

# One sample per marker, used for both fields, so t_mono and off_c describe the same instant (A6).
mark() {
  _name=$1
  shift
  if ! _now=$(read_uptime_cs); then
    emit "OUTCOME CLOCK_UNAVAILABLE reason=cannot_read_uptime file=$UPTIME_FILE at=$_name"
    echo "interval-capture: clock unavailable at marker $_name" >&2
    exit 7
  fi
  emit "MARK t_mono_cs=$_now off_c=$((_now - T0_CS)) name=$_name $*"
}

# --- A4: frozen run manifest ----------------------------------------------
# A self-hash proves nothing about the program that launched, slept, killed and relaunched. The
# manifest must name the driver and this helper with their digests; we verify our own digest against
# it, so a manifest describing a different helper cannot authorise this run.
if [ ! -r "$MANIFEST" ]; then
  echo "interval-capture: FATAL manifest not readable: $MANIFEST" >&2
  exit 3
fi

SELF_PATH=$0
if command -v sha256sum >/dev/null 2>&1; then
  HASH_CMD="sha256sum"
elif command -v shasum >/dev/null 2>&1; then
  HASH_CMD="shasum -a 256"
else
  echo "interval-capture: FATAL no SHA-256 tool available; refusing to measure" >&2
  exit 3
fi

hash_file() {
  # shellcheck disable=SC2086
  $HASH_CMD "$1" 2>/dev/null | cut -d' ' -f1
}

SELF_DIGEST=$(hash_file "$SELF_PATH")
if [ -z "$SELF_DIGEST" ]; then
  echo "interval-capture: FATAL cannot hash $SELF_PATH" >&2
  exit 3
fi

MANIFEST_DIGEST=$(hash_file "$MANIFEST")
[ -z "$MANIFEST_DIGEST" ] && { echo "interval-capture: FATAL cannot hash manifest" >&2; exit 3; }

# Extract the HELPER line's digest from the manifest. Format is one record per line:
#   HELPER path=<path> sha256=<digest>
#   DRIVER path=<path> sha256=<digest>
#   RUN id=<identifier>
MANIFEST_HELPER=""
MANIFEST_DRIVER=""
MANIFEST_DRIVER_DIGEST=""
MANIFEST_RUN=""
while IFS= read -r _line; do
  case "$_line" in
    HELPER\ *)
      MANIFEST_HELPER=$(printf '%s' "$_line" | sed -n 's/.*sha256=\([0-9a-f]\{64\}\).*/\1/p')
      ;;
    DRIVER\ *)
      # The path is everything between 'path=' and ' sha256=', which keeps paths containing
      # spaces intact. A first draft used [^ ]* and truncated at the first space; on this project
      # the repository path itself contains spaces, so the truncation produced a *directory* that
      # passed the readability test and then hashed to nothing. See the empty-digest check below.
      MANIFEST_DRIVER=$(printf '%s' "$_line" | sed -n 's/.*path=\(.*\) sha256=.*/\1/p')
      MANIFEST_DRIVER_DIGEST=$(printf '%s' "$_line" | sed -n 's/.*sha256=\([0-9a-f]\{64\}\).*/\1/p')
      ;;
    RUN\ *)
      MANIFEST_RUN=$(printf '%s' "$_line" | sed -n 's/.*id=\([^ ]*\).*/\1/p')
      ;;
  esac
done < "$MANIFEST"

if [ -z "$MANIFEST_HELPER" ] || [ -z "$MANIFEST_DRIVER" ] || [ -z "$MANIFEST_DRIVER_DIGEST" ]; then
  echo "interval-capture: FATAL manifest lacks HELPER or DRIVER records: $MANIFEST" >&2
  exit 3
fi

if [ "$MANIFEST_HELPER" != "$SELF_DIGEST" ]; then
  echo "interval-capture: FATAL self digest does not match the manifest (self=$SELF_DIGEST manifest=$MANIFEST_HELPER)" >&2
  exit 3
fi

# Verify the driver bytes still match the manifest. If the driver is gone, we cannot claim it was
# retained; that is exactly boot58's failure and must not pass silently.
if [ ! -r "$MANIFEST_DRIVER" ]; then
  echo "interval-capture: FATAL manifest names a driver that is not readable: $MANIFEST_DRIVER" >&2
  exit 3
fi
if [ ! -f "$MANIFEST_DRIVER" ]; then
  echo "interval-capture: FATAL manifest driver is not a regular file: $MANIFEST_DRIVER" >&2
  exit 3
fi
DRIVER_ACTUAL=$(hash_file "$MANIFEST_DRIVER")
# An empty digest means the hashing tool failed. Treat it as a hard failure rather than letting a
# mismatch message imply the bytes differed; the difference between "wrong bytes" and "never read
# the bytes" matters when diagnosing a bad harness.
if [ -z "$DRIVER_ACTUAL" ]; then
  echo "interval-capture: FATAL could not hash driver: $MANIFEST_DRIVER" >&2
  exit 3
fi
if [ "$DRIVER_ACTUAL" != "$MANIFEST_DRIVER_DIGEST" ]; then
  echo "interval-capture: FATAL driver digest mismatch (manifest=$MANIFEST_DRIVER_DIGEST actual=$DRIVER_ACTUAL)" >&2
  exit 3
fi

emit "RECEIPT v2"
# SELF carries the helper's own identity in the form the host verifier reads. HARNESS additionally
# records the *driver* and the manifest, because a self-hash alone does not retain the program that
# ran the experiment (Astra A4).
emit "SELF path=$SELF_PATH algo=sha256 digest=$SELF_DIGEST"
emit "HARNESS run=${MANIFEST_RUN:-unnamed} manifest=$MANIFEST manifest_sha256=$MANIFEST_DIGEST helper=$SELF_PATH helper_sha256=$SELF_DIGEST driver=$MANIFEST_DRIVER driver_sha256=$DRIVER_ACTUAL"

# --- A2/A3: mandatory generation binding ----------------------------------
# starttime is field 22 of /proc/<pid>/stat. After removing "pid (comm) ", original field 3 becomes
# field 1, so original field 22 is $20. Do not "correct" this to $22.
stat_starttime() {
  _pid=$1
  [ -r "$PROC_ROOT/$_pid/stat" ] || return 1
  sed 's/.*) //' "$PROC_ROOT/$_pid/stat" 2>/dev/null | awk '{print $20}' 2>/dev/null
}

verify_binding() {
  _phase=$1
  if [ ! -r "$PROC_ROOT/$EXPECT_PID/stat" ]; then
    emit "OUTCOME BINDING_FAILED phase=$_phase reason=pid_not_running pid=$EXPECT_PID"
    echo "interval-capture: pid $EXPECT_PID is not running at $_phase" >&2
    return 1
  fi
  _actual=$(stat_starttime "$EXPECT_PID")
  case "$_actual" in
    ''|*[!0-9]*)
      emit "OUTCOME BINDING_FAILED phase=$_phase reason=starttime_unreadable pid=$EXPECT_PID"
      return 1
      ;;
  esac
  if [ "$_actual" != "$EXPECT_STARTTIME" ]; then
    emit "OUTCOME BINDING_FAILED phase=$_phase reason=starttime_changed pid=$EXPECT_PID expected=$EXPECT_STARTTIME actual=$_actual"
    echo "interval-capture: pid $EXPECT_PID was replaced (expected starttime $EXPECT_STARTTIME, got $_actual)" >&2
    return 1
  fi
  emit "BINDING phase=$_phase pid=$EXPECT_PID starttime=$_actual state=verified"
  return 0
}

emit "TARGET app=$APP binding=pinned_pid_and_starttime pid=$EXPECT_PID starttime=$EXPECT_STARTTIME generation=launcher_supplied"
verify_binding start || exit 5

mark driver_start log="$LOG" settle_s="$SETTLE" app="$APP"

# --- settle ---------------------------------------------------------------
# A failed sleep must abort rather than silently shorten the observation window (A6).
_i=0
while [ "$_i" -lt "$SETTLE" ]; do
  _i=$((_i + 1))
  if ! sleep 1 2>/dev/null; then
    emit "OUTCOME CLOCK_UNAVAILABLE reason=sleep_failed after_s=$_i"
    echo "interval-capture: sleep failed during settle" >&2
    exit 7
  fi
  mark settle_step step="$_i" of="$SETTLE"
done

# --- A3: re-verify the binding immediately before the snapshot -------------
verify_binding pre_snapshot || exit 5

# --- A1: one immutable snapshot, then derive everything from it ------------
# Revision 1 opened the source five times; a rotation or in-place overwrite between reads could make
# the receipt describe a different object than the one measured. Here the source is read ONCE into a
# private file, and every subsequent value comes from that file.
SNAP="${IC_SNAP:-/tmp/interval-snapshot.$$.bin}"
mark snapshot_acquiring source="$LOG" snapshot="$SNAP"

if [ ! -r "$LOG" ]; then
  emit "OUTCOME SNAPSHOT_FAILED reason=source_unreadable source=$LOG"
  echo "interval-capture: source log not readable: $LOG" >&2
  exit 4
fi
SRC_SIZE_BEFORE=$(wc -c < "$LOG" 2>/dev/null | tr -d ' ')
if [ -z "$SRC_SIZE_BEFORE" ]; then
  emit "OUTCOME SNAPSHOT_FAILED reason=source_unmeasurable source=$LOG"
  exit 4
fi

if ! cp "$LOG" "$SNAP" 2>/dev/null; then
  emit "OUTCOME SNAPSHOT_FAILED reason=copy_failed source=$LOG snapshot=$SNAP"
  echo "interval-capture: could not copy $LOG to $SNAP" >&2
  exit 4
fi

SRC_SIZE_AFTER=$(wc -c < "$LOG" 2>/dev/null | tr -d ' ')
SNAP_SIZE=$(wc -c < "$SNAP" 2>/dev/null | tr -d ' ')

# The snapshot must be a whole copy of what we measured before copying. A short copy is fatal.
if [ "$SNAP_SIZE" != "$SRC_SIZE_BEFORE" ]; then
  emit "OUTCOME SNAPSHOT_INCOMPLETE expected=$SRC_SIZE_BEFORE snapshot=$SNAP_SIZE"
  echo "interval-capture: snapshot is $SNAP_SIZE bytes, expected $SRC_SIZE_BEFORE" >&2
  exit 4
fi

# If the source grew during the copy we record it rather than pretending the boundary was quiet.
GREW=no
if [ "$SRC_SIZE_AFTER" != "$SRC_SIZE_BEFORE" ]; then
  GREW=yes
fi
emit "SOURCE_BOUNDARY size_before=$SRC_SIZE_BEFORE size_after=${SRC_SIZE_AFTER:-unknown} grew_during_copy=$GREW"

# From here on, everything is derived from $SNAP only.
SNAP_DIGEST=$(hash_file "$SNAP")
[ -z "$SNAP_DIGEST" ] && { emit "OUTCOME SNAPSHOT_FAILED reason=digest_failed"; exit 4; }

FIRST_TS=$(head -c "$SNAP_SIZE" "$SNAP" 2>/dev/null | grep -ao '^\[[0-9]*\.[0-9]*\]' | head -1 | tr -d '[]')
LAST_TS=$(head -c "$SNAP_SIZE" "$SNAP" 2>/dev/null | grep -ao '^\[[0-9]*\.[0-9]*\]' | tail -1 | tr -d '[]')

# --- A5: stage, verify, then append ---------------------------------------
B64_FILE="${IC_B64:-/tmp/interval-payload.$$.b64}"
if ! head -c "$SNAP_SIZE" "$SNAP" 2>/dev/null | base64 2>/dev/null | tr -d '\n' > "$B64_FILE"; then
  emit "OUTCOME EXPORT_FAILED reason=encode_failed"
  echo "interval-capture: could not encode the snapshot" >&2
  exit 6
fi
B64_SIZE=$(wc -c < "$B64_FILE" 2>/dev/null | tr -d ' ')

# Verify the staged payload decodes back to the snapshot size BEFORE claiming anything.
DECODED_SIZE=$(base64 -d < "$B64_FILE" 2>/dev/null | wc -c | tr -d ' ')
if [ "$DECODED_SIZE" != "$SNAP_SIZE" ]; then
  emit "OUTCOME SNAPSHOT_NOT_CLOSED snapshot=$SNAP_SIZE decoded=$DECODED_SIZE"
  echo "interval-capture: staged payload decodes to $DECODED_SIZE, expected $SNAP_SIZE" >&2
  exit 4
fi

emit "CAPTURE snapshot=$SNAP bytes=$SNAP_SIZE digest=$SNAP_DIGEST first_ts=${FIRST_TS:-none} last_ts=${LAST_TS:-none} b64_bytes=${B64_SIZE:-0} source=$LOG"
emit "SNAPSHOT_CLOSED bytes=$SNAP_SIZE decoded=$DECODED_SIZE match=yes"

# Append the payload to the output channel with its status checked. No '|| true'.
if ! { printf 'BEGIN interval %s\n' "$SNAP_SIZE"; cat "$B64_FILE"; printf '\nENDinterval\n'; } >> "$OUT" 2>/dev/null; then
  emit "OUTCOME EXPORT_FAILED reason=channel_write_failed bytes=$B64_SIZE"
  echo "interval-capture: writing the payload to $OUT failed" >&2
  exit 6
fi
emit "EXPORT_WRITTEN bytes=$B64_SIZE channel=$OUT"

rm -f "$SNAP" "$B64_FILE" 2>/dev/null

mark snapshot_exported bytes="$SNAP_SIZE"

# No verdict. The host decides.
emit "OUTCOME CAPTURED bytes=$SNAP_SIZE first_ts=${FIRST_TS:-none} last_ts=${LAST_TS:-none} binding=pinned_pid_and_starttime pid=$EXPECT_PID starttime=$EXPECT_STARTTIME"
exit 0
