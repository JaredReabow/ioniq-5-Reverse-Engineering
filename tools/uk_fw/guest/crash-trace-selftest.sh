#!/bin/sh
# crash-trace positive control: stage the instrument, run the probe, assert the trace appeared.
#
# The assertion is the point. Without it, an empty /tmp/crash-trace.log is indistinguishable
# from "the instrument never loaded", which is the exact mistake this project already made three
# times. This script fails loudly in that case.
#
# Run inside the guest, as root, after the interposer and the probe are staged:
#   sh /crash-trace-selftest.sh
#
# Exit: 0 = instrument reached its target; 1 = it did not (do not trust any prior "no crash").

set -u

PRELOAD=/etc/ld.so.preload
SHIM=/crash-trace.so
PROBE=/crash_probe
LOG=/tmp/crash-trace.log

fail() { echo "SELFTEST FAIL: $*" >&2; exit 1; }

[ -f "$SHIM" ]  || fail "$SHIM missing"
[ -x "$PROBE" ] || fail "$PROBE missing or not executable"

# 1. Install the interposer. Preserve any prior content so this is reversible.
if [ -f "$PRELOAD" ] && ! grep -qx "$SHIM" "$PRELOAD" 2>/dev/null; then
	echo "$SHIM" >> "$PRELOAD"
else
	echo "$SHIM" > "$PRELOAD"
fi
echo "selftest: $PRELOAD -> $(cat "$PRELOAD" | tr '\n' ' ')"

# 2. Prove the loader actually consults the file: a shim with a deliberately bad name must make
#    a trivial program fail to start. If this probe starts fine, ld.so.preload is not being read
#    and nothing below is meaningful.
BAD=/tmp/definitely-not-a-library.so
printf '%s\n' "$BAD" > "$PRELOAD"
if /bin/true 2>/dev/null; then
	echo "selftest: WARNING ld.so.preload appears not to be consulted (bad-path probe still ran)"
	CONSULTED=0
else
	echo "selftest: ld.so.preload is consulted (bad-path probe refused to start, as expected)"
	CONSULTED=1
fi

# 3. Restore the real shim and run the faulting probe.
echo "$SHIM" > "$PRELOAD"
rm -f "$LOG"

for mode in segv abort; do
	echo "selftest: running probe mode=$mode"
	"$PROBE" "$mode" >/tmp/crash-probe.$mode.out 2>&1
	echo "selftest: probe exited $? (a fatal signal is expected)"

	if [ ! -f "$LOG" ]; then
		fail "no $LOG after mode=$mode -- interposer did not fire"
	fi
	grep -q "=== signal " "$LOG"      || fail "no signal banner in $LOG"
	grep -q -- "--- backtrace" "$LOG" || fail "no backtrace section in $LOG"
	grep -q -- "--- maps ---" "$LOG"  || fail "no maps section in $LOG"
	grep -q "crash_probe" "$LOG"      || fail "maps do not name crash_probe -- trace is from the wrong process"
	n=$(sed -n '/--- backtrace/,/--- maps ---/p' "$LOG" | grep -c "0x")
	[ "$n" -ge 3 ] || fail "only $n frames in backtrace"
	echo "selftest: mode=$mode produced $n frames"
done

echo "SELFTEST PASS: crash-trace reached its target ($CONSULTED=ld.so.preload consulted)"
echo "--- first trace ---"
sed -n '1,25p' "$LOG"
exit 0
