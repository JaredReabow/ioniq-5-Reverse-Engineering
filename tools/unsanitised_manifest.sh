#!/bin/sh
# Regenerate unsanitised/manifest/ - the identity of every held-back artefact.
#
# Two design notes, both from failures while writing this:
#
# 1. `work/decrypted-eu-260128` holds 463,964 files. A per-file manifest of half a million rows is
#    neither readable nor useful, so there are two levels and the file says which is which:
#      keys.tsv  - per-file sha256 for the small set that must not be published but must be identifiable
#      sets.tsv  - per set: file count, total bytes, and a STRUCTURAL digest over the sorted listing.
#    The structural digest proves two people hold the same tree shape and sizes without republishing
#    the bytes. It is weaker than a content hash and the note column says so.
#
# 2. The first version looped `wc -c` per file and timed out twice at 900 s, because it spawned
#    ~470,000 processes. Batching through `stat` per set does the same work in ~6 s. A tool that
#    cannot finish is not a tool.
set -eu
cd "$(dirname "$0")/.."
mkdir -p unsanitised/manifest

keys=unsanitised/manifest/keys.tsv
{
  printf 'path\tsize_bytes\tsha256\n'
  find work/abl-key-components -type f 2>/dev/null | LC_ALL=C sort | while IFS= read -r f; do
    printf '%s\t%s\t%s\n' "$f" "$(wc -c < "$f" | tr -d ' ')" "$(shasum -a 256 "$f" | cut -d' ' -f1)"
  done
} > "$keys"

sets=unsanitised/manifest/sets.tsv
{
  printf 'set\tfiles\ttotal_bytes\tstructural_sha256\tnote\n'
  for s in work/abl-key-components work/decrypted-eu-260128 evidence/vehicle-usb evidence/upstream; do
    [ -e "$s" ] || continue
    listed=$(mktemp)
    # stat -f '%z %N' is BSD; batched with + so it is one process per thousand files, not per file.
    find "$s" -type f -exec stat -f '%z %N' {} + 2>/dev/null | LC_ALL=C sort -k2 > "$listed"
    n=$(wc -l < "$listed" | tr -d ' ')
    bytes=$(awk '{s+=$1} END{printf "%.0f", s}' "$listed")
    digest=$(shasum -a 256 "$listed" | cut -d' ' -f1)
    rm -f "$listed"
    printf '%s\t%s\t%s\t%s\tstructural-only-not-content\n' "$s" "$n" "$bytes" "$digest"
  done
} > "$sets"

printf '  %s (%s key files with content hashes)\n' "$sets" "$(($(wc -l < "$keys") - 1))"
awk -F'\t' 'NR>1{printf "    %-30s %8s files  %14s B\n", $1, $2, $3}' "$sets"
