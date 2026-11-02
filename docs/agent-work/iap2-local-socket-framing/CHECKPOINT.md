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
- Added deterministic tool, tests, evidence, and artifact.

## Validation

- Focused tests: `8 passed` across local framing and revised direct-caller audit.
- Canonical suite: `1103 passed, 352357 subtests passed in 180.10s`.
- Canonical suite-log SHA-256:
  `00166fa438bf61d3626e9cd4e5192395f31681170b3e4442448e947fb86d3b7c`.
- Local-framing artifact:
  - size `65,111`;
  - file SHA-256 `4aa88a9460cec0f02aad25e8a6ebef41231b2480dec669abe447447b360af728`;
  - canonical SHA-256 `2246011e805b39b9f38d1a3af674d299fd0fe782dc8a67c8c5bee7d1f0826336`.
- Revised direct-caller artifact:
  - tool version `1.2.0`;
  - size `31,652`;
  - file SHA-256 `0437b91abb2d48f844616594f0d7c7a26bed255171adc768fb4d9bdaa777887a`;
  - canonical SHA-256 `366d116d6154d6245c4fae6937b4f8666185183b665cd9bc877f6feb1161d8b2`.

## Open

- Recover exact upstream maximum lengths and allocation feasibility for the nine
  dynamic producers.
- Finish `iAp2MarshalPut*` failure/status handling and downstream callback/sink
  review for accepted transaction-tail pointers.
- Determine live socket mode/owner/label, `/tmp` traversal/transmutation,
  capabilities, loaded SMACK rules, and actual client identities only on a
  future passive disconnected owner bench.
- Seek a lawful fixed SDK comparator.

## Boundaries

No target binary ran and no socket, protocol message, device node, packet,
radio, or firmware state was touched. No live connection, physical delivery,
crash, disclosure, code execution, root, persistence, CVE identity, or
installed-unit applicability is claimed.
