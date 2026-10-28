# `ipk.` boot container: format, signature scheme and bench experiment

Status: complete static characterisation of the plaintext boot container in the
EU `260128` package, verified against all six `iasImage*_sub` files. No device
was used. The re-signing capability exists to run an *acceptance experiment* on a
bench unit; it does **not** defeat OEM signature verification.

## Layout

| Offset | Size | Field | Value observed |
|---|---|---|---|
| 0x000 | 4 | magic | `ipk.` |
| 0x004 | 4 | format version | `0x00030300` |
| 0x008 | 4 | reserved | 0 |
| 0x00c | 4 | total size | `0x005ebfcc` = 6,209,484 |
| 0x010 | 4 | header size | `0x34` = 52 |
| 0x014 | 4 | duplicate of 0x00c | 6,209,484 |
| 0x018 | 4 | build/format id | `0x42f08d94` — **constant across all six variants** |
| 0x01c | 4 | command-line length | 953 |
| 0x020 | 4 | `0x005148e0` | |
| 0x024 | 4 | reserved | 0 |
| 0x028 | 4 | `0x0e36` | |
| 0x02c | 4 | `0x04f8` | |
| 0x030 | 4 | `0x000d6000` | |
| 0x034 | 953 | NUL-terminated kernel command line | |
| 0x3ed | … | payload; legacy LZ4 kernel stream begins at `0x445e` | |
| `hdr+total` | 4 | variant tag | `fd4578f5` (differs per variant) |
| +4 | 252 | `0xFF` padding | |
| +0x100 | 256 | RSA-2048 signature | |
| +0x200 | 256 | RSA-2048 modulus | |
| +0x300 | 4 | public exponent | 65537 |

Important correction to earlier notes: field `0x018` is **not** a checksum. It is
identical across all six payloads even though the command lines differ, so it
cannot be content-derived. The earlier CRC hypotheses (zlib and CRC-32/MPEG-2)
failed for that reason.

The six variants differ by only **261–274 bytes**: the command line, a byte at
`0x46`, and the trailer region (tag plus signature). The kernel payload is
otherwise identical, which means one kernel serves 1280, 1920/12 and p5 layouts.

## Signature scheme (verified)

- **RSA-2048, PKCS#1 v1.5, SHA-256.**
- Signed byte range: `[0, hdr + total + 4)` — that is, header **plus** payload
  **plus** the 4-byte variant tag. It ends exactly 768 bytes before EOF, i.e.
  before the `0xFF` padding.
- `pow(signature, 65537, modulus)` yields the expected
  `00 01 FF … FF 00 30 31 30 0d 06 09 60 86 48 01 65 03 04 02 01 05 00 04 20 ‖ digest`
  block, and the trailing digest equals SHA-256 of the signed range.

OEM modulus SHA-256: `227d89f5a3cabed4efb8e67d5a0f9fa29d03a6759b8a150503fb383698fedea6`.

## Where the key lives

The 256-byte modulus appears in **only** the six `_sub` containers. It is **not**
present in the shipped kernel image (`vmlinux`, SHA-256 `f5ee9c2f…6b102b`).

Therefore the verification decision is made by something outside the analysed
kernel:

1. the boot loader (not shipped in the package), which may compare the embedded
   modulus against a pinned value; or
2. the encrypted main `iasImage`, whose contents are unavailable; or
3. nothing else — in which case the container is self-signed and the trust is
   circular.

Case 3 cannot be confirmed or excluded offline. It is the single highest-value
question for boot-image customization, and it is answerable only on a bench unit.

## Tool

`tools/uk_fw/ipk_tool.py`:

```
info      parse every field, the command line and the trailer
verify    validate the embedded signature (read-only)
extract   write the payload and optionally the decompressed kernel
resign    write a modified container re-signed with a supplied RSA key
```

Verified behaviour:

- `verify` on the OEM image: **VERIFIED**, digest matches.
- `resign` with a generated 2048-bit test key and `init=/bin/sh`, followed by
  `verify` on the result: **VERIFIED** under the new modulus.
