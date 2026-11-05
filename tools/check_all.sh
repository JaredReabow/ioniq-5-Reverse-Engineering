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
[ "$rc" = 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit "$rc"

# Stage 6: the register's structural claims must still re-derive from image bytes. This is the check the
# four planners asked for, and it runs here so a claim cannot quietly stop being true.
if [ -d "work/decrypted-eu-260128/extracted-safe/mango-rootfs" ]; then
  echo "== verify_findings: re-deriving register claims from bytes =="
  if ! "${PYTHON:-python3}" tools/verify_findings.py > /tmp/verify-findings.out 2>&1; then
    echo "  FAIL: a structural claim no longer matches the image (see /tmp/verify-findings.out)"
    tail -20 /tmp/verify-findings.out
    exit 1
  fi
  grep -E 'pass, .* fail' /tmp/verify-findings.out | sed 's/^/  /'
fi
