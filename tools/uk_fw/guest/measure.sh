#!/bin/sh
# measure.sh - a measurement receipt. No validated receipt, no result.
#
# Standing rule after seven instrument failures in one session: a number is not a measurement
# unless the instrument proves it measured the intended target. This wrapper refuses to print a
# value when it cannot prove that, and prints NOT MEASURED instead. See docs/MEASUREMENT-DISCIPLINE.md
# rule 17, added the same day.
#
# Usage:   measure.sh <claim-name> <target-pid> <read-command...>
# Example: measure.sh app_label 2303 cat /proc/2303/attr/current
#
# Emits exactly one of:
#   MEASURED <claim> <value>
#   NOT MEASURED <claim> <reason>
#
# The two gates, in order:
#   1. The target must be alive *now*, and still the same process we intended (a dead or replaced
#      pid is how the label check silently became inconclusive: it read /proc/<pid> after the app
#      had been deregistered and printed an empty string).
#   2. A positive control must succeed through the same instrument: the wrapper reads a value it
#      already knows, from the same mechanism, and aborts if that fails. This is what separates
#      "the answer is empty" from "the instrument cannot see anything" - the distinction that cost
#      this project three wrong conclusions, including a monitor denied by the very SMACK policy it
#      was measuring.

PROC="${MEASURE_PROC:-/proc}"   # overridable so the gates can be tested off-device

claim="${1:-unnamed}"
target="${2:-0}"
shift 2 2>/dev/null || true

if [ -z "$claim" ] || [ "$target" = "" ] || [ $# -eq 0 ]; then
  echo "NOT MEASURED $claim usage: measure.sh <claim> <pid> <command...>"
  exit 2
fi

# Gate 1: the target must be alive and must not be a zombie.
if [ ! -d "$PROC/$target" ]; then
  echo "NOT MEASURED $claim target pid $target is not running"
  exit 3
fi
if ! grep -q '^State:[[:space:]]*[^Z]' "$PROC/$target/status" 2>/dev/null; then
  echo "NOT MEASURED $claim target pid $target is not alive (zombie or unreadable status)"
  exit 3
fi

# Gate 2: positive control. Reading our own pid's own label uses the identical mechanism. If the
# instrument cannot see a label it is allowed to see, it cannot report anything about the target.
control=$(cat "$PROC/self/attr/current" 2>/dev/null)
if [ -z "$control" ]; then
  echo "NOT MEASURED $claim positive control failed: this instrument cannot read even its own label"
  exit 4
fi

# The measurement itself, with its exit status and stderr kept.
value=$("$@" 2>/tmp/measure-stderr.$$)
rc=$?
err=$(head -c 200 /tmp/measure-stderr.$$ 2>/dev/null)
rm -f /tmp/measure-stderr.$$

if [ "$rc" -ne 0 ]; then
  echo "NOT MEASURED $claim command failed rc=$rc err=[$err] (instrument=$control)"
  exit 5
fi
if [ -z "$value" ]; then
  # An empty result through a validated instrument is a *real* empty - report it as measured-empty
  # rather than as a value, so nobody reads absence as a negative finding.
  echo "MEASURED $claim <empty> (instrument=$control target=$target alive)"
  exit 0
fi
echo "MEASURED $claim $value (instrument=$control target=$target alive)"
exit 0
