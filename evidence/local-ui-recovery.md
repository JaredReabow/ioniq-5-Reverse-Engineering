# Local UI recovery: boot-public-key and Mac-updater hypotheses

2026-10-21. **No genuine infotainment application or validated firmware plaintext
was recovered.** This continuation tested two additional, bounded hypotheses
using existing packages, the installed Navigation Updater and installed tools.
It did not download anything, execute the updater, contact an update API, access
the head unit or flash firmware.

The existing VM still works: fresh serial and whole-frame/keyboard graphical
checks pass, as do **137 unit tests**. Those graphics remain our diagnostic,
not Hyundai/LG's UI.

## 1. Could the boot-container public key recover a wrapped block?

The older Chimaera description mentions a public RSA operation on wrapped key
material. That motivates a test, **not an assumption that boot signing and
payload wrapping use the same key or format**.

All six plaintext `ipk.` containers in each of the EU `260128` and AU `260319`
packages have the same RSA-2048 public key, exponent 65537. Modulus SHA-256:

```text
227d89f5a3cabed4efb8e67d5a0f9fa29d03a6759b8a150503fb383698fedea6
```

All 12 signatures pass strict PKCS#1 v1.5 type-1 recovery and comparison of the
recovered SHA-256 DigestInfo with the actual signed bytes. This verifies the
containers against their embedded public key; it does not prove bootloader
acceptance of a replacement key.

`tools/uk_fw/public_rsa_probe.py` tests every fully contained 256-byte block,
at one-byte strides, in each selected file's first/last 16 KiB. Overlapping
ranges merge, so the small upgrade descriptors are scanned whole. Both big-
and little-endian block representations are tested. Only strict type-1 padding
is accepted; recovered bytes are not printed or retained, only their length,
classification and digest.

| Measurement | Result |
|---|---:|
| Opaque envelopes | 38: 19 per package |
| Sample bytes read | 1,215,130 |
| Public RSA attempts | 2,392,520 |
| Valid type-1 blocks | **0** |

The input selection uses the earlier package inventory, excludes the two
front-key MCU images per package and the empty marker file, and verifies
sample prefixes/sizes against that inventory. Each report records exact
half-open ranges and their hashes, not an implied full-file hash.

**Controls:** 13 new tests cover real synthetic signatures, a synthetic
16-byte non-DigestInfo type-1 payload, wrong/short padding, type-2 rejection,
byte order, unaligned/final offsets, edge merging, unchanged input, refusal to
overwrite output, and rejection of a modified signed container. The non-digest
control matters: this is not merely a search for SHA-256 signature blocks.

**Boundary:** no conclusion about another public key, other padding/encoding,
interior ranges, split blocks or an AES key elsewhere in the package. This is
not RSA private-key recovery or a proof that local decryption is impossible.

## 2. Does the installed Mac updater supply usable firmware crypto?

Target: `/Applications/Navigation Updater.app/Contents/MacOS/Navigation Updater`.
Bundle version `261.015.0.215`; size 67,950,208 bytes; SHA-256:

```text
7b63734d60ca42648e81fcf12a9518c46077859554c050e2134dc27120e0f37c
```

### Static observations

REA `inspect_macho` identifies an x86-64 Mach-O, UUID
`956B1973-013F-36BE-8D60-661E2F04F1D2`. Complete retained Evidence:
`local-ui-recovery/updater-macho.json`, ID
`ev_1455e1dd1062656f90d7ac28fc97a5047c52b9821356fddabcb4221cd514f03f`.
Its symbol coverage is explicitly limited by stripping/toolchain visibility.

The REA/Ghidra function request timed out after 330 seconds during whole-image
analysis. Its diagnostic is retained in `updater-decrypt-function.json`.
**It did not produce a function dossier or successful decompilation.** The
following observations instead come from installed LLVM `llvm-nm` and
`llvm-objdump`; they are not mislabeled as REA function evidence.

**Temporary-path exception:** despite project-local `TMPDIR`, the REA provider
reported an internally selected `/tmp/rea-ghidra-socket-*` endpoint. This did
not fully meet the intended project-only temporary-path policy. No manual
cleanup outside the project was performed. Do not repeat this provider route
under that policy without a configurable project-local socket location; the
subsequent LLVM analysis wrote its outputs inside the project.

- `aesutils::EncryptedText::decryptAsUpdate` at `0x10026d250` Base64-decodes
  its text input, assembles constant byte strings, and calls
  `TinyAES256::cbc_decrypt` at `0x10026d4b3`.
- The key/IV strings are constructed from `_array0` / `_array1` bytes through
  two `%c` format strings, then copied unchanged into byte vectors. The
  reconstructed lengths are 32 and 16 bytes respectively.
- A separate `PlainText::toEncrypt` branch hex-decodes the named
  `AuthenticationConstants::ENCRYPT_KEY` / `ENCRYPT_IV` strings and uses
  `TinyAES::cbc_encrypt` (AES-128). The global constructor identifies the two
  32-character source strings.
