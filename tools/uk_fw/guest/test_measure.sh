#!/bin/sh
# Self-test for measure.sh - the instrument must fail closed on every gate, or it is not an instrument.
# Runs anywhere, including macOS, by pointing MEASURE_PROC at a fake proc tree.
set -u
here=$(dirname "$0")
fake=$(mktemp -d)
mkdir -p "$fake/self/attr" "$fake/1234/attr" "$fake/5678"
printf 'App::home\n' > "$fake/self/attr/current"     # the instrument's own label (positive control)
printf 'App::home\n' > "$fake/1234/attr/current"     # a live target
printf 'State:\tS (sleeping)\n' > "$fake/1234/status"
printf 'State:\tZ (zombie)\n'   > "$fake/5678/status" # a dead-but-present target
pass=0; fail=0
check() { # check <expected-prefix> <label> <args...>
  want="$1"; label="$2"; shift 2
  out=$(MEASURE_PROC="$fake" sh "$here/measure.sh" "$@" 2>&1 | head -1)
  case "$out" in
    "$want"*) pass=$((pass+1)); printf '  [ok]   %s\n         %s\n' "$label" "$out" ;;
    *)        fail=$((fail+1)); printf '  [FAIL] %s\n         want %s... got: %s\n' "$label" "$want" "$out" ;;
  esac
}
check "MEASURED"          "live target, healthy instrument"        claim 1234 cat "$fake/1234/attr/current"
check "NOT MEASURED"      "dead pid is refused"                    claim 999999 cat "$fake/999999/attr/current"
check "NOT MEASURED"      "zombie target is refused"               claim 5678 cat "$fake/5678/attr/current"
check "NOT MEASURED"      "command failure is not a value"         claim 1234 cat "$fake/does-not-exist"
check "NOT MEASURED"      "usage error is refused"                 claim 1234

# The positive-control gate: an instrument that cannot read its own label must report nothing.
mv "$fake/self/attr/current" "$fake/self/attr/current.moved"
out=$(MEASURE_PROC="$fake" sh "$here/measure.sh" claim 1234 cat "$fake/1234/attr/current" 2>&1 | head -1)
case "$out" in
  "NOT MEASURED"*) pass=$((pass+1)); printf '  [ok]   %s\n         %s\n' "blind instrument refuses to report" "$out" ;;
  *)               fail=$((fail+1)); printf '  [FAIL] blind instrument reported: %s\n' "$out" ;;
esac
rm -rf "$fake"
printf '\n  %s ok, %s failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
