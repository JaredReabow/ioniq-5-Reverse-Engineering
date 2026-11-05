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
