# ABL IAS embedded-key trust checkpoint

## Status

Exact proprietary ABL carried-key pinning is closed; expected-digest provisioning remains open.

## Frozen evidence

- Canonical decrypted update archive and unique ABL member identity.
- Exact BPDT/CPD/IBB topology and ABL build strings.
- Canonical rootfs `ias_image_app` identity and instruction anchors.
- All twelve exact EU package-source identities and common carried RSA key.
- Intel `iasimage` commit and source hashes.
- Public Slim Bootloader Apollo Lake IAS key-hash-before-signature chain at
  commit `5f5c14b10ae6bd3cd0cf7e274142767dc2635a06`.
- Public-SBL candidate key digest and bounded absence from stored flash bytes.
- Strict raw-LZ4 recovery and identities for all three compressed IBB stages.
- Stage-1 load base `0xe0000`, exact authentication range, complete direct-call
  inventory, key-hash input, 32-byte comparison, failure edge, and later RSA
  verification.
- Exact type-3 OS path using the pinned-key routine with selector `0x27`.
- Byte-free exact-static disassembly excerpt SHA-256
  `5c069c0b869288e38087ad25dc86c8efa18d2f16799a8c26434dc8d82515932b`.

## Validation

- focused ABL package: `10 passed, 7 subtests passed`;
- ABL + matrix + DecryptToPIPE integration: `26 passed, 12 subtests passed`;
- canonical suite: `987 passed, 352199 subtests passed in 178.63s`;
- canonical log SHA-256:
  `c487e1c117cecdbb33a2e37ae188c3f67277ab8c377c645ce1220fb8babc761b`;
- report SHA-256:
  `df9d9a2f730efb2103a11113f028008ac3c36b1b05293602d72958f5612c5fa6`.

The canonical run initially exposed an intermittent host-only Python 3.13/macOS
pipe deadlock in the pre-existing boot-matrix helper's LZ4 subprocess. The
helper now drains stdin, stdout, and stderr concurrently with bounded output and
a timeout. Its matrix report is unchanged; the DecryptToPIPE report changed
only in the hash identity of that bound helper.

## Verdict

The exact `rel.1714-HF3` LGE ABL hashes the carried modulus/exponent, compares
that digest with a selected 32-byte runtime hash record, fails on mismatch, and
only then performs RSA payload verification. Its type-3 OS path uses this
routine with selector `0x27`. Arbitrary carried-key acceptance is therefore
rejected by the exact path. The persistent source and authenticated delivery of
the expected digest are not yet identified.

## Next exact work

1. Trace the runtime descriptor table at `0xc10c0`/`0xc10c8` back to its
   persistent source and authenticated delivery path.
2. Recover selector `0x27`'s exact semantic name and matching hash record.
3. Determine normal-versus-`_sub` image selection, attempt counters, health,
   mark-good, rollback, and recovery.
4. Bind the expected digest bytes if they are present in a manifest, SMIP,
   `rot.key`, `oem.key`, or a CSE-supplied object.
