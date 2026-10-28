# OTA container structure: the package footer

Status: ciphertext-only structural analysis of the EU `260128` and AU `260319`
packages. No decryption, no device. Method: common-suffix/prefix detection over
the committed envelopes, entropy profiling, and manifest cross-check.

**Scope correction, 2026-10-21:** shared bytes and lengths are observations;
"footer", manifest contents, encryption boundaries and trust semantics are
hypotheses. Earlier instructions to strip this suffix were wrong. The documented
`DecryptToPIPE` invocation consumes the **whole input**. See
[`local-ui-recovery.md`](local-ui-recovery.md) for the latest bounded probes.

## Finding

Each package appends an identical, package-scoped block to exactly three files:

| Package | Footer length | SHA-256 of footer | Carriers |
|---|---|---|---|
| EU `260128` | **14,059 bytes** | `fc1c07cc891f09eaef7bf2b01404a38b3f26d7870cc0830b319d0747638a8ea9` | `AppUpgrade`, `.lge.upgrade.xml`, `update.tar.gz` |
| AU `260319` | **14,315 bytes** | `81c18efd94ba84b50dde63a6cc52eb1d5b29407958efeb090ba16c6ef298ac02` | same three |

The four large payloads (`mango-rootfs.tar.gz`, `new_gui.tar.gz`, `appnavi.tar`,
`mango-rwdata.tar.gz`) have no shared suffix in the tested comparisons. No
shared prefix was found in the inspected windows; this does **not** establish
where an IV is stored or whether IVs are reused.

Per-file split after removing the footer:

| File | EU size | EU unique | AU size | AU unique |
|---|---|---|---|---|
| `AppUpgrade` | 10,803,676 | 10,789,617 | 10,807,772 | 10,793,457 |
| `.lge.upgrade.xml` | 17,670 | **3,611** | 17,812 | **3,497** |
| `update.tar.gz` | 42,117,462 | 42,103,403 | 70,901,166 | 70,886,851 |

`.lge.upgrade.xml` is therefore almost entirely footer: only ~3.5 KB is its own
encrypted content. That is consistent with the documented behaviour — `AppSetup`
decrypts this file first, reads the version from it, and only then hands over to
`AppUpgrade`.

## Entropy profile

- shared suffix: 7.98 overall, 7.1–7.3 per 256-byte block. The lower small-sample
  estimate does **not** distinguish structure from random bytes;
- each file's unique head: 8.00;
- no gzip, zlib, DER/PKCS#7, PEM or X.509 markers anywhere in the footer;
- byte histogram is flat and no printable runs longer than 8 bytes.

Interpretation remains open. A package-scoped encrypted descriptor is one
hypothesis, but repetition and entropy do not identify its contents, encryption
scheme or verification role. Offline recovery has not been demonstrated; it has
not been proved impossible.

## Why only those three files

The three carriers are named as the upgrader binary, upgrade descriptor and
firmware archive. Whether the updater authenticates them as a group is unknown.
The `.ver` manifest records **CRC-32 and size** for individual payloads; this
does not establish which additional checks the updater performs.

## An integrity question this raises

If the footer's signature covers a descriptor that lists per-file **CRC-32**
values, then per-file integrity reduces to CRC-32, which is linear and trivially
forgeable: for any malicious body of the correct size there exists a 4-byte
tweak that restores the original CRC. That would allow a modified payload to pass
without the OEM private key.

This is a **hypothesis, not a finding**. It is consistent with three observations
but not proven by them:

1. the `.ver` manifest records size and signed CRC-32 only;
2. the kernel's signature path (`verify_oem_signature`,
   `manifest_key_verify_digest`) is a SHA-256 + asymmetric verify used for
   manifests, and it is reachable only from keystore backup/migration;
3. the large payloads carry no footer of their own.

The weaker half of the question is now **proven**: CRC-32 cannot serve as an
integrity control at all. `tools/uk_fw/crc32_forge.py` computes the 4-byte
correction that forces any chosen CRC-32 value, and the demonstration below
preserves the manifest value across a real content change.

```
original  Checksum.txt      crc=0xa09a265d
byte 20 changed              crc=0x0338bbdf
corrected at offset 8        crc=0xa09a265d   MATCH
differing bytes              [8, 9, 10, 11, 20]
```

What remains unproven is whether the upgrader relies on those CRC values, and
whether a modified payload can still be decrypted and a footer still verified.
Because the `.ver` CRC is computed over **ciphertext**, an attacker without the
key still cannot produce a payload that decrypts to anything useful. So even if
the CRC hypothesis holds, it is a **post-execution** mechanism — useful for
persistence after the `disableEncryptionUpdate` path is established, not a route
to first execution.

**Field evidence now weakens even that.** A public report
(`navi_extended` issue #3, 2023-09-23) describes exactly this attack on a
sibling unit — updating the `.ver` with the corrected CRC and file size — and the
unit still refused to install. The integrity gate is therefore stronger than the
`.ver` CRC alone. See `evidence/community-field-evidence.md`. The arithmetic
result stands; the exploitable reading does not.

It is falsified if the descriptor contains a cryptographic digest per file, or if
`AppUpgrade` re-hashes decrypted content. Deciding it requires either the
decrypted descriptor or observation on the bench.

## Tool

`tools/uk_fw/ota_structure.py`:

```
python3 tools/uk_fw/ota_structure.py --root ~/Downloads/NaU/IONIQ5_EU
python3 tools/uk_fw/ota_structure.py --root <pkg> --json out.json
```

Reports pairwise shared regions, the detected footer, its digest and entropy, and
each file's unique byte count. Reads only 64 KiB windows per file, so it is cheap
even on the 17 GB map archive.

## Consequences for the plan

- Preserve and pass the whole input to an authentic decryptor. Do not strip or
  re-append guessed fields without establishing the format.
- Cross-package transplantation and acceptance semantics are untested; the
  different suffix bytes alone cannot settle either question.
- CRC repair is an arithmetic capability, not a demonstrated update-integrity
  bypass or sufficient custom-firmware installation procedure.

## Next evidence

1. Recover the actual `.lge.upgrade.xml` format. The EU unique prefix is 3,611
   **opaque bytes**, not an established plaintext length.
2. Identify the shared suffix's content and processing before assigning it a
   descriptor schema or signature algorithm.
3. Current work is local-only; device acceptance remains unobserved.
