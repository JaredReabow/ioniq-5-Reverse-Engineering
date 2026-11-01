# GStreamer 2026 backport exact-static audit checkpoint

## Status

Implementation, strict manifest, deterministic report, bounded evidence,
documentation, and focused tests are complete. Only the nine authorized paths
were created or modified. Nothing was staged, committed, or pushed.

## Exact pinned results

- Canonical archive: size `879109759`, SHA-256
  `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`,
  `66836` members, inventory SHA-256
  `c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c`.
- RIFF member: size `59256`, instruction count/digest `8084` /
  `63d273a3fbe4d13594f3c1a18072f9d3b36770e2d589f9f04b29f9d01ae1f987`,
  FDE count/digest `17` /
  `815880e1bbd13e6819136305cb584a7eaab41e87d077c307468be478ddcc7d66`.
- RealMedia member: size `142128`, instruction count/digest `19045` /
  `308bcc916905d38809d3feecc5115be5791d5ccdc40c405ecfa13cf29b37d0cc`,
  FDE count/digest `141` /
  `b8671586965366718f94e25c915e6c695c52f72a801db5ff0ffb790efaf9a196`.
- Manifest SHA-256:
  `78e8f49f6064351f7a90e0c54321698d39716d8b6d8cfbc3bc563b8566029fa4`.
- Deterministic report: `5381` bytes, SHA-256
  `49d67b1773de9243615b54795538867398756b5554b9f6c04f1a4e1f0d8bd2df`.

## Commands and results

Focused tests (canonical exact run was available and was not skipped):

```text
/Users/leo/.platformio/penv/bin/python3 -m unittest -v tests/test_gstreamer_2026_backport_audit.py
```

Result: `Ran 24 tests in 3.611s` and `OK`.

Compilation checks:

```text
/Users/leo/.platformio/penv/bin/python3 -m py_compile tools/uk_fw/gstreamer_2026_backport_audit.py tests/test_gstreamer_2026_backport_audit.py
```

Result: exit status 0, no output.

Deterministic regeneration used the following analyzer arguments twice, once
with `PYTHONIOENCODING=utf-16:strict` and once with
`PYTHONIOENCODING=ascii:replace`:

```text
/Users/leo/.platformio/penv/bin/python3 tools/uk_fw/gstreamer_2026_backport_audit.py --rootfs work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz --llvm-objdump /opt/homebrew/opt/llvm/bin/llvm-objdump --llvm-readelf /opt/homebrew/opt/llvm/bin/llvm-readelf --manifest evidence/artifacts/media-candidates/gstreamer-2026-backport-audit-manifest.json
```

Result: byte-for-byte `cmp` succeeded; the first output was installed as the
tracked report. The report hash and byte count are recorded above.

UTF-8/LF validation decoded each of the eight then-existing package files with
strict UTF-8, rejected any CR byte, and required a final LF:

```text
/Users/leo/.platformio/penv/bin/python3 - <<'PY'
# strict UTF-8 decode + no-CR + final-LF assertions over the package paths
PY
```

Result: `utf8_lf_files=8`. The final strict UTF-8/LF/no-CR/no-trailing-
whitespace check including this checkpoint reported
`utf8_lf_no_trailing_whitespace_files=9`.

Final whitespace check:

```text
git diff --check
```

Result: exit status 0 with no diagnostics (`git_diff_check=ok`).

## Safety and limitations

- No recovered target binary or plugin was executed or loaded.
- No media input was created, loaded, or parsed; no malformed media, trigger,
  exploit material, callable target coordinate, proprietary binary, full
  disassembly, or operational device procedure was emitted.
- Conclusions are limited to the pinned archive/member/tool identities and the
  three exact local invariants. They do not establish exact installed/runtime
  reachability, delivery, parser execution, crash, disclosure, code execution,
  privilege/root, or persistence.
- The analyzer deliberately fails closed on any other patch state, binary,
  archive inventory, LLVM identity, or mixed/contradictory semantic state.
