# ABL IAS embedded-key trust checkpoint

## Status

Bounded package complete; exact proprietary ABL trust verdict remains open.

## Frozen evidence

- Canonical decrypted update archive and unique ABL member identity.
- Exact BPDT/CPD/IBB topology and ABL build strings.
- Canonical rootfs `ias_image_app` identity and instruction anchors.
- All twelve exact EU package-source identities and common carried RSA key.
- Intel `iasimage` commit and source hashes.
- Public Slim Bootloader Apollo Lake IAS key-hash-before-signature chain at
  commit `5f5c14b10ae6bd3cd0cf7e274142767dc2635a06`.
- Public-SBL candidate key digest and bounded absence from the exact 8 MiB
  flash bytes.

## Validation

- focused ABL package: `8 passed, 7 subtests passed`;
- ABL + matrix + DecryptToPIPE integration: `24 passed, 12 subtests passed`;
- canonical suite: `985 passed, 352199 subtests passed in 181.95s`;
- canonical log SHA-256:
  `43f52d366c9f83d664136f172f2ef316104820b1719f2c98969be3f3c3177b30`;
- report SHA-256:
  `2e6096d14d54d06af4ddd2989e80de1558ff8de081b64e64306ada123658f3b7`.

The canonical run initially exposed an intermittent host-only Python 3.13/macOS
pipe deadlock in the pre-existing boot-matrix helper's LZ4 subprocess. The
helper now drains stdin, stdout, and stderr concurrently with bounded output and
a timeout. Its matrix report is unchanged; the DecryptToPIPE report changed
only in the hash identity of that bound helper.

## Verdict

The public implementation pins the carried IAS OS key using a component digest
from the payload key-hash HOB. The exact LGE ABL has not yet been matched to
that code or trust-store record. Therefore exact key pinning and arbitrary-key
acceptance are both unresolved.

## Next exact work

1. Recover the IBB/IBBL executable mappings and compact-log references.
2. Locate exact callers of `iasImage`/`ipk.` parsing code.
3. Match key-normalization, SHA-256, RSA, and failure propagation to exact ABL
   instructions.
4. Recover the source of the expected key digest: BPM/IBBP manifest, CSE HOB,
   SMIP, `rot.key`, `oem.key`, or another verified structure.
5. Only then classify exact target key pinning.
