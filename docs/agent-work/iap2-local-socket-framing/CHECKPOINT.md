# Checkpoint: iAP2 local-socket framing audit

## Completed

- Exact subjects:
  - framework SHA-256 `d4d0558c9c53f02ee14024c081ccd83a02ca29404ef400131e2951f68a388120`;
  - service SHA-256 `38419131df82ec7e3c3b29a68ecc1a078c7f0b403051f137fe9f46f82b99f26e`.
- Bound framework and service to AF_UNIX/SOCK_STREAM pathname
  `/tmp/iAp2Socket`.
- Bound service `umask(0)`, unlink/bind/listen, accept, 64-byte header framing,
  offset-`0x38` declared total, allocation, fixed header copy, body receive, and
  `handleClientCmd()` dispatch.
- Bound `handleClientCmd` `0x2ea28..0x2f1ad` and its direct calls to all 11
  reviewed byte-accessor caller functions plus both identification paths.
- Established the exact-static declared-total-below-64 heap OOB write candidate:
  the 64-byte copy precedes the lower-bound branch.
- Established positive-short-read uninitialized header/body candidates and the
  no-maximum resource-exhaustion candidate.
- Bound framework receiver symmetry.
- Verified all 37 direct `SendEventToApp` producers initialize at offset 64 and
  store/send `iAp2MarshalGetUsedSize()` as total transaction size.
- Identified nine dynamic uint32 capacity formulas for separate arithmetic and
  upstream-length review.
- Reconciled total-size framing with `iAp2MarshalInitFromTxn`: parse pointer is
  advanced by 64 while remaining is not reduced, yielding an exact-static
  transaction-tail OOB read candidate of up to 64 bytes.
- Verified configured UID 0, `App::projection`, and 19 labels with bilateral
  recovered SMACK write rules; retained runtime pathname and label gates.
- **Retired wrapped-capacity heap-overflow hypothesis**: Marshal writer family
  (`iAp2MarshalInit` at `0x21038`, `iAp2MarshalAlloc` at `0x211e5..0x211ee`,
  `iAp2MarshalPutBytes` at `0x215e3..0x215fe`, `iAp2MarshalGetUsedSize` at
  `0x21b87`) enforces remaining capacity before body copy. Wrapped/undersized
  capacity → alloc failure → `NULL` return → no `memcpy`. Dynamic producer
  arithmetic cannot reach wrap values (requires ~1 GiB; upstream parsers supply
  16-bit TLV lengths max 65535; max observed capacity ~524 KiB).
- **Producer residue documented**: `handleExternalAccessoryProtocolRecvData`
  (`0x141896`) unconditional header stores at `+0x00`, `+0x38`, `+0x3c` after
  possibly-failed marshal. Reachable only if `param_5 <= -0x19`; reviewed
  callers produce positive bounded lengths. Code smell, not demonstrated primitive.
- Added deterministic tool (v1.1.0), tests, evidence, and artifact.

## Validation

- Focused tests: `8 passed` across local framing and revised direct-caller audit.
- Canonical suite: `1103 passed, 352357 subtests passed in 145.55s`.
- Canonical suite-log SHA-256:
  `00166fa438bf61d3626e9cd4e5192395f31681170b3e4442448e947fb86d3b7c`.
- Local-framing artifact (regenerated v1.1.0):
  - canonical SHA-256 `163e51b395feee04fc883d2abad5b0e1df6d60b7885469ef7b314a8dccde44b5`.
- Revised direct-caller artifact:
  - tool version `1.2.0`;
  - size `31,652`;
  - file SHA-256 `0437b91abb2d48f844616594f0d7c7a26bed255171adc768fb4d9bdaa777887a`;
  - canonical SHA-256 `366d116d6154d6245c4fae6937b4f8666185183b665cd9bc877f6feb1161d8b2`.

## Open

- Finish `iAp2MarshalPut*` failure/status handling and downstream callback/sink
  review for accepted transaction-tail pointers (31 direct `iAp2MarshalGetBytes`
  callers).
- Complete external-accessory, file-transfer, HID, Wi-Fi, list-update consumer analysis.
- Build passive VM admission tooling for `/tmp/iAp2Socket` metadata, SMACK labels,
  capabilities.
- Seek a lawful fixed SDK comparator.

## Boundaries

No target binary ran and no socket, protocol message, device node, packet,
radio, or firmware state was touched. No live connection, physical delivery,
crash, disclosure, code execution, root, persistence, CVE identity, or
installed-unit applicability is claimed.
