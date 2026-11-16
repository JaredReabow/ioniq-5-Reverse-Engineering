#!/bin/sh
# crash-trace selftest — VERIFIED WORKING RECIPE (run 1793872985618150000).
#
# Purpose: prove the crash-trace interposer reaches its target BEFORE any real crash is
# interpreted. An empty /tmp/crash-trace.log must never be read as "no crash".
#
# Two things this script encodes, both learned the hard way:
#
#   1. `/etc/ld.so.preload` is consulted by the guest loader. Proven, not assumed: pointing it
#      at a bogus path makes the loader print
#          ERROR: ld.so: object '<path>' from /etc/ld.so.preload cannot be preloaded ...: ignored.
#      and any dynamically linked program then fails with rc=127.
#
#   2. The SUBJECT MUST BE DYNAMICALLY LINKED. A static binary (including tools/uk_fw/guest/
#      crash_probe.c built with -static) never invokes the loader, so ld.so.preload cannot reach
#      it and it will never produce a trace. An earlier version of this script used the static
#      probe and could not have passed for that reason alone.
#
# The subject used here is /app/bin/iAP2Service-2.0, a vendor dynamic glibc binary that aborts
# deterministically when /iap2_exploit sends its 0x2eff packet (glibc malloc consistency check).
#
# Run in the guest as root. Exit 0 = instrument reached its target.
#
# NOTE: the research image has no applet symlinks in $PATH; use /bin/busybox explicitly.

set -u
BB=/bin/busybox
PRELOAD=/etc/ld.so.preload
SHIM=/crash-trace.so
LOG=/tmp/crash-trace.log
SUBJECT=/app/bin/iAP2Service-2.0
TRIGGER=/iap2_exploit

fail() { echo "SELFTEST FAIL: $*" >&2; exit 1; }

[ -f "$SHIM" ]        || fail "$SHIM missing"
[ -x "$SUBJECT" ]     || fail "$SUBJECT missing"
[ -x "$TRIGGER" ]     || fail "$TRIGGER missing (needed as the deterministic abort trigger)"
export LD_LIBRARY_PATH=/app/lib:/lib

# --- Step 1: prove the loader consults /etc/ld.so.preload at all -------------------------
# A bogus path must make a dynamic program fail to start (glibc treats the preload error as
# non-fatal but then cannot resolve the real libs here, giving rc!=0). If the subject starts
# cleanly with a bogus preload, preload is NOT being read and everything below is meaningless.
echo "$PRELOAD <- bogus path"
echo /nonexistent-bogus.so > "$PRELOAD"
"$SUBJECT" --selftest-bogus >/tmp/selftest.bogus 2>&1
rc=$?
if [ "$rc" -eq 0 ]; then
	fail "subject started with a bogus preload; ld.so.preload is not consulted"
fi
grep -q "cannot be preloaded" /tmp/selftest.bogus \
	|| fail "no loader preload error; cannot conclude ld.so.preload is consulted"
echo "selftest: ld.so.preload IS consulted (loader reported the bogus object, rc=$rc)"

# --- Step 2: install the real shim and trigger a real abort ------------------------------
echo "$SHIM" > "$PRELOAD"
"$BB" rm -f "$LOG" /tmp/selftest.svc
"$SUBJECT" >/tmp/selftest.svc 2>&1 &
svcpid=$!
"$BB" sleep 5
"$TRIGGER" >/tmp/selftest.trigger 2>&1
echo "selftest: trigger rc=$?"
"$BB" sleep 3

# --- Step 3: assert the trace is real ----------------------------------------------------
[ -f "$LOG" ] || fail "no $LOG — interposer did not fire (pid $svcpid)"
grep -q "=== signal "        "$LOG" || fail "no signal banner"
grep -q -- "--- backtrace"   "$LOG" || fail "no backtrace section"
grep -q -- "--- maps ---"    "$LOG" || fail "no maps section"
grep -q "iAP2Service-2.0"    "$LOG" || fail "maps/backtrace do not name the subject"
grep -q "signal 6 (Aborted)" "$LOG" || fail "expected SIGABRT from the malloc check"

n=$(sed -n '/--- backtrace/,/--- maps ---/p' "$LOG" | grep -c "0x")
[ "$n" -ge 6 ] || fail "only $n frames; expected a full abort chain"

echo "SELFTEST PASS: crash-trace reached a dynamic vendor subject"
echo "  frames: $n   log lines: $($BB wc -l < "$LOG")"
echo "--- backtrace ---"
sed -n '/--- backtrace/,/--- maps ---/p' "$LOG"
exit 0
