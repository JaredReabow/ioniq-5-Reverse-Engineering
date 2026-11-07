#!/bin/sh
# Every consistency check this repository has, in one command.
#
# These are cheap and they have each already caught something a careful read missed:
#   - register numbering and cross-references (found a stale V-056 heading still asserting the withdrawn claim)
#   - the append-only history invariant (found 21 historical rewrites and one future-dated entry)
#   - document cross-references (found links into files that had been renamed)
#
# Usage: sh tools/check_all.sh      (exit status is non-zero if any check fails)
set -e
cd "$(dirname "$0")/.."
PY=${PY:-python3.13}
rc=0
echo "=== register consistency ==="
"$PY" tools/check_register_consistency.py || rc=1
echo
echo "=== history is append-only ==="
"$PY" tools/check_history_append_only.py || rc=1
"$PY" tools/check_remediation_items.py || rc=1
# last few commits only: a document that lost sections in this session is worth seeing now
"$PY" tools/check_doc_shrinkage.py 5 || true
echo
echo "=== tooling parses ==="
pyfail=0
for f in $(git ls-files 'tools/*.py' 'tools/**/*.py'); do
  "$PY" -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$f" 2>/dev/null || { echo "  SYNTAX FAIL: $f"; pyfail=1; }
done
shfail=0
for f in $(git ls-files 'tools/*.sh' 'tools/**/*.sh'); do
  sh -n "$f" 2>/dev/null || { echo "  SHELL FAIL: $f"; shfail=1; }
done
[ "$pyfail" = 0 ] && [ "$shfail" = 0 ] && echo "all tooling parses" || rc=1
echo

echo "=== document cross-references ==="
"$PY" tools/check_doc_links.py || rc=1
echo

# Stage 6: the register's structural claims must still re-derive from image bytes. This is the check the
# four planners asked for, and it runs here so a claim cannot quietly stop being true.
#
# This stage and the ones below it used to sit after an `exit "$rc"`, which made them unreachable dead
# code: they were reported as wired in but had never executed. The summary and exit now come last, and
# Stage 6 uses "$PY" because bare python3 is broken on this host.
if [ -d "work/decrypted-eu-260128/extracted-safe/mango-rootfs" ]; then
  echo "=== verify_findings: re-deriving register claims from bytes ==="
  if ! "$PY" tools/verify_findings.py > /tmp/verify-findings.out 2>&1; then
    echo "  FAIL: a structural claim no longer matches the image (see /tmp/verify-findings.out)"
    tail -20 /tmp/verify-findings.out
    rc=1
  else
    grep -E 'pass, .* fail' /tmp/verify-findings.out | sed 's/^/  /' || true
  fi
  echo
fi

# Stage 7: the measuring instrument itself must fail closed. An instrument that reports a value when
# it is blind is worse than no instrument, and this project has paid for that lesson seven times.
if [ -f tools/uk_fw/guest/test_measure.sh ]; then
  echo "=== measure.sh self-test: the instrument must fail closed ==="
  if ! sh tools/uk_fw/guest/test_measure.sh > /tmp/measure-selftest.out 2>&1; then
    echo "  FAIL: the measurement wrapper did not fail closed (see /tmp/measure-selftest.out)"
    tail -12 /tmp/measure-selftest.out
    rc=1
  else
    tail -1 /tmp/measure-selftest.out | sed 's/^/  /'
  fi
  echo
fi

# Stage 8: the interval-capture harness must prove its own boundary, and the verifier must refuse to
# turn a truncated window into a negative. Both are direct consequences of docs/kernel/42.
echo "=== interval capture: closed-snapshot and per-cause-null guarantees ==="
mkdir -p work/test-tmp
if ! TMPDIR="$PWD/work/test-tmp" "$PY" -m unittest tests.test_interval_capture_script \
      tests.test_verify_interval_capture tests.test_make_run_manifest \
      > /tmp/interval-capture-tests.out 2>&1; then
  echo "  FAIL: the interval-capture harness or verifier broke a guarantee (see /tmp/interval-capture-tests.out)"
  tail -20 /tmp/interval-capture-tests.out
  rc=1
else
  tail -3 /tmp/interval-capture-tests.out | sed 's/^/  /'
fi
echo

[ "$rc" = 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit "$rc"