- The OEM image still verifies afterwards; inputs are never modified.

## The bench experiment this enables

The question is not "can a container be forged" — it can, trivially. The question
is **what the boot loader accepts**. On a bench unit, with a full pre-write dump
of the boot partitions:

1. Confirm the stock image boots and capture the boot log on `ttyS2`.
2. Write a container that differs only in a harmless way (e.g. a comment in the
   command line) and is re-signed with a **new** key.
3. Observe: does the loader reject it (pinned key), accept it silently (embedded
   key trusted — critical finding), or fail with a specific error?
4. If rejected, repeat with the OEM signature intact but the payload altered, to
   determine whether the signature covers the payload or only the header.

Step 2 is the decisive test and it requires physical access. Nothing in the
package can answer it.

## What this changes for custom firmware

- The boot image is authenticated with a real, correctly formed RSA-2048
  signature. A modified image will be rejected by any verifier that pins the OEM
  key.
- Conversely, if the loader trusts the embedded modulus, boot-image substitution
  is possible without the OEM private key.
- Either way, the **userland** update path (CVE-2023-26244/26245/26246) remains
  the documented route, because it targets exactly the components that check
  package authenticity before any boot image is written.

## Safety

`resign` produces a test artifact. Writing any modified boot image to a unit
without a verified restore path is unrecoverable if the loader rejects it in a
way that leaves the boot partitions inconsistent. Take the full dump first.

## Addendum: the encrypted wrapper (`iasImage` without `_sub`)

The six plaintext `*_sub` containers are the analysable form. The matching
`iasImage` files are the **encrypted** form used by the loader:

- all six `iasImage` variants are the same size, 6,226,728 bytes, 16,420 bytes
  larger than the `_sub` payload;
- five of the six share an identical **13,035-byte trailer**
  (SHA-256 `41885928b3823d0b4b57094b2a355cbe6ff639cfb099a0480aa1f619f90dd770`,
  entropy 7.976), while `iasImage_p5_1920_12` has a completely different tail;
- the trailer is **package-scoped**: EU and AU `iasImage` share no suffix;
- unlike `_sub`, the encrypted images contain no plaintext `01 00 01 00`
  exponent marker, so the RSA key block is inside the encrypted region.

This mirrors the OTA footer pattern and supports one packing model: each
protected artifact is *encrypted content plus a package-level descriptor*, with
the descriptor produced once per package and appended verbatim. The
`p5_1920_12` anomaly is most likely a stale or separately built artifact in the
package rather than a different scheme.

### Exact three-part decomposition

The sizes close arithmetically for every variant:

```
6,226,728  =  3,385  +  6,210,308  +  13,035
             header      payload      trailer
```

The payload length is **exactly** the size of the corresponding plaintext
`_sub` container, so the encrypted image is a wrapper of the same boot payload.
All three regions are high-entropy:

- the header is **variant-specific** (the six variants share no common prefix)
  and has no plaintext fields — no size, build-id or magic appears in it, and a
  search for the known constants (6,210,308; 3,385; 13,035; 52; 953; `0x42f08d94`)
  as little-endian words finds nothing;
- the trailer is **identical across five variants** and package-scoped.

So the header is encrypted, variant-scoped metadata and the trailer is an
encrypted, package-scoped descriptor. Neither is parseable offline.

### The wrapper is not handled by Linux

The kernel contains **no** IAS-related symbol, string or config option (`ias`,
`iasImage`, `image_auth`, `sub_image` all return nothing in `kallsyms.tsv`,
`vmlinux` strings and `kernel.config`). The `ipk.`/`iasImage` format is therefore
a **boot loader** concern: verification and unwrapping happen before Linux runs.

The consequence is firm: reverse engineering the boot-image format requires the
boot loader, which lives in SPI NOR and is not published. That path is closed
without a hardware dump; the OTA/update path remains the open one.