- Direct calls into `toDecrypt` / `toEncrypt` appear in named disassembly
  regions for deep-link handling, authorization time, INI values, request
  parameters and error logs. **No firmware-payload decoding link was
  established by this call-site examination.**

Relevant instruction ranges, caller records and the one-build reconstruction
script are retained. Raw key/IV values are not included in the reports.
The script refuses a different updater hash. This is static reconstruction,
not runtime observation of the updater or proof that its constants apply to
head-unit firmware.

### Bounded candidate test

Two observed constant pairs were tested against the same 38 opaque envelopes:

- CBC input starts at **each byte offset 0 through 16,384**, inclusive;
- 512-byte plaintext sample per start;
- IV hypotheses: zero, the corresponding updater constant, the file's first
  block, and the preceding block when available;
- recognition: `ipk.`, ELF, gzip or XML prefix, or checksum-valid ustar header.

That is **4,979,824 key/start/IV hypotheses**. The implementation decrypts once
per key/start with zero IV, then changes only the first plaintext block for
other IV hypotheses, using the CBC relation. Other blocks are unchanged.

**Controls:** the independent NIST SP 800-38A AES-128-CBC known-answer vector
passes; a synthetic XML ciphertext at an unaligned offset is found with its
preceding IV. These validate the probe path, not execution-equivalence with
the updater's complete crypto implementation.

Two raw gzip-prefix matches occurred: EU and AU `iasImage_1920_12`, offset
12,267, under the same AES-128/file-first-block hypothesis. Their sample hashes
are identical. Both have gzip flags **`0xc6`**, including reserved bits, and
zlib rejects them with **`unknown header flags set`**. A synthetic valid gzip
control passes. **Neither marker match is recovered firmware.**

Reports: `updater-aes-probe.json` and `updater-aes-validation.json`.

**Boundary:** other updater crypto modes/derivations were not exhaustively
traced. Other firmware keys, IV rules, modes, encodings, start locations and
plaintext types remain untested. The tested text/API constants are not
established firmware keys. No broad claim of key absence follows.

## 3. VM and evidence regressions

Fresh runs:

- Serial: `work/vm/bootable/runs/1792537568609140000`; root/userspace true,
  guest `id` exit 0, no timeout/error, QEMU exit 0.
- Graphics: `work/vm/graphics/runs/1792537568608919000`; same boot result,
  R/G/B/Q interaction and complete expected-frame checks pass, QEMU exit 0.
- All prepared artifact hashes match each workspace's existing `prepare.json`
  **after** the runs.
- All 8 entries in `vm-local-only/evidence-sha256.json` and all 11 entries in
  `vm-graphics/evidence-sha256.json` still match. Original evidence was not
  overwritten to record later outcomes.
- Full suite: **137 tests pass**, using existing PlatformIO Python and
  project-local `TMPDIR`. Retained output: `local-ui-recovery/tests-all.log`.

Machine-readable results: `local-ui-recovery/vm-regressions.json`.
The two original serial capture files retain their exact CR/whitespace bytes;
Git's raw staged whitespace check flags those logs. Source/document checks
excluding only those two captures pass; the captures were not normalized to
silence warnings or change their recorded hashes.
Legacy Council accepted-input hashes were not updated. No Fable review is
claimed.

## Reproduce without downloads

For one file (repeat `--input` for others):

```sh
/Users/researcher/.platformio/penv/bin/python3 tools/uk_fw/public_rsa_probe.py \
  --container /Users/researcher/Downloads/NaU/IONIQ5_EU/HU/images/iasImage_1280_sub \
  --input /Users/researcher/Downloads/NaU/IONIQ5_EU/.lge.upgrade.xml \
  --window 16384 --output work/vm/recovery/rsa-recheck-new.json
```

The complete RSA file list and exact ranges are in `public-rsa-edges.json`.
For the updater hypotheses:

```sh
/Users/researcher/.platformio/penv/bin/python3 \
  evidence/local-ui-recovery/probe_updater_aes.py \
  --updater '/Applications/Navigation Updater.app/Contents/MacOS/Navigation Updater' \
  --inventory evidence/local-ui-recovery/package-inventory.json \
  --output work/vm/recovery/aes-recheck-new.json

/Users/researcher/.platformio/penv/bin/python3 \
  evidence/local-ui-recovery/validate_updater_hits.py \
  --updater '/Applications/Navigation Updater.app/Contents/MacOS/Navigation Updater' \
  --report work/vm/recovery/aes-recheck-new.json \
  --output work/vm/recovery/aes-validation-new.json
```

Choose fresh output names. The retained bundle's `evidence-sha256.json`
records integrity, not independent review or acceptance.

## Outcome for the real-UI goal

These experiments narrow two local recovery hypotheses; **they do not unlock
the UI**. The real GUI/rootfs/AppNavi payloads, dependencies and launcher remain
opaque or unknown. Avoid more diagnostic cosmetics or repeated generic magic
scans being presented as application recovery. Further work needs a concrete
new local format/dataflow hypothesis, followed by dependency and graphics-API
inventory if genuine vendor code is recovered.
