# Checkpoint: iAP2 marshal byte callers

## Status

Complete for direct static callers in the recovered `extracted-safe` corpus.
Downstream callback bodies remain a separate continuation.

## Exact results

- `libiAP2AppFramework-2.0.so`: 190,272 bytes,
  `d4d0558c9c53f02ee14024c081ccd83a02ca29404ef400131e2951f68a388120`.
- `iAP2Service-2.0`: 633,216 bytes,
  `38419131df82ec7e3c3b29a68ecc1a078c7f0b403051f137fe9f46f82b99f26e`.
- Only those two reviewed extracted-tree files carry the exact symbol string.
- `iAp2MarshalGetBytes` `0x21a56..0x21b21` and aligned accessor
  `0x21645..0x2176a` remain bounded; the helper performs no destination copy.
- Inventoried 31 exact direct calls across 11 service functions.
- Bound one caller-side null-source candidate in the heap-string materializer
  `0x2957c..0x296a7`.
- Bound 22 exact materializer calls from:
  - `SessionConnection` command `0x2afb` (`kCmdIdentificationSelect`); and
  - `SessionIdentification` command `0x2f95`
    (`kCmdIdentificationUpdate`).
- Bound plain `%s` logging of length-delimited byte pointers in AppLaunch,
  PlayMediaLibrary, and Communications callers.

## Deliverables

- `tools/uk_fw/iap2_marshal_getbytes_audit.py`
- `tests/test_iap2_marshal_getbytes_audit.py`
- `evidence/iap2-marshal-getbytes-caller-audit.md`
- `evidence/artifacts/projection-candidates/iap2-marshal-getbytes-audit.json`

Artifact:

- schema `ioniq-iap2-marshal-getbytes-audit/v1`;
- tool version `1.0.0`;
- size `27,905` bytes;
- file SHA-256
  `d5182ffe5700c481a45c568810b00b5813cf027b42ff883ad74b4dfc9df2f5f6`;
- canonical SHA-256
  `ef94c5f75e30855ed0c0cf9f178f9e4f93dcda34ba1a1ce7b205334fe5f0417d`.

## Validation

- focused pytest: `4 passed`;
- projection-focused pytest: `24 passed`;
- canonical suite: `1094 passed, 352357 subtests passed in 174.44s`;
- final canonical suite-log SHA-256:
  `f94a904c811374eac3b9c5c328604577cd8c2f36e89a37503cd251bd81f4ace2`;
- `py_compile`: passed;
- deterministic reproduction: passed;
- exclusive no-overwrite output: tested;
- exact subject hashes, range hashes, PT_LOAD mappings, and instruction anchors:
  passed.

## Boundaries

No target code ran and no protocol input was created. The results do not prove
physical delivery, successful iAP2 admission, process impact, information
exposure to an attacker, code execution, root, persistence, CVE identity, or
installed-unit applicability. Direct-call coverage does not exclude indirect
aliases, other extracted states, alternate builds, or defects in downstream
callbacks.
