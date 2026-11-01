# GStreamer parser backport exact-static audit checkpoint

Status: complete; focused validation passed.

## Exact artifacts

### Subparse

- tar member: `./usr/lib/gstreamer-1.0/libgstsubparse.so`
- SHA-256: `8814f320ebb3ec9558e9455baaecf25ff51f527c49bd8ee716eae288fc564c1e`
- GNU Build ID: `0f86f3c35000b43071f28990a5d9e9b34140ed52`
- selected FDE: `[0xb7b0,0xb9bf)`

The `strlen` result is tested for zero and branches around last-byte address
formation and the terminal-byte write. The CVE-2017-5842-associated nonzero
length effect is present; the named underwrite mechanism is rejected for this
exact binary, without rejecting unrelated subtitle defects.

### Typefind

- tar member: `./usr/lib/gstreamer-1.0/libgsttypefindfunctions.so`
- SHA-256: `d772d31a2b64d393a72844bbfeba2f0efa12b93d6bf87f37818823958668df30`
- GNU Build ID: `224dc195678a0319cf6319c5db46551bc1d46740`
- selected FDE: `[0x2ca0,0x2d8b)`

The initial `<18` guard is present, but the later `<22` correction is absent.
The exact function can reach a four-byte read beginning at source offset 18 for
total lengths 18 through 21, leaving a bounded 4, 3, 2, or 1 bytes outside the
total range respectively.

## Canonical binding and safety

The analyzer streams selected regular members directly from canonical archive
SHA-256 `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`.
The manifest pins archive inventory, member identities, LLVM identities,
complete instruction/FDE count and hash, selected FDEs, and semantic anchors.
No recovered target was executed, no parser input was created, and no full
binary or full disassembly is retained.

Production delivery, parser execution, observable disclosure, code execution,
privilege gain/root access, and persistence remain unknown.

## Validation

Focused command:

```sh
<platformio-env>/bin/python3 -m pytest -q \
  tests/test_gstreamer_parser_backport_audit.py
```

Result: `18 passed, 43 subtests passed in 3.65s`.

Tracked artifact SHA-256 values:

- manifest: `42c900a3d8fe6376aa668d7af2b9443469589a9e46da59fb06f2dfac37d6460c`
- deterministic report: `bceb8886b4e3f4d9d67f0ff4b1398b412de0f27b6f20b0628d9cb3a35c730c73`
- bounded exact-static excerpt: `e43add89eed78b35090e611d70eda9a55cab36db31617fb988e187d00be0ec64`
