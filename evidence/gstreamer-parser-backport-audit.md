# Exact-static GStreamer parser backport audit

## Question and boundary

This package characterizes two exact GStreamer plugin states from the canonical
EU 260128 rootfs. It answers only whether the reviewed machine-code effects of
three public upstream changes are present in those exact tar members.

The work is offline and static. The recovered plugins were not loaded or
executed, no parser input or media file was created, and no delivery path was
tested. The conclusions do not claim code execution, information disclosure,
root access, persistence, or production delivery.

## Canonical evidence binding

The sole firmware source for the published result is:

- archive: `work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz`
- SHA-256: `423491fd8b86bd815d4e12f47054e08a589a5159f87213f08980fcc3a0e47c84`
- size: 879,109,759 bytes
- tar members: 66,836
- normalized inventory SHA-256:
  `c85bc4b1b12bc4704c3aea30489bac99c10cb2211f80d94f48f3e1e22fd7a94c`

`gstreamer_parser_backport_audit.py` streams the gzip tar directly. For each
selected canonical name it requires one exact regular member with the expected
mode, size, SHA-256, and no link target. It rejects name aliases, duplicate
selected members, links, special nodes, unsafe names, archive inventory drift,
archive identity drift, and input changes observed during analysis. Temporary
private copies exist only long enough to pass the selected bytes to
`llvm-objdump` and `llvm-readelf`; they are removed automatically and are not
recovered targets executed by the analyzer.

The strict manifest also pins the Homebrew LLVM version and executable hashes,
each member's complete normalized instruction count/hash, complete FDE
count/hash, Build ID, selected FDE, and exact semantic anchors. Unknown or
missing JSON keys, duplicate keys, Boolean integers, malformed ranges or
instructions, unsupported commits/states, and all pinned evidence drift fail
closed.

## Public comparison basis

The comparison is effect-based rather than version-string-based:

- subparse fix commit:
  <https://gitlab.freedesktop.org/gstreamer/gst-plugins-base/-/commit/d894c19db62ce87115317616f0a5d4482d6332c4>
- typefind initial fix commit:
  <https://gitlab.freedesktop.org/gstreamer/gst-plugins-base/-/commit/2fdccfd64fc609e44e9c4b8eed5bfdc0ab9c9095>
- typefind corrected minimum commit:
  <https://gitlab.freedesktop.org/gstreamer/gst-plugins-base/-/commit/a3bf3094d17dded324c713d5d55968caa779a895>

The first commit adds the nonzero-length predicate before the subparse
last-byte access. The second adds an 18-byte minimum to the icon typefinder;
the third corrects that minimum to 22 bytes. These public semantics are then
compared with the exact instruction effects below.

## Result 1: `libgstsubparse.so`

Exact identity:

- member: `./usr/lib/gstreamer-1.0/libgstsubparse.so`
- SHA-256: `8814f320ebb3ec9558e9455baaecf25ff51f527c49bd8ee716eae288fc564c1e`
- GNU Build ID: `0f86f3c35000b43071f28990a5d9e9b34140ed52`
- selected FDE: `[0xb7b0,0xb9bf)`

Upstream commit `d894c19db62ce87115317616f0a5d4482d6332c4`, associated
with CVE-2017-5842, adds a nonzero-length condition before accessing
`attr_value[length - 1]`.

The exact function calls `strlen` at `0xb86b`, tests `%rax` at `0xb870`, and
branches on zero at `0xb873` to `0xb88d`. The last-byte address is formed only
after that branch at `0xb875`. The terminal double- and single-quote checks
then route to the byte write at `0xb928`.

**Conclusion:** the nonzero-length fix effect is present. The named zero-length
underwrite mechanism is backported/rejected for this exact binary. This is not
a claim that the subtitle parser has no unrelated defect.

## Result 2: `libgsttypefindfunctions.so`

Exact identity:

- member: `./usr/lib/gstreamer-1.0/libgsttypefindfunctions.so`
- SHA-256: `d772d31a2b64d393a72844bbfeba2f0efa12b93d6bf87f37818823958668df30`
- GNU Build ID: `224dc195678a0319cf6319c5db46551bc1d46740`
- selected FDE: `[0x2ca0,0x2d8b)`

Initial upstream commit `2fdccfd64fc609e44e9c4b8eed5bfdc0ab9c9095`, associated
with CVE-2016-9811, adds a `datalen < 18` return. Corrective commit
`a3bf3094d17dded324c713d5d55968caa779a895` changes the complete minimum to
22 bytes.

The exact function calls `gst_type_find_get_length` at `0x2cb9`, compares the
result with `0x11` at `0x2cbe`, and at `0x2cc2` admits only values greater than
17 to the parsing path. Values through 17 fall through to the return sequence.
The admitted path requests six bytes at `0x2ce2`/`0x2ced`; after the header
checks it reads the 32-bit size at source offset 14 and the 32-bit offset field
at source offset 18 (`movl 0x12(%rax),%eax` at `0x2d20`). There is no 22-byte
minimum guard before that exact read.

For total lengths 18, 19, 20, and 21, the four-byte read beginning at source
offset 18 therefore extends respectively 4, 3, 2, and 1 bytes beyond the total
range.

**Conclusion:** the initial `<18` guard is present, but the later complete
`<22` correction is absent. A bounded residual out-of-range read of 1 to 4
bytes remains possible in the reviewed exact function for total lengths 18
through 21.

This finding does not itself establish parser invocation, production delivery,
observable disclosure, a crash, code execution, privilege gain, root access,
or persistence.

## Reproduction

Use the repository's local Python environment and explicit pinned LLVM tools:

```sh
<platformio-env>/bin/python3 tools/uk_fw/gstreamer_parser_backport_audit.py \
  --rootfs work/decrypted-eu-260128/HU/images/mango-rootfs.tar.gz \
  --llvm-objdump <homebrew-llvm>/bin/llvm-objdump \
  --llvm-readelf <homebrew-llvm>/bin/llvm-readelf \
  --manifest evidence/artifacts/media-candidates/gstreamer-parser-backport-audit-manifest.json
```

The analyzer writes deterministic UTF-8/LF JSON through `sys.stdout.buffer`,
independent of `PYTHONIOENCODING`. Its expected output is
`evidence/artifacts/media-candidates/gstreamer-parser-backport-audit-report.json`.
Focused tests are:

```sh
<platformio-env>/bin/python3 -m pytest -q \
  tests/test_gstreamer_parser_backport_audit.py
```

## Tracked package

- `tools/uk_fw/gstreamer_parser_backport_audit.py`
- `tests/test_gstreamer_parser_backport_audit.py`
- `evidence/artifacts/media-candidates/gstreamer-parser-backport-audit-manifest.json`
- `evidence/artifacts/media-candidates/gstreamer-parser-backport-audit-report.json`
- `evidence/artifacts/media-candidates/gstreamer-parser-backport-exact-static.txt`
- `docs/agent-work/gstreamer-parser-backport-audit/PLAN.md`
- `docs/agent-work/gstreamer-parser-backport-audit/CHECKPOINT.md`

The tracked excerpt contains only the reviewed instruction windows and public
patch semantics. Full plugins, full disassemblies, and development downloads
remain outside the package.
